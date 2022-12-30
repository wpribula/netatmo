import os
import datetime
import pandas as pd
import numpy as np
from dataModel.items import Items, Item

    
class Room(Item):
    def _process_data(self, data : dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.type = data['type'] if 'type' in data.keys() else None
        self.modules_ids = data['module_ids'] if 'module_ids' in data.keys() else None
        self.home_id = None
        
    def add_status(self, status_data : dict):
        for item_status in status_data:
            if item_status['id'] == self.id:
                self._process_status(item_status)
    
    
    def _process_status(self, item_status : dict):
        self.reachable = item_status['reachable'] if 'reachable' in item_status.keys() else None
        self.heating_power_request = item_status['heating_power_request'] if 'heating_power_request' in item_status.keys() else None
        self.therm_measured_temperature = item_status['therm_measured_temperature'] if 'therm_measured_temperature' in item_status.keys() else None
        self.therm_setpoint_temperature = item_status['therm_setpoint_temperature'] if 'therm_setpoint_temperature' in item_status.keys() else None
        self.therm_setpoint_mode = item_status['therm_setpoint_mode'] if 'therm_setpoint_mode' in item_status.keys() else None
        self.therm_setpoint_fp = item_status['therm_setpoint_fp'] if 'therm_setpoint_fp' in item_status.keys() else None
        self.therm_setpoint_start_time = item_status['therm_setpoint_start_time'] if 'therm_setpoint_start_time' in item_status.keys() else None
        self.therm_setpoint_end_time = item_status['therm_setpoint_end_time'] if 'therm_setpoint_end_time' in item_status.keys() else None
        self.anticipating = item_status['anticipating'] if 'anticipating' in item_status.keys() else None
        self.open_windows = item_status['open_windows'] if 'open_windows' in item_status.keys() else None
        
        
    def _getroommeasure_url_data(self, type : str, from_time : datetime.datetime) -> dict:
        header = {'home_id':self.home_id,
                  'room_id':self.id,
                  'scale':'30min',
                  'type':type,
                  # 'date_end':self.id,
                  # 'limit':1024,
                  'optimize':'false',
                  'real_time':'true'
                }
        try:
            header.update({'date_begin':(int(from_time.timestamp()) + 1)})
        except AttributeError:
            pass
        except TypeError:
            pass
        return header
        
    #=======================================================================================
    #                         TIMESERIES
    #=======================================================================================
    def load_room_timeseries_data(self, type : str, from_time : datetime.datetime):
        data_json = self._netatmo_api.api_request('getroommeasure', self._getroommeasure_url_data(type, from_time))
        data_df = self._parse_temperature_response_real_time(data_json)
        data_df['room_id'] = self.id
        data_df['type'] = type
        return data_df
    
    
    def _parse_temperature_response_real_time(self, response):
        values = []
        times = []
        try:
            for key, value in response['body'].items():
                values.append(value[0])
                times.append(datetime.datetime.fromtimestamp(int(key)))
        except AttributeError:
            pass
        return pd.DataFrame({'datetime':times, 'value':values})
    
    
    def _parse_temperature_response(self, response):
        values = []
        value_time = datetime.datetime.fromtimestamp(response['body']['home']['beg_time'])
        step = datetime.timedelta(seconds=response['body']['home']['step_time'])
        for value in response['body']['home']['values']:
            values.append([value_time, value])
            value_time = value_time + step
    
        
        
    def __str__(self):
        return f"""Room: {self.name}
    Type: {self.type}
    Reachable: {self.reachable}
    Heating power request: {self.heating_power_request}
    Setpoint temperature: {self.therm_setpoint_temperature}
    Setpoint mode: {self.therm_setpoint_mode}
    Setpoint start time: {self.therm_setpoint_start_time}
    Setpoint end time: {self.therm_setpoint_end_time}
    """
    
        
class Rooms(Items):
    Item_Obj = Room
    data_path =  os.path.join(os.path.dirname(__file__), r"temperature_data.csv")
    
    
    def add_home_id(self, home_id):
        for room_id in self.items:
            self.items[room_id].home_id = home_id
    
    
    def get_timeseries_data(self):
        self.temperatures_df = self._load_temperatures_from_file()
        self.temperatures_df['datetime'] = pd.to_datetime(self.temperatures_df['datetime'])
        types = ['temperature', 'sp_temperature']
        for type in types:
            self._load_new_timeseries_data_for_type(type) 
        self.temperatures_df.drop_duplicates(inplace=True)
        self.temperatures_df.to_csv(self.data_path, index=False)     
        return self.temperatures_df
            
            
    def _load_new_timeseries_data_for_type(self, type):
        for room_id in self.items:
            from_date = self._get_latest_value_date(room_id, type)
            if (datetime.datetime.now() - from_date) > datetime.timedelta(minutes=30):
                data_df = self.items[room_id].load_room_timeseries_data(type, from_date)
                self.temperatures_df = pd.concat([self.temperatures_df, data_df])
        
            
    def _load_temperatures_from_file(self):
        try:
            return pd.read_csv(self.data_path)
        except FileNotFoundError:
            return pd.DataFrame({'room_id':[], 'type':[], 'datetime':[], 'value':[]})
        
        
    def _get_latest_value_date(self, room_id, type) -> datetime.datetime:
        filt = (self.temperatures_df['room_id'] == int(room_id)) & (self.temperatures_df['type'] == type)
        return self.temperatures_df.loc[filt, 'datetime'].max()
        
        