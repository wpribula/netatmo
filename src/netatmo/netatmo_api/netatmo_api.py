import requests
import time
import json
from uuid import uuid4

from netatmo.netatmo_api.netatmo_secrets import NetatmoSecrets
from netatmo.netatmo_api.netatmo_tokens import NetatmoTokens


# class Scope:
#     read_station = 'read_station'
#     read_thermostat = 'read_thermostat'
#     write_thermostat = 'write_thermostat'
#     read_camera = 'read_camera'
#     write_camera = 'write_camera'
#     access_camera = 'access_camera'
#     read_presence = 'read_presence'
#     access_presence = 'access_presence'
#     read_smokedetector = 'read_smokedetector'
#     read_homecoach = 'read_homecoach'
    
        

class NetatmoApi():
    def __init__(self):
        self._guid = uuid4().hex
        self._auth_url = 'https://api.netatmo.com/oauth2/'
        self._api_url = 'https://api.netatmo.com/api/'
        self.tokens = NetatmoTokens()   
        self.secrets = NetatmoSecrets(self._guid)
        
        
    def get_netatmo_login_page_url(self):
        return self._auth_url + 'authorize' + self.secrets.get_netatmo_login_page_url_parameters_string()
 
 
    def send_token_request(self, header):
        response = requests.post(f'{self._auth_url}token', data=header).json()
        self._check_response_error(response)
        self._parse_token_resposne(response)
        
        
    def refresh_tokens(self):
        if self.tokens.need_new_login():
            raise RuntimeError("Need to login again.")
        header = self.secrets.get_header_for_refresh_token(self.tokens.refresh_token)
        self.send_token_request(header)
        
        
    def new_token(self, code):
        header = self.secrets.get_header_for_new_token_request(code)
        self.send_token_request(header)
        
        
    def api_request(self, function : str, data : dict = {}):
        if not self.tokens.is_authenticated():
            self.refresh_tokens()
        # response = requests.get(f'{self._api_url}{function}', headers=self._get_base_header(), data=data)
        return requests.get(f'{self._api_url}{function}?{"&".join(f"{key}={value}" for key, value in data.items())}', headers=self.tokens.get_base_header_wit_bearer()).json()
    
    
    #==============================================================================
    #                              CHECK
    #==============================================================================   
    def is_authenticated(self):
        if not self.tokens.is_authenticated(): 
            try:
                self.refresh_tokens()
            except RuntimeError:
                return False
        return self.tokens.is_authenticated()
    
             
    def _parse_token_resposne(self, response):
        try:
            self.tokens.set_tokens(response['access_token'],
                                   response['refresh_token'],
                                   time.time() + 0.95 * response['expires_in'])
        except KeyError:
            raise RuntimeError(f'{response}')
        
        
    def _check_response_error(self, response : json):
        try:
            raise RuntimeError(f"Error: {response['error']}, Description: {response['error_description']}")
        except KeyError:
            return
            