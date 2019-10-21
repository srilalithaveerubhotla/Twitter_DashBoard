import requests
from requests_oauthlib import OAuth1, OAuth1Session
from .exceptions import TwitterException


class API:
    _consumer_key = None
    _consumer_secret = None
    _access_token = None
    _access_token_secret = None
    _auth = None
    _api_base_url = 'https://api.twitter.com/1.1/'
    _request_token_url = 'https://api.twitter.com/oauth/request_token'
    _authorization_url = 'https://api.twitter.com/oauth/authorize'
    _access_token_url = 'https://api.twitter.com/oauth/access_token'

    def __init__(self, consumer_key, consumer_secret, access_token=None, access_token_secret=None):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

    def get_authorization_url(self, callback):
        oauth = OAuth1Session(self._consumer_key, client_secret=self._consumer_secret, callback_uri=callback)
        oauth.fetch_request_token(self._request_token_url)
        return oauth.authorization_url(self._authorization_url)

    def get_access_token(self, oauth_token, oauth_verifier):
        oauth = OAuth1Session(
            self._consumer_key, client_secret=self._consumer_secret, resource_owner_key=oauth_token,
            verifier=oauth_verifier
        )

        token = oauth.fetch_access_token(self._access_token_url)
        self.set_access_token(token['oauth_token'], token['oauth_token_secret'])
        return token

    def set_access_token(self, access_token, access_token_secret):
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._auth = OAuth1(self._consumer_key, self._consumer_secret, access_token, access_token_secret)

    def get(self, endpoint, **kwargs):
        return self.request('get', endpoint, params=kwargs)

    def post(self, endpoint, **kwargs):
        return self.request('post', endpoint, data=kwargs)

    def request(self, method, endpoint, **kwargs):
        url = self._api_base_url + endpoint + '.json' if 'url' not in kwargs else kwargs['url']
        response = getattr(requests, method)(url, auth=self._auth, **kwargs)

        if response.status_code < 200 or response.status_code > 299:
            raise TwitterException(response.status_code, response.json())

        return response.json()
