import urllib
import urllib2
import json


# utility

def construct_url(url_path, kwargs, base_url='https://api.github.com'):
    return base_url + (url_path + '?access_token=%(access_token)s') % kwargs

def get_text(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

def get_json(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    json_response = json.load(response)
    return json_response

# oauth

def get_access_token(consumer_key, consumer_secret, code):
    data = urllib.urlencode((
            ('client_id', consumer_key),
            ('client_secret', consumer_secret),
            ('code', code)))
    request = urllib2.Request('https://github.com/login/oauth/access_token', data, {'Accept': 'application/json'})
    response = json.load(urllib2.urlopen(request))
    return response['access_token']

# API

def compare(**kwargs):
    return get_json(construct_url('/repos/%(owner)s/%(repo)s/compare/%(base)s...%(head)s', kwargs))

def commit(**kwargs):
    return get_json(construct_url('/repos/%(owner)s/%(repo)s/git/commits/%(sha)s', kwargs))

def tree(**kwargs):
    return get_json(construct_url('/repos/%(owner)s/%(repo)s/git/trees/%(sha)s', kwargs))

def raw(**kwargs):
    return get_text(construct_url('/%(owner)s/%(repo)s/raw/%(sha)s/%(filename)s', kwargs, base_url='https://github.com'))
