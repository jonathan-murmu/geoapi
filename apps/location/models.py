import googlemaps
from django.conf import settings
from django.db import models


class Country(models.Model):
    """Model to store the country details."""
    country = models.CharField(max_length=255)


class State(models.Model):
    """Model to store the state details."""
    state = models.CharField(max_length=255)
    country = models.ForeignKey(Country, null=True, blank=True,
                                on_delete=models.SET_NULL)


class City(models.Model):
    """Model to store the city details."""
    city = models.CharField(max_length=255)
    state = models.ForeignKey(State, null=True, blank=True,
                              on_delete=models.SET_NULL)


class Address(models.Model):
    """Model to store the address."""
    address_line_1 = models.TextField(null=True, blank=True)
    address_line_2 = models.TextField(null=True, blank=True)
    pincode = models.PositiveIntegerField()

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    city = models.ForeignKey(City, null=True, blank=True,
                             on_delete=models.SET_NULL)

    # def save(self, domain='maps.google.com.my', *args, **kwargs):
    #     location = self.address_line_1 + self.address_line_2 or '' + str(self.pincode) +
    #     gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)
    #
    #     if location:
    #         if not self.latitude or not self.longitude:
    #             try:
    #                 geocode_result = gmaps.geocode(''
    #                 # g = geocoders.GoogleV3(domain=domain)
    #                 # self.place, (self.latitude, self.longitude) = g.geocode(
    #                 #     location)
    #             except Exception as e:
    #                 print(e)
    #
    #     super(Address, self).save(*args, **kwargs)