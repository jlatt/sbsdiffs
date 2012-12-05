Side-by-Side Diffs for Github
-------------------------------

sbsdiffs is a flask app that is easily deployed to heroku. A reference app runs at [diff.jlatt.com](http://diff.jlatt.com/).

Deploying
---------

- Register a new application on [Github](https://github.com/settings/applications/new) to get an oauth consumer key and secret.
- Create a new application on [Heroku](https://devcenter.heroku.com/articles/python).
- Generate a key for [Flask](http://flask.pocoo.org/) sessions in python:

```python
>>> import os
>>> os.urandom(24).encode('base64').strip()
```

- Set the following environment variables:

```sh
GITHUB_CONSUMER_KEY='.........'
GITHUB_CONSUMER_SECRET='..........'
FLASK_SESSION_KEY='......'
```

- Push to heroku:

```sh
$ git push heroku master
```
