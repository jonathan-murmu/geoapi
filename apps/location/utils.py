import os

import googlemaps
import xlrd
import xlwt
from django.conf import settings
from django.http import HttpResponse

from apps.location.models import Country, State, City, Address


def handle_file_upload(file_data):
    file_name = file_data.name
    path = settings.MEDIA_ROOT + 'uploads/address_files/'
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + file_name, 'wb+') as destination:
            for chunk in file_data.chunks():
                destination.write(chunk)
    except Exception as e:
        return False
    else:
        return True, path, file_name


def cell_value(sheet, row_index, column_index):
    """Returns the cell value of the excel sheet."""
    try:
        if sheet.cell_type(row_index, column_index) == 2:  # 2 for float values
            # when its pure float number.
            return str(int(sheet.cell(row_index, column_index).value or ''))
        elif sheet.cell_type(row_index, column_index) == 1:  # 1 for unicode
            return str(sheet.cell(row_index, column_index).value or '')
        else:
            return str(sheet.cell(row_index, column_index).value or '')
    except:
        return ''


def import_address_sheet(request, path, file_name):
    """Import the sheet data into the database."""
    response = {'status': False, 'message': 'File did not upload'}

    upload_file_path = path + file_name
    book = xlrd.open_workbook(upload_file_path)
    sheet = book.sheet_by_index(0)
    for row_index in range(sheet.nrows):
        if row_index > 0:
            data = {}
            address_1 = cell_value(sheet, row_index, 0)
            address_2 = cell_value(sheet, row_index, 1)
            pin_code = cell_value(sheet, row_index, 2)
            city = cell_value(sheet, row_index, 3)
            state = cell_value(sheet, row_index, 4)
            country = cell_value(sheet, row_index, 5)

            country_obj, created = Country.objects.get_or_create(
                country=country.lower())

            state_obj, created = State.objects.get_or_create(
                state=state.lower(), country=country_obj
            )

            city_obj, created = City.objects.get_or_create(
                city=city.lower(), state=state_obj
            )

            data['address_line_1'] = address_1
            data['address_line_2'] = address_2
            data['pincode'] = pin_code
            data['city'] = city_obj

            location = ' '.join([address_1, address_2, pin_code, city, state,
                                 country])

            latitude, longitude = get_lat_long(location)
            data['latitude'] = latitude
            data['longitude'] = longitude

            Address.objects.get_or_create(**data)

            response['status'] = True
            response['message'] = "Successfully uploaded."

    return response


def get_address():
    return Address.objects.values(
        'address_line_1', 'address_line_2', 'pincode', 'latitude', 'longitude',
        'city__city', 'city__state__state', 'city__state__country__country')


def get_headers():
    return [
        "Address Line 1", "Address Line 2", "Latitude", "Longitude", "Pin Code",
        "City", "State", "Country"
    ]


def setup_workbook(file_name,sheet_name):
    # Setting up the response header
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % (
        file_name)

    # Initialing the spreadsheet
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet(sheet_name)

    return workbook, worksheet, response


def get_lat_long(location):
    """Calls the google maps api to get the latitude - longitude."""
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)
    geocode_result = gmaps.geocode(location)
    return geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng']



