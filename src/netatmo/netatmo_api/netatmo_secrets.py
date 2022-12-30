import json
import os

   
class NetatmoSecrets():
    def __init__(self, guid, file = os.path.join(os.path.dirname(__file__),'config.json'), redirect_url = 'http://localhost/token'):
        self._guid = guid
        self._client_id = ''
        self._client_secret = ''
        self._scope = ''
        
        self._redirect_url = redirect_url
        
        self._file = file
        self._load_secrets()
        
        
    def _load_secrets(self):
        with open(self._file,'r') as file:
            cfg = json.loads(file.read())['netatmo_app']
        self._client_id = cfg['client_id']
        self._client_secret = cfg['client_secret']
        self._scope = cfg['scope']
        
        
    #==============================================================================
    #                                 HTTP
    #==============================================================================            
    def get_netatmo_login_page_url_parameters_string(self) -> str:
        url = f'?client_id={self._client_id}'
        url += f'&redirect_uri={self._redirect_url}'
        url += f'&scope={self._scope}'
        url += f'&state={self._guid}'
        return url
    
        
    def get_header_for_new_token_request(self, code : str) -> dict:
        return {'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'grant_type':'authorization_code',
                'client_id':self._client_id,
                'client_secret':self._client_secret,
                'redirect_uri':self._redirect_url,
                'code':code,
                'scope':self._scope,
                'state':self._guid}
        
        
    def get_header_for_refresh_token(self, refresh_token) -> dict:
        return {'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                'grant_type':'refresh_token',
                'client_id':self._client_id,
                'client_secret':self._client_secret,
                'refresh_token':refresh_token}
        