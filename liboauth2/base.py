# -*- coding: utf-8 -*-


class ArgumentError(Exception):
    pass


class GrantType(object):

    def validate_parameters(self, parameters):
        pass


class AuthorizationCode(GrantType):

    GRANT_TYPE = 'authorization_code'


    def validate_parameters(self, parameters):
        if 'code' not in parameters:
            raise ArgumentError('The \'code\' parameter must be defined for the Authorization Code grant type')
        elif 'redirect_uri' not in parameters:
            raise ArgumentError('The \'code\' parameter must be defined for the Authorization Code grant type')


class Password(GrantType):

    GRANT_TYPE = 'password'

    def validate_parameters(self, parameters):
        if 'username' not in parameters:
            raise ArgumentError('The \'username\' parameter must be defined for the Password grant type')
        elif 'password' not in parameters:
            raise ArgumentError('The \'password\' parameter must be defined for the Password grant type')


class RefreshToken(GrantType):

    GRANT_TYPE = 'refresh_token'

    def validate_parameters(self, parameters):
        if 'refresh_token' not in parameters:
            raise ArgumentError('The \'refresh_token\' parameter must be defined for the refresh token grant type')


class ClientCredentials(GrantType):

    GRANT_TYPE = 'client_credentials'

    def validate_parameters(self, parameters):
        pass
