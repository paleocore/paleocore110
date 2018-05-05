import urllib.request
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
import re
from standard.models import *
from projects.models import *

dwc_url = 'http://rs.tdwg.org/dwc/terms/'
simple_dwc_url ='http://rs.tdwg.org/dwc/terms/simple/'


def get_dwc_html(url=dwc_url):
    opener = urllib.request.build_opener()
    html = opener.open(url)
    return html


def get_terms_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    tbody_list = soup.find_all('tbody')
    for t in tbody_list:
        if t.find_all(string=re.compile('Begin Terms Table')):
            return t


def get_dwc_terms():
    """
    Function to scrape Darwin Core terms from the Darwin Core website.
    Class is set to None where Class is empty.
    :return: [(0_name, 1_identifier, 2_class, 3_definition, 4_comments, 5_details), ... ]
    names = [t[0] for t in result_list]
    """
    result_list = []
    html = get_dwc_html()
    terms_table = get_terms_table(html)
    tr_list = terms_table.find_all('tr')
    term_chunks = [tr_list[i:i+6] for i in range(0, len(tr_list), 6)]
    for t in term_chunks[0:]:
        tname = t[0].string[11:].strip()
        tidentifier, tclass, tdefinition, tcomments, tdetails = [t[i].td.next_sibling.contents for i in range(1, 6)]
        if tclass:
            tclass = tclass[0]
        else:
            tclass = None
        result_list.append((tname, tidentifier[0], tclass, tdefinition[0], tcomments[0], tdetails[0]))
    return result_list


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def ppterms(dict):
    pstring = 'Name: {}\nIdentifier: {}\nClass: {}\nDefinition: {}\nComments: {}\nDetails: {}\n------------------------'
    for t in dict:
        try:
            print_string = pstring.format(t[0], t[1], t[2], t[3], t[4], t[5])
            print(print_string)
        except UnicodeEncodeError:
            print_string = 'Unable to print {}'.format(t[0])
            print(print_string)


def get_my_dwc():
    return [term_object for term_object in Term.objects.filter(projects=10)]


def compare_terms():
    dwc = get_dwc_terms()  # list of tuples
    mydwc = get_my_dwc() # list of objects
    dwc_ids =  set([t[1] for t in dwc]) # ids should be unique. len(set) should equal len(list)
    mydwc_ids = set([t.uri for t in mydwc])
    return [[dwc_ids - mydwc_ids], [dwc_ids & mydwc_ids], [mydwc_ids - dwc_ids]] # [left_comp, intersection, right_comp]


def import_dwc_terms():
    dwc = get_dwc_terms()
    dwc_project_object = Project.objects.get(short_name='Darwin Core')
    for t in dwc:
        if t[2] in [None, '']:
            category = TermCategory.objects.get(name='Class')
        elif t[2] == 'all':
            category = TermCategory.objects.get(name='Record')
        else:
            category = TermCategory.objects.get(uri=t[2])

        try:
            #  (0_name, 1_identifier, 2_class, 3_definition, 4_comments, 5_details)
            myt = Term.objects.get(uri=t[1])
            myt.name = t[0]
            myt.category = category
            myt.definition = t[3]
            myt.examples = t[4]
            myt.save()

            if dwc_project_object not in myt.projects.all():
                ProjectTerm.objects.create(
                    project=dwc_project_object,
                    term=myt,
                    native=True,
                )

        except ObjectDoesNotExist:
            myt = Term.objects.create(
                name=t[0],
                uri=t[1],
                category=category,
                definition=t[3],
                example=t[4],
                remarks=t[5],
                status=TermStatus.objects.get(name='standard'),
                data_type=TermDataType.objects.get(name='string'),
                uses_controlled_vocabulary=False
            )

            ProjectTerm.objects.create(
                project=dwc_project_object,
                term=myt,
                native=True,
            )


def import_dwc_classes():
    dwc = get_dwc_terms()
    for t in dwc:
        if t[2] in ['', None]:
            try:
                category_object = TermCategory.objects.get(name=t[0])
                category_object.uri = t[1]
                category_object.description = t[3]
                category_object.save()
            except ObjectDoesNotExist:
                TermCategory.objects.create(
                    name=t[0],
                    uri=t[1],
                    description=t[3],
                    is_occurrence=False,
                    tree_visibility=True
                )


#        | Classes  Terms |
# Simple |    13     169  | 182
# Aux    |     2      16  |  18
# -----------------------------
#             15     185  | 200
def dwc_summary():
    dwc = Term.objects.filter(projects__short_name='Darwin Core')  # all dwc terms = 200
    dwc_classes = dwc.filter(is_class=True)  # classes = 15
    dwc_terms = dwc.filter(is_class=False)  # terms without classes = 15

    sdwc = dwc.exclude(category__name='ResourceRelationship').exclude(category__name='MeasurementOrFact') # simple = 182
    sdwc_classes = sdwc.filter(is_class=True)  # simple dwc classes = 13
    sdwc_terms = sdwc.filter(is_class=False)  # simple dwc terms = 169

    adwc = dwc.filter(category__name__in=['ResourceRelationship', 'MeasurementOrFact'])  # aux dwc = 18
    adwc_classes = adwc.filter(is_class=True)  # aux dwc classes = 2
    adwc_terms = adwc.filter(is_class=False)  # aux dwc terms = 16

    row1 = '       | Classes  Terms |'
    row2 = 'Simple |    {}     {}  |  {}'
    row3 = 'Aux    |     {}      {}  |   {}'
    row4 = '-----------------------------'
    row5 = '            {}     {}  | {}'

    print(row1)
    print(row2.format(sdwc_classes.count(), sdwc_terms.count(), sdwc.count()))
    print(row3.format(adwc_classes.count(), adwc_terms.count(), adwc.count()))
    print(row4)
    print(row5.format(dwc_classes.count(), dwc_terms.count(), dwc.count()))


def print_dwc_terms():
    categories = [['Record'], ['Occurrence'], ['Organism'], ['MaterialSample', 'LivingSpecimen', 'PreservedSpecimen',
                  'FossilSpecimen'], ['Event', 'HumanObservation', 'MachineObservation'], ['Location'],
                  ['GeologicalContext'], ['Identification'], ['Taxon']]
    dwc = Term.objects.filter(projects__short_name='Darwin Core')
    for c in categories:
        print_string = ', '.join(c)
        print(print_string)
        terms = dwc.filter(category__name=c[0]).filter(is_class=False).order_by('name')
        for t in terms:
            print(t)


from mlp.models import *
def update_mlp_terms():
    """
    Procedure to read mlp.models and from that add terms. Not working yet: need way to select data_type based on
    field type, e.g. CharField == string
    :return:
    """
    bio = Biology
    arch = Archaeology

    # get a unique set of terms from all relevant models

    field_list = list(set([f for f in bio._meta.get_fields()] + [f for f in arch._meta.get_fields()]))
    # iterate over fields, check if each is in the DB, if not add, if yes check if assoc. with project
    active_status = TermStatus.objects.get(name='active')
    mlp = Project.objects.get(paleocore_appname='mlp')
    string = TermDataType.objects.get(name='string')
    for field in field_list:
        t, created = Term.objects.get_or_create(name=field.name, defaults={'name': field.name,
                                                                           'status': active_status,
                                                                           'data_type': string,
                                                                           'definition': field.description})
        pt = ProjectTerm.objects.create(term=t, project=mlp)
