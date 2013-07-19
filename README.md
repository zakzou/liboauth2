liboauth2
=========

Light Python wrapper for the OAuth 2.0


Installation
=============

PIP

```sh
pip install liboauth2
```
Easy Install

```sh
easy_install liboauth2
```



Usage
=====================


### Demo for Facebook

```python
# -*- coding: utf-8 -*-


import liboauth2
import urllib
from flask import Flask, redirect, request


CLIENT_ID = 'you client id'
CLIENT_SECRET = 'you client secret'

client = liboauth2.Client(CLIENT_ID, CLIENT_SECRET)


REDIRECT_URI            = 'http://localhost:5000/callback/'
AUTHORIZATION_ENDPOINT  = 'https://graph.facebook.com/oauth/authorize'
TOKEN_ENDPOINT          = 'https://graph.facebook.com/oauth/access_token'


app = Flask(__name__)
app.debug = True


@app.route('/')
def home():
    # get auth url
    url = client.get_auth_url(AUTHORIZATION_ENDPOINT, REDIRECT_URI)
    return redirect(url)


@app.route('/callback/')
def callback():
    # get access token
    params = {'code': request.args['code'], 'redirect_uri': REDIRECT_URI}
    resp = client.get_access_token(TOKEN_ENDPOINT, liboauth2.GRANT_TYPE_AUTH_CODE, params)
    def urldecode(values):
        ret = {}
        for s in values.split('&'):
            if s.find('=') > -1:
                k, v = map(urllib.unquote, s.split('='))
                ret[k] = v
                #ret.setdefault(k, []).append(v)
        return ret
    info = urldecode(resp['result'])
    client.set_access_token(info['access_token'])
    resp = client.fetch('http://graph.facebook.com/me')
    return str(resp)

if __name__ == '__main__':
    app.run(host='localhost', port=5000)

```




#### Demo for Tencent Weibo

```python
# -*- coding: utf-8 -*-


import liboauth2
import urllib
from flask import Flask, redirect, request


CLIENT_ID = 'you client id'
CLIENT_SECRET = 'you client secret'

client = liboauth2.Client(CLIENT_ID, CLIENT_SECRET)


REDIRECT_URI = 'http://localhost:5000/callback/'
AUTH_URI = 'https://open.t.qq.com/cgi-bin/oauth2/authorize'
ACCESS_TOKEN_URL = 'https://open.t.qq.com/cgi-bin/oauth2/access_token'


app = Flask(__name__)
app.debug = True


@app.route('/')
def home():
    # get auth url
    url = client.get_auth_url(AUTH_URI, REDIRECT_URI)
    return redirect(url)


@app.route('/callback/')
def callback():
    # get access token
    params = {'code': request.args['code'], 'redirect_uri': REDIRECT_URI}
    resp = client.get_access_token(ACCESS_TOKEN_URL, liboauth2.GRANT_TYPE_AUTH_CODE, params)
    # print resp
    def urldecode(values):
        ret = {}
        for s in values.split('&'):
            if s.find('=') > -1:
                k, v = map(urllib.unquote, s.split('='))
                ret[k] = v
                #ret.setdefault(k, []).append(v)
        return ret
    data = urldecode(resp['result'])
    # set access token and query user info
    client.set_access_token(data['access_token'])
    params = {
            'oauth_consumer_key': CLIENT_ID,
            'openid': data['openid'],
            'clientip': request.remote_addr,
            'oauth_version': '21',
            }
    resp = client.fetch('http://open.t.qq.com/api/user/info', params)
    return str(resp['result'])


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
```
