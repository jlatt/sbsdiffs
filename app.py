#!/usr/bin/env python2.7
import collections
import itertools

import flask

import app_config
import formatter
import github
import udiff


# flask
app = flask.Flask(__name__)


@app.route('/login')
def login():
    return flask.redirect('https://github.com/login/oauth/authorize?client_id=%s' % app_config.consumer_key)


@app.route('/oauth/authorize')
def oauth_authorize():
    code = flask.request.args.get('code', None)
    access_token = github.get_access_token(app_config.consumer_key, app_config.consumer_secret, code)
    response = flask.redirect(flask.url_for('root'))
    response.set_cookie('access_token', access_token)
    return response


@app.route('/')
def root():
    return ''


@app.route('/<owner>/<repo>/<base>/<head>/')
def compare(owner, repo, base, head):
    access_token = flask.request.cookies['access_token']
    response = github.compare(owner=owner, repo=repo, base=base, head=head, access_token=access_token)
    return flask.render_template(
        'index.html',
        files=response['files'],
        compare=response)


@app.route('/<owner>/<repo>/<base>/<head>/<path:filename>')
def compare_file(owner, repo, base, head, filename):
    access_token = flask.request.cookies['access_token']
    response = github.compare(owner=owner, repo=repo, base=base, head=head, access_token=access_token)
    file_data = itertools.ifilter(lambda f: f['filename'] == filename, response['files']).next()
    base_data, head_data = udiff.parse_patch(file_data['patch'])
    base_lines = github.raw(owner=owner, repo=repo, sha=base, filename=filename, access_token=access_token)
    head_lines = github.raw(owner=owner, repo=repo, sha=head, filename=filename, access_token=access_token)

    # render
    return flask.render_template(
        'diff.html',
        filename=filename,
        base_html=formatter.format_code(filename, base_lines, lambda ln: 'del' if ln in base_data else 'reg'),
        head_html=formatter.format_code(filename, head_lines, lambda ln: 'add' if ln in head_data else 'reg'))


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
