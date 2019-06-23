from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http.request import HttpRequest
from .models import Fossil
import xlrd
from datetime import datetime
import pytz
import re
from paleocore110.settings import PROJECT_ROOT
from sys import path
import collections
import idigbio
import requests

#FOLDER_PATH = '/Users/dnr266/Documents/PaleoCore/projects/Laetoli/csho_versions/'
FOLDER_PATH = PROJECT_ROOT + '/laetoli/fixtures/'
YEARS = [1998, 1999, 2000, 2001, 2003, 2004, 2005, 2012, 2014, 2016]
CSHO_YEARS = YEARS[0:7]  # 1998-2005
file_name = 'laetoli_csho_1998'
verbose_default = False
SPLITS = ['EP 1280/01', 'EP 3129/00', 'EP 1181/00', 'EP 3635/00']


# Functions for opening Excel files and reading headers
def make_file_string(year):
    """
    Create a file name string from the year, e.g. 'laetoli_csho_1998.xls'
    :param year: four digit integer value
    :return: string representation of file name
    """
    return 'laetoli_csho_'+str(year)+'.xls'


def delete_all():
    """
    Delete all Fossil objects.
    :return:
    """
    for s in Fossil.objects.all():
        s.delete()


def open_book(folder, file):
    """
    Open an Excel workbook
    :param folder: string representing folder path with starting and ending slashes,
    e.g. '/Users/dnr266/Documents/PaleoCore/projects/Laetoli/csho_versions/'
    :param file: string representation of the file name, with no slashes, e.g. 'laetoli_csho_1998.xls'
    :return: Returns an xlrd workbook object
    """
    return xlrd.open_workbook(folder+file)


def get_max_sheet(book):
    """
    Get the sheet in the workbook with the most rows of data
    :param book: An xlrd book object
    :return: Returns an xlrd sheet object
    """
    row_counts = [s.nrows for s in book.sheets()]  # list of row counts for each sheet
    max_sheet_index = row_counts.index(max(row_counts))  # find list index for largest sheet
    sheet = book.sheet_by_index(max_sheet_index)  # return the sheet with the greatest number of rows
    return sheet


def get_header_cells(sheet):
    return sheet.row(0)


def get_header_list(sheet):
    return [c.value for c in sheet.row(0)]


lookup_dict = {
    'Specimen Number': 'verbatim_specimen_number',
    'Specimen number': 'verbatim_specimen_number',
    'Date Discovered': 'verbatim_date_discovered',
    'Date discovered': 'verbatim_date_discovered',
    'Storage': 'verbatim_storage',
    'tray': 'verbatim_tray',
    'Tray': 'verbatim_tray',
    'Locality': 'verbatim_locality',
    'Horizon': 'verbatim_horizon',
    'Column22': 'verbatim_horizon',
    'Element': 'verbatim_element',
    'Kingdom:': 'verbatim_kingdom',
    'Kingdom': 'verbatim_kingdom',
    'Phylum': 'verbatim_phylum_subphylum',
    'Phylum/Subphylum:': 'verbatim_phylum_subphylum',
    'Phylum/Subphylum': 'verbatim_phylum_subphylum',
    'Class:': 'verbatim_class',
    'Class': 'verbatim_class',
    'Order:': 'verbatim_order',
    'Order': 'verbatim_order',
    'Family': 'verbatim_family',
    'Tribe': 'verbatim_tribe',
    'Tribe:': 'verbatim_tribe',
    'Genus': 'verbatim_genus',
    'Species': 'verbatim_species',
    'Species:': 'verbatim_species',
    'other': 'verbatim_other',
    'Other': 'verbatim_other',
    'Other:': 'verbatim_other',
    'Comments': 'verbatim_comments',
    'Comment': 'verbatim_comments',
    'Published': 'verbatim_published',
    'published': 'verbatim_published',
    'Problems': 'verbatim_problems',
    'Breakage': 'verbatim_breakage',
    'Weathering': 'verbatim_weathering',
    'Animal Damage': 'verbatim_animal_damage',
    'Animal damage': 'verbatim_animal_damage',
    'NonAnimal Damage': 'verbatim_nonanimal_damage',
    'Nonanimal Damage': 'verbatim_nonanimal_damage',
    'Nonanimal damage': 'verbatim_nonanimal_damage',
}


def validate_header_list(header_list):
    """
    Check that the elements of the header list are present in the lookup dictionary
    :param header_list:
    :return: 1 if all header elements in lookup dict, 0 otherwise
    """
    result = 1
    for i in header_list:
        if lookup_dict[i]:
            pass
        else:
            result = 0
    return result


def validate_all_headers(file_years=YEARS):
    files = [make_file_string(y) for y in file_years]
    for file in files:
        book = open_book(file=FOLDER_PATH+file)
        sheet = book.sheet_by_index(0)
        header = get_header_list(sheet)
        if validate_header_list(header):
            print("Header for {} is valid".format(file))
        else:
            print("Header for {} is NOT valid".format(file))


# Functions for processing data in Excel Files
def convert_date(date_cell, date_mode):
    date_value = None
    if date_cell.ctype == 1:  # unicode string
        try:
            date_format = '%d/%m/%y'
            date_value = datetime.strptime(date_cell.value, date_format)
        except ValueError:
            date_format = '%d/%m/%Y'
            date_value = datetime.strptime(date_cell.value, date_format)
    elif date_cell.ctype == 3:
        date_value = xlrd.xldate_as_datetime(date_cell.value, date_mode)
    return date_value


def make_row_dict(book, header_list, row_data_cell_list):
    """
    Assumes header row is valid
    :param book: an excel workbook object
    :param header_list: a list of column headings
    :param row_data_cell_list: a list of xl cell data
    :return: returns a dictionary with Fossil model keys and excel row data as values
    """
    cells_dict = dict(zip(header_list, row_data_cell_list))  # dictionary of cell values
    try:
        date_discovered = convert_date(cells_dict['Date Discovered'], book.datemode)  # convert xl dates to datetime
    except KeyError:  # check for alternate capitalization
        date_discovered = convert_date(cells_dict['Date discovered'], book.datemode)  # convert xl dates to datetime
    row_cells_list = list(cells_dict.items())  # list of tuples of dict items
    # use list comprehension to generate tuples of dict items replacing cell instances with cell values
    row_values_list = [(i[0], i[1].value) for i in row_cells_list]
    row_values_dict = dict(row_values_list)  # convert the list back to a dict
    try:
        row_values_dict['Date Discovered'] = date_discovered  # replace cell values (text or float) with datetime
    except KeyError:
        row_values_dict['Date discovered'] = date_discovered  # replace cell values (text or float) with datetime
    occurrence_item_list = [(lookup_dict[i[0]], i[1]) for i in row_values_dict.items()]
    item_dict = dict(occurrence_item_list)
    if item_dict['verbatim_specimen_number']:
        item_dict['catalog_number'] = item_dict['verbatim_specimen_number']
    else:
        item_dict = None  # no verbatim specimen number signals empty row.
    return item_dict


def import_sheet(year, file, book, header, sheet, header_row=True, verbose=verbose_default):
    """
    Import data from an Excel spreadsheet. Skips empty rows.
    :param year: Integer value for the woorkbook year.
    :param file: String value containing file name without leading or trailing slashes.
    :param book: An Excel workbook object
    :param header: A list of column header names
    :param sheet: An Excel spreadsheet object
    :param header_row: header row present or not
    :param verbose: verbose output desired
    :return: returns an integer row count and an integer created count. If all goes well the two should match.
    """
    created_count = 0
    starting_row = 1
    row_count = 0
    if not header_row:
        starting_row = 0
    for row in range(starting_row, sheet.nrows):
        if verbose:
            print("processing row {}".format(row_count))
        row_dict = make_row_dict(book, header, sheet.row(row))
        if row_dict:
            row_dict['verbatim_workbook_name'] = file
            row_dict['verbatim_workbook_year'] = year
            # specimen_number = row_dict['verbatim_specimen_number']
            Fossil.objects.create(**row_dict)
            created_count += 1
            row_count += 1
        else:  # if empty row
            row_count += 1
            print('skipping blank row {}'.format(row_count))
    return row_count, created_count


def import_file(folder, file, year, verbose=verbose_default):
    """
    Procedure to import data from an Excel workbook
    :param folder: Directory path to workbook as string and with trailing slash, e.g. '/laetoli/fixtures/'
    :param file: File name of workbook including extension, e.g. 'csho_laetoli_1998.xls'
    :param year: Year of data being imported as integer, e.g. 1998
    :param verbose: True/False for more verbose output
    :return:
    """
    print("\nImporting data from {}".format(file))  # Indicate function has started
    book = open_book(folder, file)  # open the excel workbook
    sheet = get_max_sheet(book)  # get the sheet from the workbook
    header = get_header_list(sheet)  # get the header as a list
    if validate_header_list(header):  # validate the header, make sure all columns are in lookup dictionary
        rc, cc = import_sheet(year, file, book, header, sheet, verbose=verbose)  # import data from the sheet
        print("Processed {rc} rows and created {cc} new Fossil objects.".format(rc=rc, cc=cc))
    else:
        print('Invalid Header List')


# Function to delete duplicate and incorrect records
def delete_records():
    """
    Procedure to delete duplicate and erroneous records.
    :return: Returns an integer count of the number of records deleted.
    """
    count = 0
    # Seven specimens are clones. Delete one of each
    # clones = ['EP 1582b/00', EP 1144/04', 'EP 1173/04', 'EP 1400/04', 'EP 1403/04', 'EP 1542/04', 'EP 515/05']
    # 1. Fix EP 1582b/00. Keep the item with the more complete description.
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 1582B/00', verbatim_element='Dist. M/Podial')
    fossil.delete()
    count += 1

    # 2 - 7.  Fix 6 cloned entries, delete one copy.
    for cn in ['EP 1144/04', 'EP 1173/04', 'EP 1400/04', 'EP 1403/04', 'EP 1542/04', '515/05']:
        fossils = Fossil.objects.filter(verbatim_specimen_number=cn)
        if len(fossils) == 2:
            delete_me = fossils[0]
            delete_me.delete()
            count += 1

    # 8. One item is modern, not fossil.
    specimen = Fossil.objects.get(verbatim_specimen_number='EP 1905/00')
    specimen.delete()
    count += 1

    # 9. Fix EP 1052/98. The Aves specimen is an inccorrect entry and is deleted.
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 1052/98', verbatim_class='Aves')
    fossil.delete()
    count += 1

    # 10. Fix EP 001/98 Delete the crocodile entry
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 001/98', verbatim_family='Crocodylidae')
    fossil.delete()
    count += 1

    # 11. EP 1477b/00 Delete the suid entry.
    fossil = Fossil.objects.get(verbatim_specimen_number='EP 1477B/00', verbatim_order='Artiodactyla')
    fossil.delete()
    count += 1

    return count


# Function to split bulk records
def split_records():
    """
    Procedure that splits records into parts. Needed for some bulk items where more than one taxa is
    included in a single item. In these cases taxa appear as a comma separated list in the verbatim taxon
    field, (e.g. tgenus = 'Achatina, Burtoa').
    This procedure splits the single record into to parts, e.g. EP 1280/01 becomes EP 1280a/01 and EP 1280b/01
    The taxon information for each new part is then updated.
    :return:
    """
    count = 0
    # Split 4 bulk samples that contain multiple taxa.
    splits = SPLITS
    for catno in splits:
        if Fossil.objects.filter(verbatim_specimen_number=catno):
            print("Splitting {}".format(catno))
            split2part(Fossil.objects.get(verbatim_specimen_number=catno))
            count += 1
    return count


# Functions for processing and validating data by field
def update_idq(rts):
    """
    Function to update the identification qualifier field when appropriate.
    This function searches a taxonomic string for Open Nomenclature abbreviations (e.g. cf. aff. sp. indet.)
    If found the string is excised from the taxon field and added to the identification qualifier field
    Darwin Core stipulates that all notations about taxonomic uncertaintly are limited to the
    identificationQualifier field.
    :param rts: The raw taxanomic string, e.g. 'cf. major'
    :return: returns the cleaned taxon string and the identification qualifier string
    """
    idq = None
    ts = rts.strip()
    # regex matches all of the following:
    # test_list = ['? major', '?major', 'aff. major', 'Nov. sp.', 'indet', 'Indet.', 'cf.', 'Cf', 'cf. major', 'sp.',
    #             'Sp.', 'sp', 'Sp', ' sp.', 'major sp. nov.', 'sp. A', 'sp. A, sp. B', 'major']
    idqre = re.compile(r'[sS]p[.]?.*|[cC]f[.]?|[iI]ndet[.]?|Nov[.]?.*|[Aa]ff[.]?|[?]')
    if ts:
        if idqre.search(ts):
            idq = ts
            ts = idqre.sub('', ts)
    return ts, idq


def test_idq():
    test_list = ['? major', '?major', 'aff. major', 'Nov. sp.', 'indet', 'Indet.', 'cf.', 'Cf', 'cf. major', 'sp.', 'Sp.', 'sp', 'Sp', ' sp.', 'major sp. nov.', 'sp. A', 'sp. A, sp. B', 'major']
    for t in test_list:
        t, i = update_idq(t)
        print(str(t)+' |  '+str(i))
    print("============")
    # for s in [t[0] for t in field_list('verbatim_species', report=False)]:
    #     idq(s)


def update_date_recorded():
    """
    date_recorded = verbatim_date_discovered
    Function to copy dates to date_recorded field and add timezone info.
    :return:
    """
    print("Updating date_recorded from verbatim_date_discovered")
    tz = pytz.timezone('Africa/Dar_es_Salaam')
    for s in Fossil.objects.all():
        if s.verbatim_date_discovered:
            s.date_recorded = datetime.combine(s.verbatim_date_discovered, datetime.min.time(), tzinfo=tz)
            s.save()
        else:
            s.date_recorded = None


def validate_date_recorded():
    """

    :return:
    """
    print("Validating date_recorded")
    result = 1
    for fossil in Fossil.objects.all():
        if fossil.date_recorded:
            if not 1998 <= fossil.date_recorded.year <= 2005:
                print("Fossil is outside date range 1998-2005.")
                result = 0
        else:
            print("Fossil missing date_recorded")
            result = 0
    return result


def update_catalog_number():
    """
    catalog_number = verbatim_specimen_number
    fix 3 catalog numbers with format errors or incorrect year suffixes
    remove 7 duplicate (cloned) records
    fix 6 unique entries that have duplicate catalog numbers from digitizing errors
    :return: 
    """
    print("Updating catalog_number from verbatim_specimen_number.")
    ep_re = re.compile(r'EP ')
    cat_re = re.compile(r'EP \d{3,4}[a-zA-Z]{0,1}/[089][01234589][a-zA-Z]$')
    cap = re.compile(r'EP \d{3,4}[A-Z]/[089][01234589]$')
    missing_slash = re.compile(r'EP \d{3,4}[a-zA-Z]{0,1}[089][01234589]$')
    extra_year = re.compile(r'EP \d{3,4}[a-zA-Z]{0,1}/[089][01234589][9]$')
    period = re.compile(r'EP \d{3,4}[a-zA-Z]{0,1}/[089][01234589][.]$')
    colon = re.compile(r'EP \d{3,4}[a-zA-Z]{0,1}:/[089][01234589]$')
    # update catalog number for all records EXCEPT the splits
    for fossil in Fossil.objects.exclude(verbatim_specimen_number__in=SPLITS):
        # Initial write of verbatim catalog number to catalog number
        # Fix missing EP prefix in 2005 records at the same time.
        if not ep_re.match(fossil.verbatim_specimen_number):  # 2005 catalog numbers missing EP prefix
            fossil.catalog_number = 'EP '+fossil.verbatim_specimen_number
        else:
            fossil.catalog_number = fossil.verbatim_specimen_number
        fossil.save()

        # Fix catalog numbers with trailing letters e.g. EP 001/98A to EP 001a/98
        if cat_re.match(fossil.catalog_number):
            part = fossil.catalog_number[-1:]  # A
            base = fossil.catalog_number[:-1]  # EP 001/98
            slash = base.index('/')
            fossil.catalog_number = base[:slash] + part.lower() + base[slash:]  # 'EP 001' + 'a' + '/98'

        # Fix cat numbers with cap part letters e.g. EP 001A/98 to EP 001a/98
        if cap.match(fossil.catalog_number):
            cn = fossil.catalog_number  # 'EP EP 001A/98'
            ci = cn.index('/')
            pre = cn[:ci-1]  # EP 001
            part = cn[ci-1:ci]  # A
            post = cn[ci:]  # /98
            cn = pre + part.lower() + post  # 'EP 001' + 'a' + '/98'
            fossil.catalog_number = cn

        # Fix cat numbers missing slash, e.g. EP 284100
        if missing_slash.match(fossil.catalog_number):
            cn = fossil.catalog_number  # 'EP 284100'
            cn = cn[:-2] + '/' + cn[-2:]  # 'EP 2841' + '/' + '00'
            fossil.catalog_number = cn

        # Fix cat numbers with extra 9 in year, e.g. EP 265/999
        if extra_year.match(fossil.catalog_number):
            fossil.catalog_number = fossil.catalog_number[:-1]  # EP 265/99

        # Fix cat numbers with trailing periods  e.g. EP 001/98.
        if period.match(fossil.catalog_number):
            fossil.catalog_number = fossil.catalog_number[:-1]

        # Fix cat numbers with colons
        if colon.match(fossil.catalog_number):
            cn = fossil.catalog_number  # 'EP 525:/05'
            ci = cn.index(':')
            cn = cn[:ci] + cn[ci+1:]  # 'EP 525' + '/05'
            fossil.catalog_number = cn
        fossil.save()

    # Fix 3 Format Errors
    # Three specimens have badly formed catalog numbers.
    # format_errors = ['EP 120A+B/98', 'EP 507/07', 'EP 756/06']
    # 1. Fix EP 120A+B/98
    ep120 = Fossil.objects.get(verbatim_specimen_number='EP 120A+B/98')
    ep120.catalog_number = 'EP 120/98'
    if ep120.remarks:
        ep120.remarks += ' Catalog number changed from EP 120A+B/98'
    else:
        ep120.remarks = 'Catalog number changed from EP 120A+B/98'
    ep120.save()

    # 2. Fix EP 507/07
    fossil = Fossil.objects.get(catalog_number='EP 507/07')
    fossil.catalog_number = 'EP 507/05'
    fossil.save()

    # 3. Fix EP 756/06
    fossil = Fossil.objects.get(catalog_number='EP 756/06')
    fossil.catalog_number = 'EP 756/05'
    fossil.save()

    # Fix 6 duplicate catalog number entries.
    # Fix two pairs of duplicate entries that reflect emended taxonomic identifications of the same specimen.
    # emended_specimens = ['EP 001/98', 'EP 1477b/00']
    # EP 001/98 was emended from crocodile to rhino
    # EP 1477b/00 was emended from suid to felid

    # 1. Fix EP 0001/98, update comments to the rhino entry.
    fossil = Fossil.objects.get(catalog_number='EP 001/98', verbatim_family='Rhinocerotidae')
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from Animalia:Vertebrata:Reptilia:Crocodilia:Crocodylidae'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from Animalia:Vertebrata:Reptilia:Crocodilia:Crocodylidae'
        fossil.save()

    # 2. Fix EP 1477b/00 and also related specimen EP 1477a/00
    # Update comments to the the felid entry.
    fossil = Fossil.objects.get(catalog_number='EP 1477b/00', verbatim_order='Carnivora')
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from Animalia:Vertebrata:Mammalia:Artiodactyla:cf. Suidae'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from Animalia:Vertebrata:Mammalia:Artiodactyla:cf. Suidae'
        fossil.save()
    # Also emend the taxonomic information for related record EP 1477a/00
    fossil = Fossil.objects.get(catalog_number='EP 1477a/00')
    fossil.torder='Carnivora'
    fossil.tfamily='Felidae'
    fossil.tsubfamily = None
    fossil.tgenus = None
    fossil.ttribe = None
    fossil.trivial = None
    fossil.scientific_name = 'Animalia:Vertebrata:Mammalia:Carnivora:Felidae'
    fossil.save()
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from ' \
                                'Animalia:Vertebrata:Mammalia:Artiodactyla:Suidae:Kolpochoerus'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from ' \
                               'Animalia:Vertebrata:Mammalia:Artiodactyla:Suidae:Kolpochoerus'
        fossil.save()

    # We are still left with 3 duplicates resulting from typos during digitization.
    # duplicates = ['EP 1052/98', 'EP 1075/03', 'EP 348/04', 'EP 2188/99']
    # These items need to be fixed individually.
    
    # 1. Fix EP 1075/03. The Serengetilabus specimen has a typo in the catalog number. Should be EP 1975/03
    fossil = Fossil.objects.get(catalog_number='EP 1075/03', verbatim_genus='Serengetilagus')
    fossil.catalog_number = 'EP 1975/03'
    fossil.save()

    # 2. Fix EP 348/04. The distal radius specimen has a typo in the catalog number and incorrect date. It should
    # read EP 349/04 and the date should be 29 June 2004
    fossil = Fossil.objects.get(catalog_number='EP 348/04', verbatim_element='Distal radius')
    fossil.catalog_number = 'EP 349/04'
    tz = pytz.timezone('Africa/Dar_es_Salaam')
    fossil.date_recorded = datetime(year=2004, month=6, day=29, tzinfo=tz)
    fossil.save()

    # 3. Fix EP 2188/99, the Bovidae distal humerus is a typo and should be EP 2188/03
    fossil = Fossil.objects.get(catalog_number='EP 2188/99', verbatim_element='distal humerus')
    fossil.catalog_number = 'EP 2188/03'
    fossil.save()

    fossil = Fossil.objects.get(catalog_number='EP 2188/99', verbatim_element='Lumbar Vertebral Centrum')
    fossil.catalog_number = 'EP 2188/00'
    fossil.save()


def validate_catalog_number():
    print("Validating catalog_number.")
    # regular expression to test proper format of catalog numbers
    cat_re = re.compile(r'EP \d{3,4}[a-zA-Z]?/[09][01234589]$')
    # list of catalog_number column in db
    catalog_list = list(Fossil.objects.values_list('catalog_number', flat=True))
    # Test catalog numbers against re
    re_errors_list = [item for item in catalog_list if not cat_re.match(item)]
    duplicate_list = [item for item, count in collections.Counter(catalog_list).items() if count > 1]

    # Pretty print format errors
    print("\nFormat Errors\n---------------------")
    if re_errors_list:
        for f in re_errors_list:
            print("Format error in catalog number {}".format(f))
    else:
        print("No formatting errors found.")

    # Pretty print duplicates
    print("\nDuplicate Summary\n---------------------")
    if duplicate_list:
        for duplicate_catalog_number in duplicate_list:
            print("Duplicate catalog number {}".format(duplicate_catalog_number))
            duplicate_qs = Fossil.objects.filter(catalog_number=duplicate_catalog_number)
            for d in duplicate_qs:
                print('id:{}  loc:{}  desc:{}  taxon:{}'.format(d.id, d.locality_name, d.description, d.scientific_name))
    else:
        print("No duplicates found.")


def update_institution():
    """
    Copy data from verbatim_storage into disposition
    :return:
    """
    print("Updating disposition from verbatim_storage")
    for fossil in Fossil.objects.all():
        fossil.disposition = fossil.verbatim_storage
        fossil.save()


def update_locality():
    print("Updating Locality")

    # Define dictionary of replacement values to be used in multi-replace function
    rep = {
        '1NW': '1 Northwest',
        '2 (NW)': '2 Northwest',
        '2 (?West)': '2 ?West',
        '2 (West)': '2 West',
        '(S)': 'South',
        '(South)': 'South',
        '22S': '22 South',
        '7E': '7 East',
        '7 E': '7 East',
        '9S': '9 South',
        '9 S': '9 South',
        '10 E': '10 East',
        '10E': '10 East',
        '10 W': '10 West',
        '10W': '10 West',
        '10 Ne': '10 Northeast',
        '12 E': '12 East',
        '12E': '12 East',
        '13 E': '13',
        '13E': '13',
        '13/14': '13',
        '21E': '21 East',
        '22E': '22 East',
        '22 E': '22 East',
        '(Nenguruk Hill)': 'Nenguruk Hill',
        'Gulley': 'Gully',
        'Lobeleita': 'Lobileita',
        'Olesuisu': 'Oleisusu',
        'Laetolil': 'Laetoli',
        'snake gully': 'Snake Gully',
        '#': '',
        '.': '',
        ',': ' ',
    }

    # Compile regular expressions outside loop
    loc = re.compile(r'^Loc[.]* \d{1,2}\w*')  # All cases beginning with 'Loc
    l9s = re.compile(r'^Laetoli Loc.[\s]*9[\s]*')
    l22s = re.compile(r'22 S[\s]*$')
    esere = re.compile(r'^Esere$')
    garusi = re.compile(r'Garusi R  Sw Of Norsigidok$')
    l18 = re.compile(r'18.*')
    l2 = re.compile(r'[\s]2[\s].*')
    noiti = re.compile(r'^Noiti$')

    # iterate through all records
    for f in Fossil.objects.all():
        ln = f.verbatim_locality     
        if loc.match(ln):
            ln = ln.replace('Loc', 'Laetoli')  # If entry begins with Loc.

        ln = multireplace(ln, rep)

        ln = ln.replace('Loc', '')  # remove any remaining Loc
        ln = ln.replace(' Upper Laetoli Beds between Tuffs 5 +7', '')
        ln = ln.replace('Laetoli 95', 'Laetoli 9 South')
        ln = l22s.sub('22 South', ln)
        ln = esere.sub('Esere 1', ln)
        ln = garusi.sub('Garusi Southwest', ln)
        ln = l18.sub('18', ln)
        ln = l2.sub(' 2 ', ln)
        ln = noiti.sub('Noiti 1', ln)
        ln = ln.replace('   ', ' ')  # remove triple spaces
        ln = ln.strip().replace('  ', ' ')  # remove all extraneous whitespaces
        ln = ln.replace('Gully 05 km north of 5', 'Laetoli 5')

        # Convert all versions of blank to None
        if ln in ['', ' ', None]:
            ln = None

        # Assign and save
        f.locality_name = ln
        if f.verbatim_horizon == 'South Below Tuff 2' and l9s.match(f.verbatim_locality):
            f.locality_name = 'Laetoli 9 South'
        f.save()

    # Fix three specimens that have incorrect geological context and locality info
    # ['EP 900/98', 'EP 901/98', 'EP 902/98']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 900/98', 'EP 901/98', 'EP 902/98'])
    if fossils.count() == 3:  # should have three matches
        fossils.update(locality_name='Laetoli 9 South')  # update does not require save

    # Fix two specimens that are missing locality information.
    # ['EP 1308/04', 'EP 1309/04']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 1308/04', 'EP 1309/04'])
    if fossils.count() == 2:
        fossils.update(locality_name='Laetoli 6')


def validate_locality(verbose=False):
    """
    Validate locality entries against locality vocabulary.
    :return:
    """
    print("Validating localities")
    locality_list = field_list('locality_name')
    i = 1
    for loc in locality_list:
        locality_set = set([l.verbatim_locality for l in Fossil.objects.filter(locality_name=loc[0])])
        locality_string = str(locality_set)[1:-1].replace("', ", "'; ")
        area_set = set([l.area_name for l in Fossil.objects.filter(locality_name=loc[0])])
        area_string = '; '.join(area_set)
        if verbose:
            print("{}\t{}\t{}\t{}\t{}".format(i, loc[0], loc[1], area_string, locality_string))
        i += 1


def update_area():
    """
    Assumes upldate locality
    :return:
    """
    emboremony = re.compile('Emboremony')
    engesha = re.compile('Engesha')
    esere = re.compile('Esere')
    kakesio = re.compile('Kakesio')
    garusi = re.compile('Garusi')
    lobileita = re.compile('Lobileita')
    ndoroto = re.compile('Ndoroto')
    noiti = re.compile('Noiti')
    olaltanaudo = re.compile('Olaltanaudo')
    oleisusu = re.compile('Oleisusu')

    for f in Fossil.objects.all():
        if emboremony.search(f.locality_name):
            f.area_name = 'Kakesio'
        elif engesha.search(f.locality_name):
            f.area_name = 'Esere-Noiti'
        elif esere.search(f.locality_name):
            f.area_name = 'Esere-Noiti'
        elif garusi.search(f.locality_name):
            f.area_name = 'Laetoli'
        elif kakesio.search(f.locality_name):
            f.area_name = 'Kakesio'
        elif lobileita.search(f.locality_name):
            f.area_name = 'Kakesio'
        elif garusi.search(f.locality_name):
            f.area_name = 'Laetoli'
        elif noiti.search(f.locality_name):
            f.area_name = 'Esere-Noiti'
        elif olaltanaudo.search(f.locality_name):
            f.area_name = 'Olaltanaudo'
        elif ndoroto.search(f.locality_name):
            f.area_name = 'Ndoroto'
        elif oleisusu.search(f.locality_name):
            f.area_name = 'Oleisusu'
        else:
            f.area_name = 'Laetoli'
        f.save()


def validate_area():
    kakesio_list = ['Kakesio 1', 'Kakesio 2', 'Kakesio 3', 'Kakesio 4', 'Kakesio 5', 'Kakesio 6', 'Kakesio 7',
                    'Kakesio 8', 'Kakesio 9', 'Kakesio 10', 'Kakesio 1-6', 'Kakesio South', 'Kakesio 2-4',
                    'Lobileita', 'Emboremony 1', 'Emboremony 2', 'Emboremony 3']

    esere_list = ['Engesha', 'Esere 1', 'Esere 2', 'Esere 3', 'Noiti 1', 'Noiti 3']
    laetoli_list = ['Laetoli 1',
                    'Laetoli 1 Northwest',
                    'Laetoli 10',
                    'Laetoli 10 East',
                    'Laetoli 10 Northeast',
                    'Laetoli 10 West',
                    'Laetoli 11',
                    'Laetoli 12',
                    'Laetoli 12 East',
                    'Laetoli 13',
                    'Laetoli 13 "Snake Gully"',
                    'Laetoli 14',
                    'Laetoli 15',
                    'Laetoli 16',
                    'Laetoli 17',
                    'Laetoli 18',
                    'Laetoli 19',
                    'Laetoli 2',
                    'Laetoli 20',
                    'Laetoli 21',
                    'Laetoli 21 And 21 East',
                    'Laetoli 22',
                    'Laetoli 22 East',
                    'Laetoli 22 South',
                    'Laetoli 22 South Nenguruk Hill',
                    'Laetoli 23',
                    'Laetoli 24',
                    'Laetoli 3',
                    'Laetoli 4',
                    'Laetoli 5',
                    'Laetoli 6',
                    'Laetoli 7',
                    'Laetoli 7 East',
                    'Laetoli 8',
                    'Laetoli 9',
                    'Laetoli 9 South', 'Olaitole River Gully', 'Silal Artum', 'Garusi Southwest']
    oleisusu_list = ['Oleisusu']
    olaltanaudo_list = ['Olaltanaudo']
    ndoroto_list = ['Ndoroto']

    for f in Fossil.objects.all():
        if f.area_name == 'Kakesio' and f.locality_name not in kakesio_list:
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Esere-Noiti' and f.locality_name not in esere_list:
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Laetoli' and f.locality_name not in laetoli_list:
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Oleisusu' and f.locality_name != 'Oleisusu':
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Olaltanaudo' and f.locality_name != 'Olaltanaudo':
            print('Area missmatch for {}'.format(f.catalog_number))
        elif f.area_name == 'Ndoroto' and f.locality_name != 'Ndoroto':
            print('Area missmatch for {}'.format(f.catalog_number))


def update_geological_context():
    """
    Clean up and consolidate entries in the Horizon field and copy to geological_context_name
    :return:
    """
    print("Updating Geological Context")

    # Define dictionary of replacement values to be used in multi-replace function
    rep = {
        'And': '-',
        'and': '-',
        '+': '-',
        '&': '-',
        '? ': '?',
        'T1 - T2': 'Tuffs 1 - 2',
        'T2 - T3': 'Tuffs 2 - 3',
        'T3 - T5': 'Tuffs 3 - 5',
        'T4 - T5': 'Tuffs 4 - 5',
        'T5 - T6': 'Tuffs 5 - 6',
        'T5 - T7': 'Tuffs 5 - 7',
        'T6 - T7': 'Tuffs 6 - 7',
        'T6 - T8': 'Tuffs 6 - 8',
        'T7 - T8': 'Tuffs 7 - 8',
        'Below T2': 'Below Tuff 2',
        'Below T3': 'Below Tuff 3',
        'Above T7': 'Above Tuff 7',
        '5-7': '5 - 7',
        '6-7': '6 - 7',
        '5 -7': '5 - 7',
        'Btw': 'Between',
        'Ymt': 'Yellow Marker Tuff',
        'Laeotolil': 'Laetolil',
        'Laetoli ': 'Laetolil ',
    }

    # Compile regular expressions outside loop
    lb_re = re.compile(r'^Upper Laetoli[l]*.*(Be.*)')  # All cases beginning with 'Upper Laetoli' or 'Upper Laetolil'
    bt_re = re.compile(r'^Below Tuff.*|^Between Tuff.*')  # All cases beginning w/ 'Below Tuff' or 'Between Tuff'
    ub_re = re.compile(r'^Upper Beds (Between Tuff[s]* [\d] - .*)')  # Upper Beds Betwee ...
    so_re = re.compile(r'^South Below Tuff 2')  # All cases beginning with 'South Below Tuff 2'
    tf_re = re.compile(r'.*Tuffs 6 - [\d]{2, 2}$')  # Auto increment error
    ab_re = re.compile(r'^Above Tuff 8$')  # All cases beginning with 'Above Tuff 8'
    ue_re = re.compile(r'^[?]Upper Ndolanya$')  # All cases beginning with '? Upper Ndolanya'

    # Define a standard prefix string for Laetoli Upper Beds
    prefix = 'Laetolil Beds, Upper Unit, '

    # Iterate through all records and update
    for f in Fossil.objects.all():
        gcn = f.verbatim_horizon.title()  # Make all cases consistent

        # Standardize symbols and expand abbreviations
        gcn = multireplace(gcn, rep)  # Fix abbreviations
        gcn = multireplace(gcn, rep)  # Need to run 2x to catch changes from first round

        # Substitute matching strings with groups, group 0 is whole string, group 1 is partial string in parentheses
        gcn = re.sub(lb_re, prefix+'\g<1>', gcn)
        gcn = re.sub(bt_re, prefix+'\g<0>', gcn)
        gcn = re.sub(ub_re, prefix+'\g<1>', gcn)
        gcn = re.sub(so_re, prefix+'\g<0>', gcn)  # These localities should also be updated to 9S
        gcn = re.sub(ab_re, 'Upper Ndolanya Beds, Above Tuff 8', gcn)
        gcn = re.sub(ue_re, '?Upper Ndolanya Beds', gcn)

        # Fix auto sequence error
        gcn = tf_re.sub('Laetolil Beds, Upper Unit, Between Tuffs 6 - 8', gcn)
        gcn = gcn.replace('Laetolil Beds, Upper Unit, Between Tuffs 6 - 9',
                          'Laetolil Beds, Upper Unit, Between Tuffs 6 - 8')

        # Fix remaining oddballs
        gcn = gcn.replace(' T7', ' Tuff 7 ')
        gcn = gcn.replace('T8', 'Tuff 8')
        gcn = gcn.replace('Tuff 8V', 'Tuff 8')
        gcn = gcn.replace('Between 5 - 7', 'Between Tuffs 5 - 7')
        gcn = gcn.replace('Tuffs 6 - Just Above Tuff 7', 'Tuff 6 - Just Above Tuff 7')
        gcn = gcn.replace('Tuffs 6 - Just Above Tuff 8', 'Tuff 6 - Just Above Tuff 8')

        gcn = gcn.replace('Tuffs 7 Just Above Tuff 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuff 7 Just Above Tuff 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuffs 7 - Just Above 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuffs 7 - Just Above Tuff 8', 'Tuff 7 - Just Above Tuff 8')
        gcn = gcn.replace('Tuffs 7 - Yellow Marker Tuff', 'Tuff 7 - Yellow Marker Tuff')

        gcn = gcn.replace('Laetolil Beds Between Tuffs 6 - 7', 'Laetolil Beds, Upper Unit, Between Tuffs 6 - 7')
        gcn = gcn.replace('Ngaloba Beds?', '?Ngaloba Beds')
        gcn = gcn.replace('Upper ?Ngaloba Beds', '?Upper Ngaloba Beds')
        gcn = gcn.replace('Horizon Unknown ', '')
        gcn = gcn.replace('(Th)', '')
        gcn = gcn.strip().replace('  ', ' ')  # remove any extraneous spaces

        # Convert all versions of blank to None
        if gcn in ['', ' ', None]:
            gcn = None

        # Assign to field and save
        f.geological_context_name = gcn
        f.save()

    # Fix three specimens that have incorrect geological context and locality info
    # ['EP 900/98', 'EP 901/98', 'EP 902/98']
    fossils = Fossil.objects.filter(catalog_number__in=['EP 900/98', 'EP 901/98', 'EP 902/98'])
    if fossils.count() == 3:  # should have three matches
        fossils.update(geological_context_name='Upper Ngaloba Beds')  # update does not require save


def update_description():
    """
    description and item count = verbatim_element
    starting with ca 4000 unique entries
    :return:
    """
    print("Updating description and item_count")
    # Many entries are suffixed with (N) indicating the number of items. Since N differs each is uniuqe.
    # Start by splitting out item counts
    ic_re = re.compile(r'(?P<desc>[\w\s./+-]*)(?P<count>[(]\d{1,3}[)])\s*$')  # blah blah (14)  desc='blah blah' count=(14)
    for f in Fossil.objects.all():
        m = ic_re.match(f.verbatim_element)
        if m:
            c = m.group('count')  # (14)
            f.item_count = c.replace('(', '').replace(')', '')
            d = m.group('desc')  # shells
            f.description = d
        else:
            f.description = f.verbatim_element
            f.item_count = 1
        f.description = f.description.strip().lower()
        f.description = f.description.replace('w/', ' ')
        f.description = f.description.replace('with', ' ')
        f.description = f.description.replace('m/', 'meta')
        f.description = f.description.replace('mandibular fragment', 'mandible fragment')
        f.description = f.description.replace('max fragment', 'maxilla fragment')
        f.description = f.description.replace('prox ', 'proximal ')
        f.description = f.description.replace('dist ', 'distal ')
        f.description = f.description.replace('frag ', 'fragment ')
        f.description = f.description.replace(' frag', ' fragment')
        f.description = f.description.replace('mand ', 'mandible ')
        f.description = f.description.replace('vert ', 'vertebra ')
        f.description = f.description.replace('centra', 'centrum')
        f.description = f.description.replace('tust ', 'tusk ')
        f.description = f.description.replace('rightupper', 'right upper')
        f.description = f.description.replace('rightlower', 'right lower')
        f.description = f.description.replace('leftupper', 'left upper')
        f.description = f.description.replace('leftlower', 'left lower')
        f.description = f.description.replace('.', '')
        f.description = f.description.replace('   ', ' ')
        f.description = f.description.replace('  ', ' ')
        f.description = f.description.strip()
        f.save()


def update_taxon_fields(qs=Fossil.objects.all()):
    """
    Function to read values from verbatim taxon field (e.g. verbatim_kingdom, etc.) clean the entries and
    write them to the taxonomic fields (e.g. tkingdom). All taxon fields start with t to avoid conflicts
    with python keywords (e.g. class, order). The function also updates the taxon_rank field and the
    identification_qualifier field.
    :return:
    """
    print("Updating taxonomic fields")
    krep = {
        # Kingdom
        'Animaliav': 'Animalia',
        'Animvalia': 'Animalia',
        # Phylum
        'Vertebratav': 'Vertebrata',
        'Mollosca': 'Mollusca',
        # Class
        'INSECTA': 'Insecta',
        'insecta': 'Insecta',
        # Order
        'Perrisodactyla': 'Perissodactyla',
        'Perrissodactyla': 'Perissodactyla',
        'cf. Reptilia': '',
        'Cricetidae': 'Rodentia',
    }

    frep = {
        '----': '',
        'Boidae': 'Bovidae',
        'Cercopithecidae - Colobinae': 'Cercopithecidae',
        'Chameleonidae': 'Chamaeleonidae',
        'Colobinae': 'Cercopithecidae',
        'Deinotherium': 'Deinotheriidae',
        'Endiae': 'Enidae',
        'Gerbilinae': 'Muridae',
        'Hyaendae': 'Hyaenidae',
        'Hyaneidae': 'Hyaenidae',
        'Orycteropidae': 'Orycteropodidae',
        'Proboscidean': 'Proboscidea',
        'Rhioncerotidae': 'Rhinocerotidae',
        'Scarabeidae': 'Scarabaeidae',
        'Suidea': 'Suidae',
        'Testudinae': 'Testudinidae',
        'Thryonomidae': 'Thryonomyidae',
        'Urocylidae': 'Urocyclidae',
        'Not Bovidae': '',
        'See Below': '',
        'unknown': '',
    }

    trep = {
        'Alcelapini': 'Alcelaphini',
        'Neortragini': 'Neotragini',
        'HIppotragini': 'Hippotragini',
        'Hippogtragini': 'Hippotragini',
        'Hipportagini': 'Hippotragini',
        'Hippotragin': 'Hippotragini',
        'Not Alcelaphini': '',
        'AWG': '',
        'Probably': '',
        'probably': '',
        'see below': '',
    }

    grep = {
        # remove id quals.
        'Cf.': 'cf.',
        ',': '',
        'Sp.': '',
        'Gen. Et': '',
        'Incertae': '',
        'As On Bag Label': '',
        'Large Mammal': '',
        'probably': '',
        'see below': '',
        'See Comments': '',
        'see comments': '',
        'Serpentes': '',
        'small sp.': '',
        # corrections
        'Awg - Probably Gazella Kohllarseni': 'Gazella',
        'Aepyceros probably': 'Aepyceros',
        'Aepyceros probably ': 'Aepyceros',
        'Anacus': 'Anancus',
        'Antidorcus': 'Antidorcas',
        'Antidorcas Or Gazella': 'Antidorcas or Gazella',
        'Connohaetes': 'Connochaetes',
        'Euonyma Leakey 1': 'Euonyma',
        'Eurgynathohippus': 'Eurygnathohippus',
        '"Gazella"': 'Gazella',
        '"Gazella "': 'Gazella',
        'Geochelonel': 'Geochelone',
        'Girafffa': 'Giraffa',
        'Hipportagus': 'Hippotragus',
        'Loxondonta': 'Loxodonta',
        'Orcyteropus': 'Orycteropus',
        'oryx': 'Oryx',
        'Parmualarius': 'Parmularius',
        'Parmualrius': 'Parmularius',
        'Parmularis': 'Parmularius',
        'Sergetilagus': 'Serengetilagus',
        'serengetilagus': 'Serengetilagus',
        'Sublona': 'Subulona',
        'Trochananina': 'Trochonanina',
        'Rhynchocyon pliocaenicus': 'Rhynchocyon',
    }

    srep = {
        'Cf.': 'cf.',
        'probably': '',
        '-': '',
        's[/': '',
        'Indet..': '',
        'large mammal': '',
        'sedis': '',
        'aviflumminis': 'avifluminis',
        'brachygularis': 'brachygularius',
        'cf maurusium': 'cf. maurusium',
        'exopata': 'exoptata',
        'gambaszoegensis': 'gombaszoegensis',
        'janenshchi': 'janenschi',
        'janeschi': 'janenschi',
        'kohlarseni': 'kohllarseni',
        'kohllarseni V': 'kohllarseni',
        'laeotoliensis': 'laetoliensis',
        'laeotolilensis': 'laetoliensis',
        'laetolilensis': 'laetoliensis',
        #'laetoliensis sp. nov.': 'laetoliensis',
        #'major sp. nov.': 'major',
        'palaegracilis': 'palaeogracilis',
        'paleogracilis': 'palaeogracilis',
        'serpentes': '',
        'small mammal': '',
        'small rodent': '',

    }

    p_re = re.compile(r'[(].+[)]')  # matches anything in parentheses

    iq_re = re.compile(r'[cC]f|[aA]ff|[iI]ndet|[nN]ov|[sS]p|[sS]edis|\?')  # find all cases with 'cf' or 'aff'

    sp_re = re.compile(r'sp[.]+ [aAbBcC/]{0,5}')

    iqrep = {
        'cf.': '',
        'aff.': ''
    }  # remove cf. and aff.

    def clean_taxon_field(obj, verbatim_taxon_field_name, rep_dict):
        fs = getattr(obj, verbatim_taxon_field_name)  # get value for taxon field
        if fs:
            fs = fs.strip()  # get verbatim value, remove leading and trailing spaces
            fs = p_re.sub('', fs)  # remove parenthetical
            fs = q2cf(fs)  # convert any case with ? to cf.
            fs = indet2None(fs)  # remove indet
            fs = multireplace(fs, rep_dict)  # fix random misspellings and typos
            fs, idq = update_idq(fs)
            if idq:
                setattr(obj, 'identification_qualifier', idq)
            # clean any excess whitespace
            fs = fs.replace('   ', ' ')  # remove triple spaces
            fs = fs.replace('  ', ' ')  # remove double spaces
            fs = fs.strip()  # remove leading and trailing spaces

        if fs in ['', ' ', None]:  # convert any blanks to None
            fs = None
        return fs

    def update_tsubphylum(obj):
        if obj.tphylum == 'Vertebrata':
            obj.tsubphylum = obj.tphylum
            obj.tphylum = 'Chordata'
        elif obj.tphylum == 'Hexapoda':
            obj.tsubphylum = obj.tphylum
            obj.tphylum = 'Arthropoda'

    # Update taxon columns
    for f in qs:
        f.tkingdom = clean_taxon_field(f, 'verbatim_kingdom', krep)
        f.tphylum = clean_taxon_field(f, 'verbatim_phylum_subphylum', krep)
        update_tsubphylum(f)
        f.tclass = clean_taxon_field(f, 'verbatim_class', krep)
        f.torder = clean_taxon_field(f, 'verbatim_order', krep)
        f.tfamily = clean_taxon_field(f, 'verbatim_family', frep)
        f.ttribe = clean_taxon_field(f, 'verbatim_tribe', trep)
        f.tgenus = clean_taxon_field(f, 'verbatim_genus', grep)
        f.tspecies = clean_taxon_field(f, 'verbatim_species', srep)

        # Update taxon ranks
        if f.tspecies:
            f.taxon_rank = "species"
        elif f.tgenus:
            f.taxon_rank = "genus"
        elif f.ttribe:
            f.taxon_rank = "tribe"
        elif f.tfamily:
            f.taxon_rank = "family"
        elif f.torder:
            f.taxon_rank = "order"
        elif f.tclass:
            f.taxon_rank = "class"
        elif f.tphylum:
            f.taxon_rank = "phylum"
        elif f.tkingdom:
            f.taxon_rank = "kingdom"

        f.save()

    # Update Subfamily entries recorded in Family column
    fossils = Fossil.objects.filter(verbatim_family__contains='inae')
    for f in fossils:
        f.tsubfamily = f.verbatim_family
        f.tsubfamily = f.tsubfamily.replace('Cercopithecidae - Colobinae', 'Colobinae')
        f.taxon_rank = "subfamily"
        f.save()

    # Fix remaining unique errors.

    # Fix EP 297/05  verbatim_class = 'Mammalia' but verbatim_order = 'Reptilia ?'
    # Move order entry to taxonomic notes
    f = Fossil.objects.get(catalog_number='EP 297/05')
    if f.taxon_remarks:
        f.taxon_remarks += ' ' + f.verbatim_order  # copy order entry to taxonomic remarks
    else:
        f.taxon_remarks = f.verbatim_order
    if f.torder:
        f.torder = None  # remove from torder field
    f.save()

    # Fix EP 3613/00 verbatim_order='Equidae (Th)' and verbatim_family is ''. Move entry to tfamily
    f = Fossil.objects.get(catalog_number='EP 3613/00')
    f.torder = None
    f.tfamily = 'Equidae'
    f.save()

    # Fix EP 008/03 verbatim_order = 'Reptilia'
    f = Fossil.objects.get(catalog_number='EP 008/03')
    f.torder = None
    f.save()

    # Fix EP 1548/98, EP 2265/00  ttribe = 'Hippotragini Or Alcelaphini'
    fossils = Fossil.objects.filter(ttribe='Hippotraginii Or Alcelaphini')
    for f in fossils:
        # move tribe to taxon_remarks
        if f.taxon_remarks:
            f.taxon_remarks += ' ' + f.ttribe
        else:
            f.taxon_remarks = f.ttribe
        # clear tribe
        f.ttribe = None
        f.save()

    # Fix EP 2045/00 ttribe = 'Not Neotragini'
    fossils = Fossil.objects.filter(ttribe='Not Neotragini')
    for f in fossils:
        # move tribe to taxon_remarks
        if f.taxon_remarks:
            f.taxon_remarks += ' ' + f.ttribe
        else:
            f.taxon_remarks = f.ttribe
        # clear tribe
        f.ttribe = None
        f.save()

    # Fix 5 items with tgenus = 'Antidorcas or Gazella'
    fossils = Fossil.objects.filter(tgenus='Antidorcas or Gazella')
    for f in fossils:
        # move genus to taxon_remarks
        if f.taxon_remarks:
            f.taxon_remarks += ' ' + f.tgenus
        else:
            f.taxon_remarks = f.tgenus
        # clear genus
        f.tgenus = None
        f.save()

    # Fix EP 575/00 genus = Machairodontinae
    ep575 = Fossil.objects.get(catalog_number='EP 575/00')
    ep575.tsubfamily = ep575.tgenus
    ep575.tgenus = None
    ep575.save()

    # Fix frame shift error for EP 243/05
    ep243 = Fossil.objects.get(catalog_number='EP 243/05')
    ep243.order = 'Rodentia'
    ep243.family = 'Cricetidae'
    ep243.subfamily = 'Gerbillinae'
    ep243.save()

    # Fix EP 224/04 tgenus = Scaraboidea [sic]
    ep242 = Fossil.objects.get(catalog_number='EP 242/04')
    ep242.tsubfamily = 'Scarabaeoidea'
    ep242.tgenus = None
    ep242.save()

    # Fix taxon comments and species for EP 688/98
    f = Fossil.objects.get(catalog_number='EP 688/98')
    f.tspecies = 'kohllarseni'
    remark_string = 'Awg - Probably Gazella Kohllarseni'
    if f.taxon_remarks:
        f.taxon_remarks += ' ' + remark_string
    else:
        f.taxon_remarks = remark_string
    f.save()

    # Fix taxon field for EP 1542/00. Verbatim taxon fields show mix of Urocyclidaae and Achatinidae
    # Urocyclidae was moved to EP 1543/00, need  to fix taxon field for EP 1542/00
    ep1542 = Fossil.objects.get(catalog_number='EP 1542/00')
    update_dict_1542_achatina = {
        'item_count': 2,
        'tfamily': 'Achatinidae',
        'tgenus': 'Achatina',
        'tspecies': 'zanzibarica',
        'scientific_name': 'Achatina zanzibarica',
        'taxon_rank': 'species',
    }
    ep1542 = update_from_dict(ep1542, update_dict_1542_achatina)
    remark_string = 'Urocyclidae moved to 1543/00'
    if ep1542.remarks:
        ep1542.remarks += ' ' + remark_string
    else:
        ep1542.remarks = remark_string
    ep1542.save()

    # Fix Taxon fields for splits
    update_dict = {
        'EP 1280a/01': {
            'item_count': 2,
            'tfamily': 'Achatinidae',
            'tgenus': 'Achatina',
            'tspecies': 'zanzibarica',
            'scientific_name': 'Achatina zanzibarica',
            'taxon_rank': 'species',
        },
        'EP 1280b/01': {
            'item_count': 5,
            'tfamily': 'Subulinidae',
            'tgenus': 'Pseudoglessula',
            'tspecies': 'gibbonsi',
            'scientific_name': 'Pseudoglessula gibbonsi',
            'identification_qualifier': 'cf. gibbonsi',
            'taxon_rank': 'species',
        },
        'EP 3129a/00': {
            'item_count': 8,
            'tfamily': 'Achatinidae',
            'tgenus': 'Achatina',
            'tspecies': 'zanzibarica',
            'scientific_name': 'Achatina zanzibarica',
            'taxon_rank': 'species',
        },
        'EP 3129b/00': {
            'item_count': 1,
            'tfamily': 'Subulinidae',
            'tgenus': 'Pseudoglessula',
            'tspecies': 'gibbonsi',
            'scientific_name': 'Pseudoglessula gibbonsi',
            'identification_qualifier': 'cf. Pseudoglessula gibbonsi',
            'taxon_rank': 'species',
        },
        'EP 1181a/00': {
            'item_count': 1,
            'tgenus': 'Achatina',
            'tspecies': 'zanzibarica',
            'scientific_name': 'Achatina zanzibarica',
            'taxon_rank': 'species',
        },
        'EP 1181b/00': {
            'item_count': 1,
            'tgenus': 'Burtoa',
            'tspecies': 'nilotica',
            'scientific_name': 'Burtoa nilotica',
            'taxon_rank': 'species',
        },
        'EP 3635a/00': {
            'item_count': 1,
            'tgenus': 'Achatina',
            'tspecies': 'zanzibarica',
            'scientific_name': 'Achatina zanzibarica',
            'taxon_rank': 'species',
        },
        'EP 3635b/00': {
            'item_count': 8,
            'tgenus': 'Limicolaria',
            'tspecies': 'martensiana',
            'scientific_name': 'Limicolaria martensiana',
            'taxon_rank': 'species',
        }
    }
    for catno in update_dict.keys():
        if Fossil.objects.filter(catalog_number=catno):
            fossil = Fossil.objects.get(catalog_number=catno)
            fossil = update_from_dict(fossil, update_dict[fossil.catalog_number])
            fossil.save()


def validate_taxon(taxon_name, verbose=True):
    taxon_fields = ['kingdom', 'phylum', 'class', 'order', 'family', 'subfamily']
    taxon_field_name = 't'+taxon_name
    # print('Validating {}'.format(taxon_field_name))
    api = idigbio.json()  # connection to idigbio db
    tlist = [t[0] for t in field_list(taxon_field_name, report=False) if t[0]]  # list of taxon names excluding None
    for taxon in tlist:
        # print('validating {}'.format(taxon))
        r = api.search_records(rq={taxon_name: taxon})  # search
        if r['itemCount']:
            if verbose:
                print("{} OK {}".format(taxon, r['itemCount']))
        else:
            print("{} ERROR".format(taxon))


def update_scientific_name():
    """
    Update scientific name from taxon columns. Clean data from columns then concatenate to colon delimited string.
    e.g. Animalia:Chordata:Primates:Hominoidea:Homminidae:Homininae:Homo:sapiens
    :return: A coma delimited string representing a taxonomic path/hierarchy
    """
    print("Updating scientific_name")
    # rep = {
    #     '::': ':'
    # }
    c = re.compile(r'([.]*)[:]*$')  # group everything but trailing colons
    for f in Fossil.objects.all():
        snl = [f.tkingdom, f.tphylum, f.tclass, f.torder, f.tfamily, f.tgenus, f.tspecies]
        snl = ['' if x is None else x for x in snl]  # replace None elements with empty strings
        sn = ':'.join(snl)  # join all elements in the sci name list, colon delimited
        #sn = multireplace(sn, rep)  # replace all
        sn = c.sub('\g<1>', sn)  # replace with group and omit trailing colons
        f.scientific_name = sn.strip()
        f.save()

    fix = Fossil.objects.filter(verbatim_phylum_subphylum='Arthropoda').filter(verbatim_class='Mammalia')
    for fossil in fix:
        fossil.scientific_name.replace('Arthropoda:Mammalia:', 'Vertebrata:Mammalia:')
        fossil.save()


def update_taxon_remarks(verbose=False):
    """
    Procedure to update taxon_remarks
    Copies existing data to taxon_remarks from verbatim_other
    Appends parenthetical comments from verbatim_tribe
    :return:
    """
    print("Updating taxon remarks")
    p_re = re.compile(r'[(].+[)]')  # matches anything in parentheses
    print("Updating taxon_remarks from verbatim_other")
    for f in Fossil.objects.all():
        if f.verbatim_other:
            if verbose:
                print("Updating {}".format(f.catalog_number))
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + f.verbatim_other
            else:
                f.taxon_remarks = f.verbatim_other

        # Check for parenthetical and copy to taxon_remarks
        vt = f.verbatim_tribe
        m = p_re.search(vt)  # check if parenthetical
        if m:  # if entry has parenthetical
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + m.group(0)  # append parenthetical to taxon_remarks
            else:
                f.taxon_remarks = m.group(0)  # append parenthetical to taxon_remarks
        # Move Not bovid remarks
        if f.verbatim_family == 'Not Bovidae (Awg)':
            if f.taxon_remarks:
                f.taxon_remarks += f.verbatim_family
            else:
                f.taxon_remarks = f.verbatim_family

        f.save()


def update_remarks():
    print("Updating remarks")
    for f in Fossil.objects.all():
        f.remarks = f.verbatim_comments
        f.save()


def update_problems():
    print("Updating problems")
    for f in Fossil.objects.all():
        # Must check if problem has been flagged by other import functions
        if f.verbatim_problems and not f.problem:
            f.problem = True
            # append problem comment
            if f.problem_comment:
                f.problem_comment = f.problem_comment + ' ' + f.verbatim_problems
            else:
                f.problem_comment = f.verbatim_problems
        elif f.verbatim_problems and f.problem:
            # append problem comment
            if f.problem_comment:
                f.problem_comment = f.problem_comment + ' ' + f.verbatim_problems  # append comment
            else:
                f.problem_comment = f.verbatim_problems
        else:
            pass  # If no verbatim_problems do nothing
        f.save()


def validate_splits():
    # Validate catalog numbers for splits = ['EP 1280/01', 'EP 3129/99']
    splits = SPLITS
    valid = True
    for catno in splits:
        try:
            Fossil.objects.get(catalog_number=catno)  # will raise error if splits don't exist.
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            print("Split error {}".format(catno))
            valid = False
        try:
            catnoa = catno.replace('/', 'a/')
            Fossil.objects.get(catalog_number=catnoa)
        except ObjectDoesNotExist:
            print("Split error {}".format(catnoa))
            valid = False
        try:
            catnob = catno.replace('/', 'b/')
            Fossil.objects.get(catalog_number=catnob)
        except ObjectDoesNotExist:
            print("Split error {}".format(catnob))
    if valid:
        print("No split errors found.")


# Main import function
def main(year_list=CSHO_YEARS):
    # import data
    print('Importing data from XL spreadsheets.')
    for year in year_list:
        file = make_file_string(year)
        import_file(folder=FOLDER_PATH, file=file, year=year)
    print('{} records imported'.format(Fossil.objects.all().count()))
    print('====================================')

    # delete records
    print('\nDeleting duplicate and erroneous records.')
    c = delete_records()
    print('{} records deleted'.format(c))
    print('Current record count: {}'.format(Fossil.objects.all().count()))
    print('====================================')

    # split bulk collections
    print('\nSplitting bulk collections.')
    c = split_records()
    print('{} records split'.format(c))
    print('Current record count: {}'.format(Fossil.objects.all().count()))
    print('====================================')

    # update data
    print('\nUpdating records from verbatim data.')
    update_date_recorded()
    update_catalog_number()
    update_institution()
    update_locality()
    update_area()
    update_geological_context()
    update_description()
    update_taxon_fields()
    update_scientific_name()
    update_taxon_remarks()
    update_remarks()
    update_problems()
    print('Current record count: {}'.format(Fossil.objects.all().count()))
    print('====================================')

    print('\nValidating records')
    validate_date_recorded()
    validate_catalog_number()
    validate_locality()
    validate_splits()
    print('====================================')


# Additional utility functions
def get_max_field_length(field):
    bios = Fossil.objects.all()
    try:
        max_length = max([len(getattr(b, field)) for b in bios])
    except TypeError:
        attribute_list = [getattr(b, field) for b in bios]
        attribute_list = [a for a in attribute_list if a]  # remove None values
        if attribute_list:
            try:
                max_length = max([len(a) for a in attribute_list])
            except TypeError:
                max_length = None
        else:
            max_length = None
    return max_length


def report_max_field_length():
    for f in get_verbatim_fields():
        max_length = get_max_field_length(f)
        print('{} {}'.format(f, max_length))


def get_verbatim_fields():
    return set(list(lookup_dict.values()))


def field_list(field_name, report=True):
    """
    Get the unique values for a field
    :return:
    """
    res_list = []
    for f in Fossil.objects.distinct(field_name):
        n = getattr(f, field_name)
        kwargs = {
            '{0}__{1}'.format(field_name, 'exact'): n
        }
        c = Fossil.objects.filter(**kwargs).count()
        t = (n, c)
        res_list.append(t)
    if report:
        for i in res_list:
            print("{} {}".format(*i))  # use * to unpack tuple
    return res_list


def multireplace(string, replacements):
    """
    Replace multiple matches in a string at once.
    :param string: The string to be processed
    :param replacements: a dictionary of replacement values {value to find, value to replace}
    :return: returns string with all matches replaced.
    Credit to bgusach, https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
    """
    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    substrs = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def q2cf(taxon_string):
    cf_re = re.compile(r'[?]')  # find all cases with '?'
    if cf_re.search(taxon_string):
        if taxon_string.strip() == '?':  # If taxon is just ? replace with None
            taxon_string = ''
        else:
            taxon_string = 'cf. ' + cf_re.sub('', taxon_string)  # If case has ? remove it and prefix with cf.
    return taxon_string


def indet2None(taxon_string):
    indet_re = re.compile(r'[Ii]ndet[.]*')
    ndet_re = re.compile(r'[Nn]o [Dd]et[.]*[ here]*')
    taxon_string = indet_re.sub('', taxon_string)
    taxon_string = ndet_re.sub('', taxon_string)
    taxon_string = taxon_string.replace('No ID', '')
    taxon_string = taxon_string.replace('no id', '')
    taxon_string.strip()
    return taxon_string


def clear_problem_duplicate(o):
    o.problem = False
    o.problem_comment = o.problem_comment.replace('Duplicate catalog number!', '')
    o.save()


def diff_fossils(catalog_number):
    fossils = Fossil.objects.filter(catalog_number=catalog_number)
    for i in fossils[0].__dict__:
        print(str(fossils[0].__dict__[i])+'     '+str(fossils[1].__dict__[i]))


def import_report(year_list=CSHO_YEARS):
    record_count_list = []
    for year in year_list:
        workbook_name = make_file_string(year)
        count = Fossil.objects.filter(verbatim_workbook_name=workbook_name).count()
        record_count_list.append((year, count))
    return record_count_list


def update_from_dict(obj, update_dict):
    """
    A function to update an object instance with values stored in a dictionary.
    In some cases preferred over calling filter(pk=pk).update(**dict) because update does not send signals.
    :param obj: The object instance to be updated
    :param update_dict: A dictionary of attribute-value pairs to update the object
    :return: Returns the object instance with upated values. But still need to save the changes!
    """
    #
    for attr, value in update_dict.items():
        setattr(obj, attr, value)
    return obj


def duplicate(obj):
    """
    Duplicate an object in the database and return the duplicate.
    Warning, original obj now points to new object
    a = Fossil.objects.get(catalog_number = 'EP 1280/01')
    a
    <Fossil 11132>
    b = duplicate(a)
    b
    <Fossil 11134>
    a
    <Fossil 11134> !!!
    :param obj:
    :return: Return the duplicate object.
    """
    obj.id = None
    obj.pk = None
    obj.save()
    return obj


def split2part(obj):
    """
    Split a catalog number into lettered two lettered parts, by default into a and b.
    Example split EP 1280/00 into 1280a/00 and 1280b/00.
    :param obj: A fossil object to be split
    :param parts:
    :return:
    """
    # Confirm no lettered part in catalog number
    cat_re = re.compile(r'EP \d{3,4}/[09][01234589]$')
    if type(obj) == Fossil:
        if cat_re.match(obj.catalog_number):
            obj.catalog_number = obj.catalog_number.replace('/', 'a/')  # insert part letter
            obj.save()
            old_obj_id = obj.id
            old_obj = Fossil.objects.get(id=old_obj_id)
            new_obj = duplicate(obj)  # Here obj now points to new_obj!
            new_obj.catalog_number = new_obj.catalog_number.replace('a/', 'b/')
            new_obj.save()  # save second copy
            return old_obj, new_obj
        else:
            print("catalog number already has parts")
            return None
    else:
        raise TypeError


def restore_splits():
    splits = SPLITS
    for catno in splits:
        cata = catno.replace('/', 'a/')
        catb = catno.replace('/', 'b/')
        try:
            b = Fossil.objects.get(catalog_number=catb)
            b.delete()
            a = Fossil.objects.get(catalog_number=cata)
            a.catalog_number = catno
            a.save()
            update_taxon_fields(qs=Fossil.objects.filter(catalog_number=catno))
        except ObjectDoesNotExist:
            pass


def get_pbdb_taxon(taxon_name):
    url = 'https://paleobiodb.org/data1.2/taxa/single.txt?name='+taxon_name
    resp = requests.get(url)
    if resp.status_code == 200:
        h, d = resp.content.decode('utf-8').replace('"','').split('\r\n')[0:2]
        h = h.split(',')
        d = d.split(',')
        result = dict(zip(h, d))
    else:
        result = None
    return result


