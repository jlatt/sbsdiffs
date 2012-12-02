#!/usr/bin/env python2.7
import collections
import itertools

import flask

import app_config
import formatter
import github
import udiff


def check_access_token(func):
    def checks_access_token(*args, **kwargs):
        if 'access_token' not in flask.session:
            return flask.redirect(flask.url_for('login', redirect_uri=flask.request.url))
        return func(*args, **kwargs)
    return checks_access_token


# flask
app = flask.Flask(__name__)
app.secret_key = app_config.flask_secret_key


@app.route('/login')
def login():
    redirect_uri = flask.request.args.get('redirect_uri', None)
    if redirect_uri:
        flask.session['redirect_uri'] = redirect_uri
    return flask.redirect(github.authorize_url(app_config.consumer_key))


@app.route('/oauth/authorize')
def oauth_authorize():
    code = flask.request.args.get('code', None)
    if not code:
        return flask.abort(403)

    access_token = github.get_access_token(app_config.consumer_key, app_config.consumer_secret, code)
    flask.session['access_token'] = access_token

    redirect_uri = flask.session.pop('redirect_uri', None)
    if not (redirect_uri and redirect_uri.startswith(flask.request.url_root)):
        redirect_uri = flask.url_for('root')
    return flask.redirect(redirect_uri)


@check_access_token
@app.route('/')
def root():
    return 'authorized. try a url.'


@check_access_token
@app.route('/<owner>/<repo>/<base>/<head>/')
def compare(owner, repo, base, head):
    response = github.compare(owner=owner, repo=repo, base=base, head=head, access_token=flask.session['access_token'])
    return flask.render_template(
        'index.html',
        files=response['files'],
        compare=response)


@check_access_token
@app.route('/<owner>/<repo>/<base>/<head>/<path:filename>')
def compare_file(owner, repo, base, head, filename):
    access_token = flask.session['access_token']
    response = github.compare(owner=owner, repo=repo, base=base, head=head, access_token=access_token)
    file_data = itertools.ifilter(lambda f: f['filename'] == filename, response['files']).next()
    base_data, head_data = udiff.parse_patch(file_data['patch'])
    base_lines = github.raw(owner=owner, repo=repo, sha=response['merge_base_commit']['sha'], filename=filename, access_token=access_token)
    head_lines = github.raw(owner=owner, repo=repo, sha=head, filename=filename, access_token=access_token)

    # render
    return flask.render_template(
        'diff.html',
        filename=filename,
        base_html=formatter.format_code(filename, base_lines, lambda ln: 'del' if ln in base_data else 'reg'),
        head_html=formatter.format_code(filename, head_lines, lambda ln: 'add' if ln in head_data else 'reg'),
        compare=response)


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', 5000))
    debug = port == 5000
    app.run(host='0.0.0.0', port=port, debug=debug)
