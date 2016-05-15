from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transfers.models import TwitterProfile, PaymentRequest

from twython import Twython

import json


def main(request):
    if request.user.is_authenticated():
        return HttpResponse("You are logged in")
    else:
        return HttpResponse("<a href='/login'>Log in with Twitter</a>")


def logout(request, redirect_url=settings.LOGOUT_REDIRECT_URL):
    """
        Nothing hilariously hidden here, logs a user out. Strip this out if your
        application already has hooks to handle this.
    """
    django_logout(request)
    return HttpResponseRedirect(request.build_absolute_uri(redirect_url))


def begin_auth(request):
    """The view function that initiates the entire handshake.
    For the most part, this is 100% drag and drop.
    """
    # Instantiate Twython with the first leg of our trip.
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET)

    # Request an authorization url to send the user to...
    callback_url = request.build_absolute_uri(
        reverse('transfers.views.thanks'))
    auth_props = twitter.get_authentication_tokens(callback_url)

    # Then send them over there, durh.
    request.session['request_token'] = auth_props

    request.session['next_url'] = request.GET.get('next', None)

    return HttpResponseRedirect(auth_props['auth_url'])


def thanks(request, redirect_url=None):
    """A user gets redirected here after hitting Twitter and authorizing your app to use their data.
    This is the view that stores the tokens you want
    for querying data. Pay attention to this.
    """
    # Now that we've got the magic tokens back from Twitter, we need to exchange
    # for permanent ones and store them...
    oauth_token = request.session['request_token']['oauth_token']
    oauth_token_secret = request.session['request_token']['oauth_token_secret']
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                      oauth_token, oauth_token_secret)

    # Retrieve the tokens we want...
    authorized_tokens = twitter.get_authorized_tokens(
        request.GET['oauth_verifier'])

    # If they already exist, grab them, login and redirect to a page
    # displaying stuff.
    try:
        user = User.objects.get(username=authorized_tokens['screen_name'])
    except User.DoesNotExist:
        # We mock a creation here; no email, password is just the token, etc.
        user = User.objects.create_user(authorized_tokens[
                                        'screen_name'], "fjdsfn@jfndjfn.com", authorized_tokens['oauth_token_secret'])
        profile = TwitterProfile()
        profile.user = user
        profile.oauth_token = authorized_tokens['oauth_token']
        profile.oauth_secret = authorized_tokens['oauth_token_secret']
        profile.save()

    user = authenticate(
        username=authorized_tokens['screen_name'],
        password=authorized_tokens['oauth_token_secret']
    )
    login(request, user)
    redirect_url = request.session.get('next_url', redirect_url)

    return HttpResponseRedirect(redirect_url or settings.LOGIN_REDIRECT_URL)


class UnsafeSessionAuthentication(SessionAuthentication):

    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, 'user', None)

        if not user or not user.is_active:
           return None

        return (user, None)


class PaymentRequestViewSet(viewsets.ViewSet):

    authentication_classes = (UnsafeSessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        """ GET request to http://inpersontransfers.herokuapp.com/requests/{id}/
            sample data:
                {"requester":"jenblight",
                 "requestee":"twitterhandle",
                 "amount":12,
                 "latitude":37.7607947,
                 "longitude":-122.4206304,17,
                 "uber_link":"uber://action=setPickup&..."}
        """
        return Response(PaymentRequest.objects.get(id=pk).to_json())

    def create(self, request):
        """ POST request to http://inpersontransfers.herokuapp.com/requests/
            sample data:
                {"requestee":"twitterhandle",
                 "amount":12,
                 "latitude":37.7607947,
                 "longitude":-122.4206304,17}
        """

        data = request.data
        if '_content' in data:
            data = json.loads(data['_content'])
        if 'requester' not in data:
            data['requester'] = request.user.username
        pr = PaymentRequest.from_json(**data)
        return Response(pr.to_json())
