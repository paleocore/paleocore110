from .models import Fossil

file_path = '/Users/reedd/Desktop/vif.txt'
map = {'Locality': 'locality',
       'Element': 'element',
       'Acession number': 'catalog_number',
       'Age': 'age',
       'Notes': 'remarks',
       'Reference': 'reference',
       }

def validate_map(model):
    error_count = 0
    fields = model._meta.get_fields()
    field_list = [f.name for f in fields]
    for v in map.values():
        if v not in field_list:
            error_count += 1
    return error_count


def import_from_csv(path, map):
    """
    Function to read data from a delimited text file
    :return: list of header values, list of row data lists
    """
    csvfile = open(path)
    data = csvfile.readlines()
    csvfile.close()
    data_list = []
    header_list = data[0][:-1].split('\t')  # list of column headers
    # populate data list
    for row in data[1:]:  # skip header row
        data_list.append(row[:-1].split('\t'))  # remove newlines and split by delimiter
        #data_list.append(row.split('\t'))  # remove newlines and split by delimiter
    print('Importing data from {}'.format(file_path))
    return header_list, data_list

def import_data(data, map):
    for row in data:
        if row[3]:
            age=float(row[3])
        else:
            age=None
        Fossil.objects.create(
            locality = row[0],
            element=row[1],
            catalog_number=row[2],
            age=age,
            remarks=row[4],
            reference=row[5]
        )

