from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.http import quote_plus

from geopy.geocoders import Nominatim

import json
from twython import Twython


class TwitterProfile(models.Model):

    """
        An example Profile model that handles storing the oauth_token and
        oauth_secret in relation to a user. Adapt this if you have a current
        setup, there's really nothing special going on here.
    """
    user = models.OneToOneField(User)
    handle = models.CharField(max_length=200, null=True)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)


class PaymentRequest(models.Model):
    requester = models.ForeignKey(User, related_name="requests_made")
    requestee = models.ForeignKey(User, related_name="requests_owed")
    amount = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    paid = models.BooleanField(default=False)

    @property
    def uber_link(self):
        geolocator = Nominatim()
        location = geolocator.reverse("{}, {}".format(self.latitude, self.longitude))
        formatted_address = quote_plus(location.address)
        return "uber://action=setPickup&client_id=RXjda_RLc1B5KhzoOB9nDnkaGJOkJAmv&pickup=my_location&dropoff[latitude]={}&dropoff[longitude]={}&dropoff[formatted_address]={}&dropoff[nickname]=Your%20Friend&product_id=a1111c8c-c720-46c3-8534-2fcdd730040d".format(self.latitude, self.longitude, formatted_address)

    def to_json(self):
        return {
            "id": self.id,
            "requester": self.requester.username,
            "requestee": self.requestee.username,
            "amount": self.amount,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "paid": self.paid,
            "uber_link": self.uber_link
        }

    def send_tweet(self):
        request_url = "http://inpersontransfers.herokuapp.com/requests/{}/".format(self.id)
        twitter = Twython(
            settings.TWITTER_KEY,
            settings.TWITTER_SECRET,
            self.requester.twitterprofile.oauth_token,
            self.requester.twitterprofile.oauth_secret)
        status = ".@{}, you owe me ${}. Pay me back at {}".format(self.requestee.username, self.amount, request_url)
        twitter.update_status(status=status)

    @classmethod
    def from_json(self, **data):
        data['requester'] = User.objects.get(username=data["requester"])
        data['requestee'] = User.objects.get(username=data["requestee"])
        pr = PaymentRequest.objects.create(**data)
        pr.send_tweet()
        return pr
