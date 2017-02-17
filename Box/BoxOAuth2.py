# coding: utf-8
import requests
import Box.BoxExceptions as e
from __future__ import print_function, unicode_literals


class BoxOAuth2:
    CLIENT_ID = 'y0vwgy93gan8sdalfr39vjblmvyb32xw'  # Insert Box client ID here
    CLIENT_SECRET = 'WPIqt4wCxKykaq1ENozbpXElhqaMDPup'  # Insert Box client secret here

    def _oauth2_token_request(self, client_id, client_secret, grant_type, token, **kwargs):

        """
        Performs an oauth2 request against Box
        """
        args = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': grant_type,
            'refresh_token': token
        }

        args.update(kwargs)
        url = 'https://www.box.com/api/oauth2/token'
        headers = {u'content-type': u'application/x-www-form-urlencoded'}
        req = requests.Request('POST', url, headers=headers, data=args)
        prepReq = req.prepare()

        response = requests.Session().send(prepReq)                 #requests.post(url, args, headers=headers)

        return self._handle_auth_response(response)

    def _handle_auth_response(self, response):
        result = response.json()
        if 'error' in result:
            raise e.BoxAuthenticationException(response.status_code, message=result.get('error_description'), error=result['error'])
        return result




