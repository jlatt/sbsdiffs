#!/usr/bin/env python2.7
import collections
import itertools
import os

import flask

import formatter
import github
import udiff


# flask
app = flask.Flask(__name__)
app.secret_key = os.environ['FLASK_SESSION_KEY']

github_consumer_key = os.environ['GITHUB_CONSUMER_KEY']
github_consumer_secret = os.environ['GITHUB_CONSUMER_SECRET']


@app.route('/login')
def login():
    redirect_uri = flask.request.args.get('redirect_uri', None)
    if redirect_uri and redirect_uri.startswith(flask.request.url_root):
        flask.session['redirect_uri'] = redirect_uri
    return flask.redirect(github.authorize_url(github_consumer_key))


@app.route('/oauth/authorize')
def oauth_authorize():
    code = flask.request.args.get('code', None)
    if not code:
        return flask.abort(403)

    access_token = github.get_access_token(github_consumer_key, github_consumer_secret, code)
    flask.session['access_token'] = access_token

    redirect_uri = flask.session.pop('redirect_uri', None)
    if not (redirect_uri and redirect_uri.startswith(flask.request.url_root)):
        redirect_uri = flask.url_for('root')
    return flask.redirect(redirect_uri)


@app.route('/')
def root():
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login', redirect_uri=flask.request.url))
    return flask.render_template(
        'root.html',
        url_example=flask.url_for('compare', owner='owner', repo='repo', base='from_commitish', head='to_commitish')
        )


@app.route('/<owner>/<repo>')
def compare(owner, repo):
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login', redirect_uri=flask.request.url))

    base = flask.request.args['base']
    head = flask.request.args['head']

    gh = github.Github(owner, repo, access_token=flask.session['access_token'])
    response = gh.compare(base, head)

    files = [dict(
            text=fdata['filename'],
            href=flask.url_for('compare_file', owner=owner, repo=repo, filename=fdata['filename'], base=base, head=head),
            changes=fdata['changes'],
            additions=fdata['additions'],
            deletions=fdata['deletions'],
            ) for fdata in response['files'] if 'patch' in fdata]
    return flask.render_template(
        'index.html',
        owner=owner,
        repo=repo,
        base=base,
        head=head,
        files=files,
        compare=response)


def parse_owner(ref, owner):
    if ref.find(':') != -1:
        return tuple(reversed(ref.split(':', 1)))
    return ref, owner


@app.route('/<owner>/<repo>/<path:filename>')
def compare_file(owner, repo, filename):
    if 'access_token' not in flask.session:
        return flask.redirect(flask.url_for('login', redirect_uri=flask.request.url))

    base = flask.request.args['base']
    head = flask.request.args['head']
    gh = github.Github(owner, repo, flask.session['access_token'])

    response = gh.compare(base, head)
    file_data = itertools.ifilter(lambda f: f['filename'] == filename, response['files']).next()

    base_data, head_data, base_alt, head_alt = udiff.parse_patch(file_data['patch'])
    head, head_owner = parse_owner(head, owner)

    base_contents = gh.contents(filename, response['merge_base_commit']['sha'])
    head_contents = gh.contents(filename, head)

    return flask.render_template(
        'diff.html',
        owner=owner,
        repo=repo,
        base=base,
        head=head,
        filename=filename,
        base_html=formatter.format_code(filename, base_contents, base_data, base_alt),
        head_html=formatter.format_code(filename, head_contents, head_data, head_alt),
        compare_url=flask.url_for('compare', owner=owner, repo=repo, base=base, head=head),
        compare=response,
        patch=file_data['patch'])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = port == 5000
    app.run(host='0.0.0.0', port=port, debug=debug)
