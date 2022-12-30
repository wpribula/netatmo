import datetime
import pandas as pd

from netatmo.dataModel.homes import Homes
from netatmo.netatmo_api.netatmo_api import NetatmoApi


class NetatmoData():
    def __init__(self):
        self._homes = None
        
        
    def get_homes_data(self, netatmo_api : NetatmoApi = None) -> Homes:
        if not self._homes:
            self._load_homes_data(netatmo_api)
        self._chack_data_freshness(netatmo_api)
        return self._homes
    
    
    def _load_homes_data(self, netatmo_api : NetatmoApi = None):
        if not netatmo_api:
            raise RuntimeError("Missing netatmo_api.")
        self._homes = Homes(netatmo_api)
    
    
    def _chack_data_freshness(self, netatmo_api : NetatmoApi = None):
        if (datetime.datetime.now() - self._homes.last_update) > datetime.timedelta(minutes=1):
            self._load_homes_data(netatmo_api)
            
            
    def get_timeseries_df(self) -> pd.DataFrame:
        data_df = pd.DataFrame
        for home in self._homes.items.values():
            data_df = pd.concat([data_df, home.get_timeseries_data()])
        return data_df
            
    
    def get_timeseries_df_for_home(self, home_id) -> pd.DataFrame:
        data_df = pd.DataFrame
        return self._homes.items[home_id].get_timeseries_data()