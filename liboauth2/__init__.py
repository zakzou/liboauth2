# -*- coding: utf-8 -*-

'''
Note : Code is released under the MIT
'''

import base
import pycurl
import StringIO
import hmac

from os import path
from uuid import uuid4
from time import time
from urlparse import urlparse
from base64 import b64encode
from urllib import urlencode


__version__ = '0.0.3'


# Different AUTH method
AUTH_TYPE_URI                 = 0
AUTH_TYPE_AUTHORIZATION_BASIC = 1
AUTH_TYPE_FORM                = 2


# Different Access token type
ACCESS_TOKEN_URI      = 0
ACCESS_TOKEN_BEARER   = 1
ACCESS_TOKEN_OAUTH    = 2
ACCESS_TOKEN_MAC      = 3


# Different Grant types
GRANT_TYPE_AUTH_CODE          = 'authorization_code'
GRANT_TYPE_PASSWORD           = 'password'
GRANT_TYPE_CLIENT_CREDENTIALS = 'client_credentials'
GRANT_TYPE_REFRESH_TOKEN      = 'refresh_token'


# HTTP Methods
HTTP_METHOD_GET    = 'GET'
HTTP_METHOD_POST   = 'POST'
HTTP_METHOD_PUT    = 'PUT'
HTTP_METHOD_DELETE = 'DELETE'
HTTP_METHOD_HEAD   = 'HEAD'
HTTP_METHOD_PATCH   = 'PATCH'


# HTTP Form content types
HTTP_FORM_CONTENT_TYPE_APPLICATION = 0
HTTP_FORM_CONTENT_TYPE_MULTIPART = 1


class Client(object):
    '''
    Light Python wrapper for the OAuth 2.0 protocol.

    This client is based on the OAuth2 specification draft v2.15
    http://tools.ietf.org/html/draft-ietf-oauth-v2-15
    '''

    def __init__(self, client_id, client_secret, client_auth=AUTH_TYPE_URI, certificate_file=None, **kwargs):
        if certificate_file:
            if not path.isfile(certificate_file):
                raise base.ArgumentError('The certificate file was not found')
        self.client_id      = client_id
        self.client_secret  = client_secret
        self.client_auth    = client_auth
        self.certificate_file = certificate_file
        self.access_token_type = AUTH_TYPE_URI
        self.access_token_secret = None
        self.access_token_algorithm = None
        self.access_token = None
        self.access_token_param_name = 'access_token'
        self.curl_options = {}

    def get_auth_url(self, auth_edupoint, redirect_uri, **extra_parameters):
        parameters = dict(response_type='code', client_id=self.client_id, redirect_uri=redirect_uri)
        parameters.update(extra_parameters)
        return '%s?%s' % (auth_edupoint, urlencode(parameters))

    def get_access_token(self, token_endpoint, grant_type, parameters):
        className = self._covert_to_camel_case(grant_type)
        cls = getattr(base, className)
        grant_obj = cls()
        grant_obj.validate_parameters(parameters)

        parameters['grant_type'] = cls.GRANT_TYPE
        http_headers = {}
        if self.client_auth in (AUTH_TYPE_URI, AUTH_TYPE_FORM):
            parameters['client_id'] = self.client_id
            parameters['client_secret'] = self.client_secret
        elif self.client_auth == AUTH_TYPE_AUTHORIZATION_BASIC:
            parameters['client_id'] = self.client_id
            auth_str = 'Basic %s' % b64encode('%s:%s' % (self.client_id, self.client_secret))
            http_headers['Authorization'] = auth_str
        else:
            raise base.ArgumentError('Unknow client auth type.')
        return self._exec_request(token_endpoint, parameters, HTTP_METHOD_POST, http_headers, HTTP_FORM_CONTENT_TYPE_APPLICATION)

    def set_curl_option(self, option, value):
        self.curl_options[option] = value

    def set_curl_options(self, options):
        self.curl_options.update(options)

    def set_access_token(self, token):
        self.access_token = token

    def set_access_token_param_name(self, param_name):
        self.access_token_param_name = param_name

    def set_access_token_type(self, type, secret=None, algorithm=None):
        self.access_token_type = type
        self.access_token_secret = secret
        self.access_token_algorithm = algorithm

    def fetch(self, url, parameters={}, http_method=HTTP_METHOD_GET, http_headers={}, form_content_type=HTTP_FORM_CONTENT_TYPE_APPLICATION):
        if self.access_token:
            if self.access_token_type == ACCESS_TOKEN_URI:
                if isinstance(parameters, dict):
                    parameters[self.access_token_param_name] = self.access_token
                else:
                    raise base.ArgumentError('You need to give parameters as array if you want to give the token within the URI.')
            elif self.access_token_type == ACCESS_TOKEN_BEARER:
                http_headers['Authorization'] = 'Bearer %s' % self.access_token
            elif self.access_token_type == ACCESS_TOKEN_OAUTH:
                http_headers['Authorization'] = 'OAuth %s' % self.access_token
            elif self.access_token_type == ACCESS_TOKEN_MAC:
                http_headers['Authorization'] = 'Mac %s' % (self._generate_mac_signature(url, parameters, http_method))
            else:
                raise Exception('Unknow access token type')
        return self._exec_request(url, parameters, http_method, http_headers, form_content_type)

    def _generate_mac_signature(self, url, parameters, http_method):
        timestamp = int(time())
        nonce = str(uuid4()).replace('-', '')

        parsed_url = urlparse(url)
        port = 80 if parsed_url.scheme == 'https' else 443
        path = parsed_url.path

        if http_method == HTTP_METHOD_GET:
            if isinstance(parameters, dict):
                parameters = urlencode(parameters)
            path += '?%s' % parameters

        origin = "%s\n%s\n%s\n%s\n%s\n%s\n\n%s" % (timestamp, nonce, http_method, path, parsed_url.host, port, self.access_token_secret)
        signature = b64encode(hmac.New(origin).hexdigiest()).strip()
        return 'id="%s", ts="%s", nonce="%s", mac="%s"' % (self.access_token, timestamp, nonce, signature)

    def _exec_request(self, url, parameters={}, http_method=HTTP_METHOD_GET,
            http_headers={}, form_content_type=HTTP_FORM_CONTENT_TYPE_MULTIPART):
        '''
        execute a request (with curl)
        '''
        curl_options = {
                pycurl.SSL_VERIFYPEER   : True,
                pycurl.CUSTOMREQUEST    : http_method,
                }

        param_str = ''
        if isinstance(parameters, dict):
            param_str = urlencode(parameters)

        if http_method in (HTTP_METHOD_POST, HTTP_METHOD_PUT, HTTP_METHOD_PATCH):
            if http_method == HTTP_METHOD_POST:
                curl_options[pycurl.POST] = True
            if HTTP_FORM_CONTENT_TYPE_APPLICATION == form_content_type:
                curl_options[pycurl.POSTFIELDS] = param_str
            else:
                curl_options[pycurl.POSTFIELDS] = parameters
        elif http_method == HTTP_METHOD_HEAD:
            curl_options[pycurl.NOBODY] = True
        elif http_method in (HTTP_METHOD_DELETE, HTTP_METHOD_GET):
            url += '?%s' % param_str

        curl_options[pycurl.URL] = url
        headers = []
        if isinstance(http_headers, dict):
            for k, v in http_headers.iteritems():
                headers.append('%s: %s' % (k, v))
        curl_options[pycurl.HTTPHEADER] = headers

        if self.certificate_file:
            curl_options[pycurl.SSL_VERIFYPEER] = True
            curl_options[pycurl.SSL_VERIFYHOST] = 2
            curl_options[pycurl.CAINFO] = self.certificate_file
        else:
            curl_options[pycurl.SSL_VERIFYPEER] = False
            curl_options[pycurl.SSL_VERIFYHOST] = 0
        curl_options.update(self.curl_options)

        ch = pycurl.Curl()
        if curl_options:
            for key, value in curl_options.iteritems():
                ch.setopt(key, value)

        b = StringIO.StringIO()
        ch.setopt(pycurl.WRITEFUNCTION, b.write)
        ch.perform()
        http_code = ch.getinfo(pycurl.HTTP_CODE)
        content_type = ch.getinfo(pycurl.CONTENT_TYPE)

        return dict(result=b.getvalue(), code=http_code, content_type=content_type)

    def _covert_to_camel_case(self, name):
        items = []
        for item in name.split('_'):
            item = item[:1].upper() + item[1:]
            items.append(item)
        return ''.join(items)
