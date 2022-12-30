import datetime
import pandas as pd

from netatmo.dataModel.rooms import Rooms
from netatmo.dataModel.modules import Modules
from netatmo.dataModel.schedules import Schedules
from netatmo.dataModel.items import Items, Item
from netatmo.netatmo_api.netatmo_api import NetatmoApi
   
        
        
class Home(Item):
    def _process_data(self, data : dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.altitude = data['altitude'] if 'altitude' in data.keys() else None
        self.coordinates = data['coordinates'] if 'coordinates' in data.keys() else None
        self.country = data['country'] if 'country' in data.keys() else None
        self.timezone = data['timezone'] if 'timezone' in data.keys() else None
        self.temperature_control_mode = data['temperature_control_mode'] if 'temperature_control_mode' in data.keys() else None
        self.therm_mode = data['therm_mode'] if 'therm_mode' in data.keys() else None
        self.therm_setpoint_default_duration = data['therm_setpoint_default_duration'] if 'therm_setpoint_default_duration' in data.keys() else None
        
        self.schedules_ids = Schedules.add_data(self._netatmo_api, data['schedules']) if 'schedules' in data.keys() else None
        
        self._status_raw = self._get_home_status()
        self.status = self._status_raw['status'] if 'status' in self._status_raw.keys() else None
        self.time_server = self._status_raw['time_server'] if 'time_server' in self._status_raw.keys() else None
        
        try:
            self.modules_ids = Modules.add_data(self._netatmo_api, data['modules'], status_data = self._status_raw['body']['home']['modules']) if 'modules' in data.keys() else None
        except KeyError:
            self.modules_ids = Modules.add_data(self._netatmo_api, data['modules']) if 'modules' in data.keys() else None
            
        try: 
            self.rooms_ids = Rooms.add_data(self._netatmo_api, data['rooms'], status_data = self._status_raw['body']['home']['rooms']) if 'rooms' in data.keys() else None
        except KeyError:
            self.rooms_ids = Rooms.add_data(self._netatmo_api, data['rooms']) if 'rooms' in data.keys() else None
        self._add_home_id_to_rooms()
        return
    
    
    def _add_home_id_to_rooms(self):
        for room_id in self.rooms_ids:
            Rooms.items[room_id].home_id = self.id
    
    
    def _homestatus_url_data(self) -> dict:
        return {'home_id':self.id}
        
        
    def _get_home_status(self):
        return self._netatmo_api.api_request('homestatus', self._homestatus_url_data())
    
    
    def get_modules_for_room(self, room_id):
        return [module for module in self.modules_ids.items.values() if module.room_id == room_id]
    
    
    def get_timeseries_data(self) -> pd.DataFrame:
        return self.rooms_ids.get_timeseries_data()
            
    
    def __str__(self):
        return f"""Name: {self.name}
    Temperature control mode: {self.temperature_control_mode}
    Therm mode: {self.therm_mode}
    Therm setpoint default duration: {self.therm_setpoint_default_duration}
    Status: {self.status}
    Schedules:
    {self.schedules_ids}
    Modules:
    {self.modules_ids}
    Rooms:
    {self.rooms_ids}
    """
        
        
class Homes(Items):
    Item_Obj = Home
    
    
    @staticmethod
    def _get_data(data : dict = None, netatmo_api : NetatmoApi = None):
        data = netatmo_api.api_request('homesdata')
        return data['body']['homes']