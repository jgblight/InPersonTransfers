from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


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
    paid = models.BooleanField()
