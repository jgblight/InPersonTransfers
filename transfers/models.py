from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import json


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
        return "uber://action=setPickup&client_id=RXjda_RLc1B5KhzoOB9nDnkaGJOkJAmv&dropoff[latitude]={}[longitude]={}&dropoff[nickname]=Your%20Friend&product_id=a1111c8c-c720-46c3-8534-2fcdd730040d".format(self.latitude, self.longitude)

    def to_json(self):
        return json.dumps({
            "requester": "@{}".format(self.requester.username),
            "requestee": "@{}".format(self.requester.username),
            "amount": self.amount,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "paid": self.paid,
            "uber_link": self.uber_link
        })

    @classmethod
    def from_json(self, **data):
        data['requester'] = User.objects.get(username=data["requester"])
        data['requestee'] = User.objects.get(username=data["requestee"])
        return PaymentRequest.objects.create(**data)
