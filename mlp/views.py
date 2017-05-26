from django.conf import settings
from django.views import generic
import os
from .models import Occurrence, Biology
from mlp.forms import UploadKMLForm, DownloadKMLForm, ChangeXYForm, Occurrence2Biology
from fastkml import kml
from fastkml import Placemark, Folder, Document
from lxml import etree
from datetime import datetime
from django.contrib.gis.geos import GEOSGeometry
from pygeoif import geometry
from zipfile import ZipFile
from mlp.models import Taxon, IdentificationQualifier
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages


class DownloadKMLView(generic.FormView):
    template_name = 'projects/download_kml.html'
    form_class = DownloadKMLForm
    context_object_name = 'download'
    success_url = '/projects/mlp/confirmation/'

    def form_valid(self, form):
        k = kml.KML()
        ns = '{http://www.opengis.net/kml/2.2}'
        d = kml.Document(ns, 'docid', 'MLP Observations', 'KML Document')
        f = kml.Folder(ns, 'fid', 'MLP Observations Root Folder',
                       'Contains place marks for specimens and observations.')
        k.append(d)
        d.append(f)
        occurrences = Occurrence.objects.all()
        for o in occurrences:
            if o.geom:
                p = kml.Placemark(ns, 'id', 'name', 'description')
                # coord = utm.to_latlon(o.geom.coords[0], o.geom.coords[1], 37, 'P')
                pnt = geometry.Point(o.geom.coords[0], o.geom.coords[1])
                p.name = o.__str__()
                d = "<![CDATA[<table>"
                openrow = "<tr><td>"
                middlerow = "</td><td style='font-weight:bold'>"
                closerow = "</td></tr>"

                d += openrow
                d += ''.join(("Basis of Record", middlerow))
                d += ''.join([_f for _f in (o.basis_of_record, closerow, openrow) if _f])
                d += ''.join(("Time", middlerow))
                d += ''.join([_f for _f in (str(o.field_number), closerow, openrow) if _f])
                d += ''.join(("Item Type", middlerow))
                d += ''.join([_f for _f in (o.item_type, closerow, openrow) if _f])
                d += ''.join(("Collector", middlerow))
                d += ''.join([_f for _f in (o.collector, closerow, openrow) if _f])
                d += ''.join(("Collection Method", middlerow))
                d += ''.join([_f for _f in (o.collecting_method, closerow, openrow) if _f])
                d += ''.join(("Count", middlerow))
                d += ''.join([_f for _f in (str(o.individual_count), closerow, openrow) if _f])
                d += ''.join(("Bar Code", middlerow))
                d += ''.join([_f for _f in (str(o.barcode), closerow, openrow) if _f])
                d += ''.join(("Scientific Name", middlerow))
                d += ''.join([_f for _f in (o.item_scientific_name, closerow, openrow) if _f])
                d += ''.join(("Description", middlerow))
                d += ''.join([_f for _f in (o.item_description, closerow, openrow) if _f])
                d += ''.join(("Remarks", middlerow))
                d += ''.join([_f for _f in (o.remarks, closerow, openrow) if _f])
                d += ''.join(("In Situ", middlerow))
                d += ''.join([_f for _f in (str(o.in_situ), closerow) if _f])
                d += "</table>"
                p.description = d
                p.geometry = pnt
                f.append(p)
        r = k.to_string(prettyprint=True)
        response = HttpResponse(r, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="mlp.kml"'
        return response


class UploadKMLView(generic.FormView):
    template_name = 'projects/upload_kml.html'
    form_class = UploadKMLForm
    context_object_name = 'upload'
    # For some reason reverse cannot be used to define the success_url. For example the following line raises an error.
    # e.g. success_url = reverse("projects:mlp:mlp_upload_confirmation")
    success_url = '/projects/mlp/confirmation/'  # but this does work.

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # TODO parse the kml file more smartly to locate the first placemark and work from there.
        # TODO ingest kmz and kml. See the zipfile python library
        kml_file_upload = self.request.FILES['kmlfileUpload']  # get a handle on the file

        kml_file_upload_name = self.request.FILES['kmlfileUpload'].name  # get the file name
        # kml_file_name = kml_file_upload_name[:kml_file_upload_name.rfind('.')]  # get the file name no extension
        kml_file_extension = kml_file_upload_name[kml_file_upload_name.rfind('.')+1:]  # get the file extension

        kml_file_path = os.path.join(settings.MEDIA_ROOT)

        # Define a routine for importing Placemarks from a list of placemark elements
        def import_placemarks(kml_placemark_list):
            feature_count = 0

            for o in kml_placemark_list:

                # Check to make sure that the object is a Placemark, filter out folder objects
                if type(o) is Placemark:

                    table = etree.fromstring(o.description)
                    attributes = table.xpath("//text()")
                    # TODO test attributes is even length
                    attributes_dict = dict(list(zip(attributes[0::2], attributes[1::2])))

                    mlp_occ = Occurrence()

                    ###################
                    # REQUIRED FIELDS #
                    ###################

                    # Validate Basis of Record
                    if attributes_dict.get("Basis Of Record") in ("Fossil", "FossilSpecimen", "Collection"):
                        mlp_occ.basis_of_record = "FossilSpecimen"
                    elif attributes_dict.get("Basis Of Record") in ("Observation", "HumanObservation"):
                        mlp_occ.basis_of_record = "HumanObservation"

                    # Validate Item Type
                    item_type = attributes_dict.get("Item Type")
                    if item_type in ("Artifact", "Artifactual", "Archeology", "Archaeological"):
                        mlp_occ.item_type = "Artifactual"
                    elif item_type in ("Faunal", "Fauna"):
                        mlp_occ.item_type = "Faunal"
                    elif item_type in ("Floral", "Flora"):
                        mlp_occ.item_type = "Floral"
                    elif item_type in ("Geological", "Geology"):
                        mlp_occ.item_type = "Geological"

                    # Field Number
                    try:
                        # parse the field number
                        mlp_occ.field_number = datetime.strptime(attributes_dict.get("Time"), "%b %d, %Y, %I:%M %p")
                        mlp_occ.year_collected = mlp_occ.field_number.year  # set the year collected form field number
                    except ValueError:
                        # If there's a problem getting the fieldnumber, use the current date time and set the
                        # problem flag to True.
                        mlp_occ.field_number = datetime.now()
                        mlp_occ.problem = True
                        try:
                            error_string = "Upload error, missing field number, using current date and time instead."
                            mlp_occ.problem_comment = mlp_occ.problem_comment + " " + error_string
                        except TypeError:
                            mlp_occ.problem_comment = error_string

                    # Process point, comes in as well known text string
                    # Assuming point is in GCS WGS84 datum = SRID 4326
                    pnt = GEOSGeometry("POINT (" + str(o.geometry.x) + " " + str(o.geometry.y) + ")", 4326)  # WKT
                    mlp_occ.geom = pnt

                    #######################
                    # NON-REQUIRED FIELDS #
                    #######################
                    mlp_occ.barcode = attributes_dict.get("Barcode")
                    mlp_occ.item_number = mlp_occ.barcode
                    mlp_occ.catalog_number = "MLP-" + str(mlp_occ.item_number)
                    mlp_occ.remarks = attributes_dict.get("Remarks")
                    mlp_occ.item_scientific_name = attributes_dict.get("Scientific Name")
                    mlp_occ.item_description = attributes_dict.get("Description")

                    # Validate Collecting Method
                    collection_method = attributes_dict.get("Collection Method")
                    if collection_method in ("Surface Standard", "Standard"):
                        mlp_occ.collecting_method = "Surface Standard"
                    elif collection_method in ("Surface Intensive", "Intensive"):
                        mlp_occ.collecting_method = "Surface Intensive"
                    elif collection_method in ("Surface Complete", "Complete"):
                        mlp_occ.collecting_method = "Surface Complete"
                    elif collection_method in ("Exploratory Survey", "Exploratory"):
                        mlp_occ.collecting_method = "Exploratory Survey"
                    elif collection_method in ("Dry Screen 5mm", "Dry Screen 5 Mm", "Dry Screen 5 mm"):
                        mlp_occ.collecting_method = "Dry Screen 5mm"
                    elif collection_method in ("Dry Screen 2mm", "Dry Screen 2 Mm", "Dry Screen 2 mm"):
                        mlp_occ.collecting_method = "Dry Screen 2mm"
                    elif collection_method in ("Dry Screen 1mm", "Dry Screen 1 Mm", "Dry Screen 1 mm"):
                        mlp_occ.collecting_method = "Dry Screen 1mm"
                    # else:
                    #     mlp_occ.collecting_method = None
                    #     mlp_occ.problem = True
                    #     mlp_occ.problem_comment = mlp_occ.problem_comment + " problem importing collecting method"

                    mlp_occ.collecting_method = attributes_dict.get("Collection Method")
                    mlp_occ.collector = attributes_dict.get("Collector")
                    mlp_occ.individual_count = attributes_dict.get("Count")

                    if attributes_dict.get("In Situ") in ('No', "NO", 'no'):
                        mlp_occ.in_situ = False
                    elif attributes_dict.get("In Situ") in ('Yes', "YES", 'yes'):
                        mlp_occ.in_situ = True

                    ##############
                    # Save Image #
                    ##############
                    image_file = ""
                    image_added = False
                    # Now look for images if this is a KMZ
                    if kml_file_extension.lower() == "kmz":
                        # grab image names from XML
                        image_tags = table.xpath("//img/@src")
                        # grab the name of the first image
                        try:
                            image_tag = image_tags[0]
                            # grab the file info from the zip list
                            for file_info in kmz_file.filelist:
                                if image_tag == file_info.orig_filename:
                                    # grab the image file itself
                                    image_file = kmz_file.extract(file_info, "media/uploads/images/mlp")
                                    image_added = True
                                    break
                        except IndexError:
                            pass

                    mlp_occ.save()
                    # need to save record before adding image in order to obtain the DB ID
                    if image_added:
                        # strip off the file name from the path
                        image_path = image_file[:image_file.rfind(os.sep)]
                        # construct new file name
                        new_file_name = image_path + os.sep + str(mlp_occ.id) + "_" + image_tag
                        # rename extracted file with DB record ID
                        os.rename(image_file, new_file_name)
                        # need to strip off "media" folder from relative path saved to DB
                        mlp_occ.image = new_file_name[new_file_name.find(os.sep)+1:]
                        mlp_occ.save()
                    feature_count += 1

                elif type(o) is not Placemark:
                    raise IOError("KML File is badly formatted")

        kml_file = kml.KML()
        if kml_file_extension == "kmz":
            kmz_file = ZipFile(kml_file_upload, 'r')
            kml_document = kmz_file.open('doc.kml', 'r').read()
        else:
            # read() loads entire file as one string
            kml_document = open(kml_file_path + "/" + kml_file_upload_name, 'r').read()

        kml_file.from_string(kml_document)  # pass contents of kml string to kml document instance for parsing

        # get the top level features object (this is essentially the layers list)
        level1_elements = list(kml_file.features())

        # Check that the kml file is well-formed with a single document element.
        if len(level1_elements) == 1 and type(level1_elements[0]) == Document:
            document = level1_elements[0]

            #  If well-formed document, check if the file has folders, which correspond to layers
            level2_elements = list(document.features())
            if len(level2_elements) == 1 and type(level2_elements[0]) == Folder:
                folder = level2_elements[0]

                #  If a single folder is present import placemarks from that folder
                #  Get features from the folder
                level3_elements = list(folder.features())
                #  Check that the features are Placemarks. If they are, import them
                if len(level3_elements) >= 1 and type(level3_elements[0]) == Placemark:
                    placemark_list = level3_elements
                    import_placemarks(placemark_list)

            elif len(level2_elements) >= 1 and type(level2_elements[0]) == Placemark:
                placemark_list = level2_elements
                import_placemarks(placemark_list)

        return super(UploadKMLView, self).form_valid(form)


class Confirmation(generic.ListView):
    template_name = 'projects/confirmation.html'
    model = Occurrence


# class UploadShapefileView(generic.FormView):
#     template_name = 'projects/upload_shapefile.html'
#     form_class = UploadForm
#     context_object_name = 'upload'
#     success_url = 'confirmation'
#
#     def form_valid(self, form):
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
#         shapefileProper = self.request.FILES['shapefileUpload']
#         shapefileIndex = self.request.FILES['shapefileIndexUpload']
#         shapefileData = self.request.FILES['shapefileDataUpload']
#         shapefileProperName = self.request.FILES['shapefileUpload'].name
#         shapefileIndexName = self.request.FILES['shapefileIndexUpload'].name
#         shapefileDataName = self.request.FILES['shapefileDataUpload'].name
#         shapefileProperSaved = default_storage.save(shapefileProperName, ContentFile(shapefileProper.read()))
#         shapefileIndexSaved = default_storage.save(shapefileIndexName, ContentFile(shapefileIndex.read()))
#         shapefileDataSaved = default_storage.save(shapefileDataName, ContentFile(shapefileData.read()))
#         shapefilePath = os.path.join(settings.MEDIA_ROOT)
#         shapefileName = shapefileProperName[:shapefileProperName.rfind('.')]
#         sf = shapefile.Reader(shapefilePath + "\\" + shapefileName)
#
#         shapes = sf.shapes()
#         return super(UploadShapefileView, self).form_valid(form)


def change_coordinates_view(request):
    if request.method == "POST":
        form = ChangeXYForm(request.POST)
        if form.is_valid():
            obs = Occurrence.objects.get(pk=request.POST["DB_id"])
            coordinates = utm.to_latlon(float(request.POST["new_easting"]),
                                        float(request.POST["new_northing"]), 37, "N")
            pnt = GEOSGeometry("POINT (" + str(coordinates[1]) + " " + str(coordinates[0]) + ")", 4326)  # WKT
            obs.geom = pnt
            obs.save()
            messages.add_message(request, messages.INFO,
                                 'Successfully Updated Coordinates For %s.' % obs.catalog_number)
            return redirect("/admin/mlp/occurrence")
    else:
        selected = list(request.GET.get("ids", "").split(","))
        if len(selected) > 1:
            messages.error(request, "You can't change the coordinates of multiple points at once.")
            return redirect("/admin/mlp/occurrence")
        selected_object = Occurrence.objects.get(pk=int(selected[0]))
        initial_data = {"DB_id": selected_object.id,
                        "barcode": selected_object.barcode,
                        "old_easting": selected_object.easting,
                        "old_northing": selected_object.northing,
                        "item_scientific_name": selected_object.item_scientific_name,
                        "item_description": selected_object.item_description
                        }
        the_form = ChangeXYForm(initial=initial_data)
        return render_to_response('projects/changeXY.html', {"theForm": the_form}, RequestContext(request))


def occurrence2biology_view(request):
    if request.method == "POST":
        form = Occurrence2Biology(request.POST)
        if form.is_valid():
            occurrence_object = Occurrence.objects.get(barcode__exact=request.POST["barcode"])
            if occurrence_object.item_type in ('Faunal', 'Floral'):
                taxon = Taxon.objects.get(pk=request.POST["taxon"])
                id_qual = IdentificationQualifier.objects.get(pk=request.POST["identification_qualifier"])
                new_biology = Biology(barcode=occurrence_object.barcode,
                                      item_type=occurrence_object.item_type,
                                      basis_of_record=occurrence_object.basis_of_record,
                                      collecting_method=occurrence_object.collecting_method,
                                      field_number=occurrence_object.field_number,
                                      taxon=taxon,
                                      identification_qualifier=id_qual,
                                      geom=occurrence_object.geom
                                      )
                for key in list(occurrence_object.__dict__.keys()):
                    new_biology.__dict__[key] = occurrence_object.__dict__[key]

                occurrence_object.delete()
                new_biology.save()
                messages.add_message(request, messages.INFO,
                                     'Successfully converted occurrence to biology.')
            else:
                pass
                messages.error(request, "Can only convert items of type Faunal or Floral")
            return redirect("/admin/mlp/occurrence")
    else:
        selected = list(request.GET.get("ids", "").split(","))
        if len(selected) > 1:
            messages.add_message(request, messages.INFO, "Do you wish to update all the following occurrences?")
            return redirect("/admin/mlp/occurrence")
        selected_object = Occurrence.objects.get(pk=int(selected[0]))
        initial_data = {
                        "barcode": selected_object.barcode,
                        "catalog_number": selected_object.catalog_number,
                        "basis_of_record": selected_object.basis_of_record,
                        "item_type": selected_object.item_type,
                        "collector": selected_object.collector,
                        "collecting_method": selected_object.collecting_method,
                        "field_number": selected_object.field_number,
                        "year_collected": selected_object.year_collected,
                        "item_scientific_name": selected_object.item_scientific_name,
                        "item_description": selected_object.item_description
                        }
        the_form = Occurrence2Biology(initial=initial_data)
        return render_to_response('projects/occurrence2biology.html', {"theForm": the_form, "initial_data": initial_data}, RequestContext(request))
