import xlwt
from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse
from django.views.generic import TemplateView

from apps.location.forms import ImportForm
from apps.location.models import Address
from apps.location.utils import handle_file_upload, import_address_sheet, \
    get_address, get_headers, setup_workbook


class LocationIndex(TemplateView):
    template_name = "location/list_location.html"

    def get(self, request, *args, **kwargs):
        """Populates the table."""
        queryset = get_address()

        ctx = {
            'queryset': queryset
        }
        return render_to_response(self.template_name, ctx)


class ImportAddress(TemplateView):
    """Import the address from excel sheet."""
    template_name = 'location/import_address.html'

    def get_context_data(self, **kwargs):
        context = ({
            'STATIC_MEDIA_SERVER': settings.STATIC_MEDIA_SERVER,
            'form_name': 'Import Address',
            'form': ImportForm()
        })
        return context

    def post(self, request, *args, **kwargs):
        """Post request to handle file upload."""
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            file_data = request.FILES['import_address']
            upload_status, path, file_name = handle_file_upload(file_data)

            if not upload_status:
                messages.error(request, "Something went wrong during file "
                                        "upload.")
            else:
                import_response = import_address_sheet(
                    request, path, file_name)
                if import_response['status']:
                    messages.success(request, import_response['message'])
                else:
                    messages.error(request, import_response['message'])
        else:
            messages.error(request, 'File did not upload')

        return HttpResponseRedirect(reverse('location_index'))


class ExportAddress(TemplateView):
    """Export the mailing list."""

    def get(self, request, *args, **kwargs):
        counter = 0
        name = 'address-export'
        file_name = "{0}.xls".format(name)

        sheet_name = 'Address Export'
        workbook, worksheet, response = setup_workbook(file_name, sheet_name)

        # get the queryset
        address_data = get_address()

        # populate the headers
        for index, header in enumerate(get_headers()):
            worksheet.write(counter, index, header)
        counter += 1

        # populate the data rows
        for row in address_data:
            worksheet.write(counter, 0, row['address_line_1'])
            worksheet.write(counter, 1, row['address_line_2'])
            worksheet.write(counter, 2, row['latitude'])
            worksheet.write(counter, 3, row['longitude'])
            worksheet.write(counter, 4, row['pincode'])
            worksheet.write(counter, 5, row['city__city'])
            worksheet.write(counter, 6, row['city__state__state'])
            worksheet.write(counter, 7, row['city__state__country__country'])

            counter += 1

        workbook.save(response)

        return response

