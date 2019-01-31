import unicodecsv
from .models import *
from difflib import SequenceMatcher
from lxml import etree
from django.core.exceptions import ObjectDoesNotExist

# pbdb_file_path = "/Users/reedd/Documents/projects/ete/pbdb/pbdb_test_no_header.csv"
pbdb_collections_contexts_file_path = "/Users/reedd/Documents/projects/ete/pbdb/pbdb_collections_Africa_no_header.csv"

# pbdb_refs_path = "/Users/reedd/Documents/projects/ete/pbdb/pbdb_refs_test.csv"
pbdb_collection_refs_path = "/Users/reedd/Documents/projects/ete/pbdb/pbdb_refs_colls.csv"
pbdb_occurrence_refs_path = "/Users/reedd/Documents/projects/ete/pbdb/pbdb_refs_occurs.csv"

# si_ho_path = "/Users/reedd/Documents/projects/ete/si_ho/si_ho_specimens_test.xml"
hopdb_path = "/Users/reedd/Documents/projects/ete/si_ho/si_ho_specimens.xml"


def import_pbdb_refs(path):
    with open(path, 'U') as csvfile:
        reader = unicodecsv.DictReader(csvfile, encoding='utf-8')
        count = 0
        created_count = 0
        for row in reader:
            ref_dict = {f: row[f] for f in reader.fieldnames}
            # Check if ref exists using reference_no, if doesn't exist, create a new one.
            obj, created = Reference.objects.get_or_create(reference_no=row['reference_no'],
                                                           defaults=ref_dict)
            obj.source = 'pbdb'
            obj.save()
            if created:
                created_count += 1
            count += 1
        print('Successfully import {} references'.format(count))
        print('Report: {} processed, {} created'.format(count, created_count))


def import_pbdb_collections_to_contexts(path):
    """
    Read data from csv file and create new context objects
    :param path:
    :return:
    """
    csv_file = open(path, 'U')
    reader = unicodecsv.DictReader(csv_file, encoding='utf-8')
    count = 0

    for row in reader:
        new_context = Context()
        for field in reader.fieldnames:
            value = row[field]
            if value in ['', ' ']:
                value = None
            new_context.__setattr__(field, value)
        new_context.geom = "Point({} {})".format(row['lng'], row['lat'])
        new_context.source = "pbdb"
        new_context.save()  # saving here coverts attribute data to proper types
        if new_context.max_ma >= 1.8 and new_context.min_ma <= 7.25:
            new_context.mio_plio = True
        try:
            new_context.reference = Reference.objects.get(reference_no=new_context.reference_no)
        except Reference.DoesNotExist:
            new_context.reference = None
        new_context.save()
        count += 1
    csv_file.close()

    print('Successfully imported {} context objects.'.format(count))
    print('Report: Total: {}, mio_plio: {}'.format(count, Context.objects.filter(mio_plio=True).count()))


def delete_all_contexts():
    contexts = Context.objects.all()
    count = 0
    for c in contexts:
        c.delete()
        count += 1
    print('Successfully deleted all {} Context objects'.format(count))


def delete_all_sites():
    sites = Site.objects.all()
    count = 0
    for c in sites:
        c.delete()
        count += 1
    print('Successfully deleted all {} Site objects'.format(count))


def create_sites_from_contexts():
    """
    Generate the sites by aggregating over the contexts. Contexts are aggregated using the formation field.
    :return:
    """
    contexts = Context.objects.all()
    # create a new site based on first context in each formation
    site_count = 0
    for c in contexts:
        data_dict = {f: c.__getattribute__(f) for f in c.get_concrete_field_names()}
        # Delete dictionary keys unique to context model but not in site model
        context_fields_not_in_site = ['site', 'reference']
        for f in context_fields_not_in_site:
            try:
                del data_dict[f]
            except KeyError:
                pass
        # For each context, c, check if a site exists that has the same formation.
        # If no site exists create a new one using the data from that context.
        obj, created = Site.objects.get_or_create(formation=c.formation, defaults=data_dict)
        if created:
            site_count += 1
        c.site = obj  # assign site fk to each context
        c.save()

    print('Successfully created {} new sites from {} context objects'.format(site_count, contexts.count()))


def validate_context_references():
    # Validate referential integrity of all context references
    # returns True, []  if all contexts have a reference
    # returns False, [context_id_list] if any contexts are missing references

    result = True
    result_list = []
    for c in Context.objects.all():
        try:
            c.reference = Reference.objects.get(reference_no=c.reference_no)
        except Reference.DoesNotExist:
            result = False
            result_list.append(c.id)
    return result, result_list


def get_tag_list(element_tree):
    """
    Function to generate a list of all element tags from an xml file
    :param element_tree:
    :return:
    """
    return list(set([c.tag for c in element_tree.iter()]))


def import_hopdb_fossil_elements(path):
    """
    Function to import fossil elements from xml file downloaded from the HOP DB.
    This function populates both the FossilElement table and the Fossils table.
    Fossils are aggregated from elements based on values in the HomininElement field
    :param path:
    :return:
    """
    xml_file = open(path, 'U')
    tree = etree.parse(xml_file)  # tree is an lxml ElementTree object
    element_tree = tree.getroot()
    xml_file.close()

    africa_list = [u'Chad', u'Libya', u'South Africa', u'Tanzania', u'Morocco', u'Malawi', u'Ethiopia', u'Algeria',
                   u'Namibia', u'Kenya', u'Zambia']
    asia_list = [u'Israel', u'Indonesia', u'China', u'Vietnam', u'Iraq']
    item_count = 0
    for specimen in element_tree:
        new_fossil_element = FossilElement()
        # specimen_name = specimen.find('HomininElement').text
        specimen_dict = {e.tag: e.text for e in specimen}
        for element in specimen:
            new_fossil_element.__setattr__(element.tag, element.text)
        new_fossil_element.save()
        # try:
        #     print 'created new specimen {} {}'.format(new_fossil_element.id, specimen_name)
        # except UnicodeEncodeError:
        #     print 'created new specimen {}'.format(new_fossil_element.id)
        item_count += 1
        obj, created = Fossil.objects.get_or_create(HomininElement=new_fossil_element.HomininElement,
                                                    defaults=specimen_dict)
        if created:
            if obj.Country:
                if obj.Country in africa_list:
                    obj.continent = 'Africa'
                elif obj.Country in asia_list:
                    obj.continent = 'Asia'
            obj.save()
        new_fossil_element.fossil = obj
    print('Successfully imported {} fossil elements from the HOPDB'.format(item_count))


def get_max_text_lengths(element_tree):
    """
    Function to calculate the maximum length of all text entries in the xml file. This is useful
    for setting the max_length parameters  and correct field types in the model.
    :param element_tree:
    :return: Returns a dict with tag names and max length of text for each tag.
    """
    tag_dict = {}
    for sp in element_tree:
        for element in sp:
            if element.text is not None:
                text_length = len(element.text)
                try:
                    if text_length > tag_dict[element.tag]:
                        tag_dict[element.tag] = text_length
                except KeyError:
                    tag_dict[element.tag] = text_length
    return tag_dict


def get_fossil_placenames():
    """
    Function to fetch a list of unique placenames/contexts for each fossil using the placename field
    :return:
    """
    result_list = []
    unique_placenames = list(set([f.PlaceName for f in Fossil.objects.filter(continent='Africa')]))
    for p in unique_placenames:
        result_list.append([p, Fossil.objects.filter(PlaceName=p).count()])
    return sorted(result_list, key=lambda x: x[1], reverse=True)  # sort list by fossil count descending


def similar(t):
    a, b = t
    return SequenceMatcher(None, a, b).ratio()


def main():
    import_pbdb_refs(path=pbdb_collection_refs_path)
    import_pbdb_refs(path=pbdb_occurrence_refs_path)

    import_pbdb_collections_to_contexts(path=pbdb_collections_contexts_file_path)
    create_sites_from_contexts()

    import_hopdb_fossil_elements(path=hopdb_path)


def get_country_from_geom(geom):
    try:
        country_object = WorldBorder.objects.get(mpoly__intersects=geom)
        country_code = country_object.iso2
    except ObjectDoesNotExist:
        country_code = None
    return country_code


state_abbr = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY']


