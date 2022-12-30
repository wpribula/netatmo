import time
import json
import os

class NetatmoTokens():
    def __init__(self, file = os.path.join(os.path.dirname(__file__),'authentication.json')):
        self.access_token = ''
        self.refresh_token = ''
        self.expires = 0
        
        self._file = file
        self.load_tokens()
        
        
    def set_tokens(self, access_token, refresh_token, expires):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires = expires
        self.save_tokens()
        
        
    def load_tokens(self) -> bool:
        try:
            with open(self._file,'r') as file:
                values = json.loads(file.read())
        except FileNotFoundError:
            return False
        except json.decoder.JSONDecodeError:
            return False
        try:
            self.access_token = values['access_token']
            self.refresh_token = values['refresh_token']
            self.expires = values['expires']
            if not self._token_expired():
                return True
        except TypeError:
            pass
        except KeyError:
            pass            
        return False
    
    
    def save_tokens(self):
        with open(self._file,'w') as file:
            file.write(json.dumps({'access_token':self.access_token,
                                   'refresh_token':self.refresh_token,
                                   'expires':self.expires}))
            
            
    #==============================================================================
    #                                 HTTP
    #==============================================================================               
    def get_base_header_wit_bearer(self) -> dict:
        return {'Authorization':f'Bearer {self.access_token}',
                'accept':'application/json'}
        
            
    #==============================================================================
    #                                 CHECKS
    #==============================================================================
    def _token_expired(self):
        if time.time() > self.expires:
            return True
        return False
        
    
    def is_authenticated(self):
        return not self._token_expired() | (not self.access_token)
    
    
    def need_new_login(self):
        return self._token_expired() & (not self.access_token)
