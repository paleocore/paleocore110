from django.core.exceptions import ObjectDoesNotExist
from .models import Fossil
import xlrd
from datetime import datetime
import pytz
import re
from paleocore110.settings import PROJECT_ROOT
from sys import path
import collections

#FOLDER_PATH = '/Users/dnr266/Documents/PaleoCore/projects/Laetoli/csho_versions/'
FOLDER_PATH = PROJECT_ROOT + '/laetoli/fixtures/'
YEARS = [1998, 1999, 2000, 2001, 2003, 2004, 2005, 2012, 2014, 2016]
CSHO_YEARS = YEARS[0:7]  # 1998-2005
file_name = 'laetoli_csho_1998'
verbose_default = False


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
    :param file: String value containing file name without leading or trailing slashes.
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
    print("\nImporting data from {}".format(file))  # Indicate function has started
    book = open_book(folder, file)  # open the excel workbook
    sheet = get_max_sheet(book)
    header = get_header_list(sheet)
    if validate_header_list(header):
        rc, cc = import_sheet(year, file, book, header, sheet, verbose=verbose)
        print("Processed {rc} rows and created {cc} new Fossil objects.".format(rc=rc, cc=cc))
    else:
        print('Invalid Header List')


# Functions for processing and validating data by field
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
    transfer and validate catalog numbers
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
    for fossil in Fossil.objects.all():
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

    # Fix 13 Duplicates
    # Seven specimens are clones. Delete one of each
    # clones = ['EP 1582b/00', EP 1144/04', 'EP 1173/04', 'EP 1400/04', 'EP 1403/04', 'EP 1542/04', 'EP 515/05']
    # 1. Fix EP 1582b/00. Keep the item with the more complete description.
    fossil = Fossil.objects.get(catalog_number='EP 1582b/00', verbatim_element='Dist. M/Podial')
    fossil.delete()

    # 2 - 7.  Fix 6 cloned entries, delete one copy.
    for cn in ['EP 1144/04', 'EP 1173/04', 'EP 1400/04', 'EP 1403/04', 'EP 1542/04', 'EP 515/05']:
        fossils = Fossil.objects.filter(catalog_number=cn)
        if len(fossils) == 2:
            delete_me = fossils[0]
            delete_me.delete()

    # Fix two pairs of duplicate entries that reflect emended taxonomic identifications of the same specimen.
    # emended_specimens = ['EP 001/98', 'EP 1477b/00']
    # EP 001/98 was emended from crocodile to rhino
    # EP 1477b/00 was emended from suid to felid

    # 8. Fix EP 0001/98.
    # Delete the crocodile entry and update the taxonomic remarks to reflect the change in the rhino entry.
    fossil = Fossil.objects.get(catalog_number='EP 001/98', verbatim_family='Crocodylidae')
    fossil.delete()

    # Update comments to the rhino entry.
    fossil = Fossil.objects.get(catalog_number='EP 001/98', verbatim_family='Rhinocerotidae')
    if fossil.taxon_remarks:
        fossil.taxon_remarks += ' Identification updated from Animalia:Vertebrata:Reptilia:Crocodilia:Crocodylidae'
        fossil.save()
    else:
        fossil.taxon_remarks = 'Identification updated from Animalia:Vertebrata:Reptilia:Crocodilia:Crocodylidae'
        fossil.save()

    # 9. Fix EP 1477b/00 and also related specimen EP 1477a/00
    # Delete the suid entry.
    fossil = Fossil.objects.get(catalog_number='EP 1477b/00', verbatim_order='Artiodactyla')
    fossil.delete()
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

    # We are still left with four duplicates resulting from typos during digitization.
    # duplicates = ['EP 1052/98', 'EP 1075/03', 'EP 348/04', 'EP 2188/99']
    # These items need to be fixed individually.

    # 10. Fix EP 1052/98. The Aves specimen has a typo in the catalog number. Should be EP 1062/98
    fossil = Fossil.objects.get(catalog_number='EP 1052/98', verbatim_class='Aves')
    fossil.delete()
    
    # 11. Fix EP 1075/03. The Serengetilabus specimen has a typo in the catalog number. Should be EP 1975/03
    fossil = Fossil.objects.get(catalog_number='EP 1075/03', verbatim_genus='Serengetilagus')
    fossil.catalog_number = 'EP 1975/03'
    fossil.save()

    # 12. Fix EP 348/04. The distal radius specimen has a typo in the catalog number and incorrect date. It should
    # read EP 349/04 and the date should be 29 June 2004
    fossil = Fossil.objects.get(catalog_number='EP 348/04', verbatim_element='Distal radius')
    fossil.catalog_number = 'EP 349/04'
    tz = pytz.timezone('Africa/Dar_es_Salaam')
    fossil.date_recorded = datetime(year=2004, month=6, day=29, tzinfo=tz)
    fossil.save()

    # 13. Fix EP 2188/99, the Bovidae distal humerus is a typo and should be EP 2188/03
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


def validate_locality():
    locality_list = field_list('locality_name')
    i = 1
    for loc in locality_list:
        locality_set = set([l.verbatim_locality for l in Fossil.objects.filter(locality_name=loc[0])])
        locality_string = str(locality_set)[1:-1].replace("', ", "'; ")
        area_set = set([l.area_name for l in Fossil.objects.filter(locality_name=loc[0])])
        area_string = '; '.join(area_set)
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


def update_taxon_fields():
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
    }

    frep = {
        '----': '',
        'Boidae': 'Bovidae',
        'Cercopithecidae - Colobinae': 'Cercopithecidae',
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
        'Cf.': 'cf.',
        ',': '',
        'Sp.': '',
        'Gen. Et': 'gen. nov.',
        'Incertae ': '',
        'As On Bag Label': '',
        'Large Mammal': '',
        'probably': '',
        'see below': '',
        'See Comments': '',
        'see comments': '',
        'Serpentes': '',
        'small sp.': '',
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
    }

    srep = {
        'cf ': 'cf. ',
        'Sp.': 'sp.',
        'Nov': 'nov',
        'nov. sp.': 'sp. nov.',
        'probably': '',
        '-': '',
        's[/': 'sp.',
        'Indet..': 'indet',
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
        'palaegracilis': 'palaeogracilis',
        'paleogracilis': 'palaeogracilis',
        'serpentes': '',
        'small mammal': '',
        'small rodent': '',

    }

    p_re = re.compile(r'[(].+[)]')  # matches anything in parentheses

    cf_re = re.compile(r'[?]')  # find all cases with '?'
    cfstart = re.compile(r'^[?][\s]*(.*)')
    cfend = re.compile(r'(.*)[?]')
    id_re = re.compile(r'[Tt][Hh]|[A][Ww][Gg]')

    def clean_taxon_field(obj, verbatim_taxon_field_name, rep_dict):
        vfn = verbatim_taxon_field_name
        fs = getattr(f, vfn).strip()  # get verbatim value, remove leading and trailing spaces
        fs = p_re.sub('', fs)  # remove parenthetical
        fs = q2cf(fs)  # convert any case with ? to cf.
        fs = indet2None(fs)  # remove indet
        fs = multireplace(fs, rep_dict)  # fix random misspellings and typos
        fs = fs.replace('   ', ' ')  # remove double spaces
        fs = fs.replace('  ', ' ')  # remove double spaces
        fs = fs.strip()  # remove leading and trailing spaces
        if fs in ['', ' ', None]:  # convert any blanks to None
            fs = None
        return fs

    for f in Fossil.objects.all():
        f.tkingdom = clean_taxon_field(f, 'verbatim_kingdom', krep)
        f.tphylum = clean_taxon_field(f, 'verbatim_phylum_subphylum', krep)
        f.tclass = clean_taxon_field(f, 'verbatim_class', krep)
        f.torder = clean_taxon_field(f, 'verbatim_order', krep)
        f.tfamily = clean_taxon_field(f, 'verbatim_family', frep)
        f.ttribe = clean_taxon_field(f, 'verbatim_tribe', trep)
        f.tgenus = clean_taxon_field(f, 'verbatim_genus', grep)
        f.tspecies = clean_taxon_field(f, 'verbatim_species', srep)

        f.save()


def update_subfamily():
    fossils = Fossil.objects.filter(verbatim_family__contains='inae')
    for f in fossils:
        f.subfamily = f.verbatim_family
        f.subfamily = f.subfamily.replace('Cercopithecidae - Colobinae', 'Colobinae')
        f.save()


def validate_kingdom():
    pass


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


def update_taxon_remarks():
    """

    :return:
    """
    print("Updating taxon remarks")
    p_re = re.compile(r'[(].+[)]')  # matches anything in parentheses
    for f in Fossil.objects.all():
        if f.taxon_remarks:
            f.taxon_remarks += f.verbatim_other
        else:
            f.taxon_remarks = f.verbatim_other

        # Check for parenthetical and copy to taxon_remarks
        vt = f.verbatim_tribe
        m = p_re.search(vt)  # check if parenthetical
        if m:  # if entry has parenthetical
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + m.group(0)  # append parenthetical to taxon_remarks
            else:
                f.taxon_remarks = ' ' + m.group(0)  # append parenthetical to taxon_remarks
        # Move Not bovid remarks
        if f.verbatim_family == 'Not Bovidae (Awg)':
            if f.taxon_remarks:
                f.taxon_remarks += ' ' + f.verbatim_family
            else:
                f.taxon_remarks = ' ' + f.verbatim_family

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


def update_stragglers():
    """
    Fix any remaining unique problems
    :return:
    """
    print("Updating stragglers")
    # Fix three specimens that have incorrect geological context and locality info
    # ['EP 900/98', 'EP 901/98', 'EP 902/98']
    update_dict = {'geological_context_name': 'Upper Ngaloba Beds', 'locality_name': 'Laetoli 9 South'}
    fossils = Fossil.objects.filter(catalog_number__in=['EP 900/98', 'EP 901/98', 'EP 902/98'])
    if fossils.count() == 3:  # should have three matches
        fossils.update(**update_dict)

    # Fix EP 297/05  verbatim_class = 'Mammalia' but verbatim_order = 'Reptilia ?'
    # Move order entry to taxonomic notes
    f = Fossil.objects.get(catalog_number='EP 297/05')
    f.taxon_remarks += ' ' + f.verbatim_order  # copy order entry to taxonomic remarks
    if f.torder:
        f.torder = f.torder.replace('Reptilia', '')  # remove from torder field
    f.save()

    # Fix EP 3613/00 verbatim_order='Equidae (Th)' and verbatim_family is ''. Move entry to tfamily
    f = Fossil.objects.get(catalog_number='EP 3613/00')
    f.torder = f.torder.replace('Equidae', '')
    f.tfamily = 'Equidae'
    f.save()

    # Fix EP 008/03 verbatim_order = 'Reptilia'
    f = Fossil.objects.get(catalog_number='EP 008/03')
    f.torder = None
    f.save()

    # Fix taxon comments and species for EP 688/98
    f = Fossil.objects.get(catalog_number='EP 688/98')
    f.tspecies = 'kohllarseni'
    f.taxon_remarks += ' Awg - Probably Gazella Kohllarseni'
    f.save()


# Main import function
def main(year_list=CSHO_YEARS):
    # import data
    print('Importing data from XL spreadsheets')
    for year in year_list:
        file = make_file_string(year)
        import_file(folder=FOLDER_PATH, file=file, year=year)
    print('====================================')

    # update data
    print('\nUpdating records from verbatim data')
    update_date_recorded()
    update_catalog_number()
    update_institution()
    update_locality()
    update_area()
    update_geological_context()
    update_description()
    update_taxon_fields()
    update_subfamily()
    update_scientific_name()
    update_taxon_remarks()
    update_remarks()
    update_problems()
    update_stragglers()
    print('====================================')

    print('\n Validating records')
    validate_date_recorded()
    validate_catalog_number()
    validate_locality()
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
