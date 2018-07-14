from django.urls import path

from apps.location.views import LocationIndex, ImportAddress, ExportAddress

urlpatterns = [
    path('', LocationIndex.as_view(), name='location_index'),
    path('import/', ImportAddress.as_view(), name='import_address'),
    path('export/', ExportAddress.as_view(), name='export_address'),
]
