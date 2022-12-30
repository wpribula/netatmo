import datetime
import pandas as pd

from netatmo.dataModel.homes import Homes
from netatmo.dataModel.rooms import Rooms
from netatmo.dataModel.schedules import Schedules
from netatmo.dataModel.modules import Modules
from netatmo.dataModel.zones import Zones
from netatmo.netatmo_api.netatmo_api import NetatmoApi



class NetatmoData():
    def __init__(self):
        self.homes = Homes
        self.rooms = Rooms
        self.schedules = Schedules
        self.modules = Modules
        self.zones = Zones
        self.last_update = datetime.datetime.min
        self.homes_ids = []
        
        
    def load_data(self, netatmo_api : NetatmoApi) -> Homes:
        if (datetime.datetime.now() - self.last_update) > datetime.timedelta(minutes=1):
            self._load_homes_data(netatmo_api)
        return self
    
    
    def _load_homes_data(self, netatmo_api : NetatmoApi):
        self.homes_ids = Homes.add_data(netatmo_api)
        self.last_update = datetime.datetime.now()
        
            
    def get_timeseries_df(self) -> pd.DataFrame:
        data_df = pd.DataFrame
        for home in self._homes.items.values():
            data_df = pd.concat([data_df, home.get_timeseries_data()])
        return data_df
            
    
    def get_timeseries_df_for_home(self, home_id) -> pd.DataFrame:
        data_df = pd.DataFrame
        return self._homes.items[home_id].get_timeseries_data()