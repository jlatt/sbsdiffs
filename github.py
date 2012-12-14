import urllib
import urllib2
import json


# utility

base_url = 'https://api.github.com'


def make_path(path, **kwargs):
    return path % dict(((k, urllib.quote(v)) for (k, v) in kwargs.iteritems()))


def make_query(**kwargs):
    return '?' + urllib.urlencode(kwargs)


class Github(object):
    def __init__(self, owner, repo, access_token):
        self.owner = owner
        self.repo = repo
        self.access_token = access_token


    def compare(self, base, head):
        url = base_url + make_path('/repos/%(owner)s/%(repo)s/compare/%(base)s...%(head)s', owner=self.owner, repo=self.repo, base=base, head=head) + make_query(access_token=self.access_token)
        request = urllib2.Request(url)
        request.add_header('Accept', 'application/json')
        response = urllib2.urlopen(request)
        json_response = json.load(response)
        return json_response


    def contents(self, filename, ref, owner=None):
        if owner is None:
            owner = self.owner
        url = base_url + make_path('/repos/%(owner)s/%(repo)s/contents/%(filename)s', owner=owner, repo=self.repo, filename=filename) + make_query(access_token=self.access_token, ref=ref)
        request = urllib2.Request(url)
        request.add_header('Accept', 'application/vnd.github.v3.raw')
        try:
            response = urllib2.urlopen(request)
            return response.read()
        except urllib2.HTTPError:
            return ''


# oauth


def get_access_token(consumer_key, consumer_secret, code):
    data = urllib.urlencode({'client_id': consumer_key, 'client_secret': consumer_secret, 'code': code})
    headers = {'Accept': 'application/json'}
    request = urllib2.Request('https://github.com/login/oauth/access_token', data, headers)
    response = urllib2.urlopen(request)
    json_response = json.load(response)
    return json_response['access_token']


def authorize_url(client_id):
    return 'https://github.com/login/oauth/authorize?' + urllib.urlencode({'client_id': client_id})
