import datetime
from dataModel.items import Items, Item

        
class Module(Item):
    battery_states = ["very_low", 
                      "low",
                      "medium",
                      "high",
                      "full"]
    dhw_control_states = ["none", "instantaneous", "water_tank"]
    boiler_error_types = ["boiler_not_responding",
                          "maintenance",
                          "water_pressure",
                          "boiler_flame",
                          "air_pressure",
                          "boiler_temperature"]
        
    def _process_data(self, data : dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.type = self._resolve_module_type(data['type']) if 'type' in data.keys() else None
        self.setuo_date = data['setuo_date'] if 'setuo_date' in data.keys() else None
        self.room_id = data['room_id'] if 'room_id' in data.keys() else None
        self.modules_bridge = data['modules_bridge'] if 'modules_bridge' in data.keys() else None


    def add_status(self, status_data : dict):
        for item_status in status_data:
            if item_status['id'] == self.id:
                self._process_status(item_status)
    
    
    def _process_status(self, item_status : dict):
        self.reachable = item_status['reachable'] if 'reachable' in item_status.keys() else None
        self.firmware_revision = item_status['firmware_revision'] if 'firmware_revision' in item_status.keys() else None
        self.wifi_strenght = item_status['wifi_strenght'] if 'wifi_strenght' in item_status.keys() else None
        self.rf_strenght = item_status['rf_strenght'] if 'rf_strenght' in item_status.keys() else None
        self.dhw_control = item_status['dhw_control'] if 'dhw_control' in item_status.keys() else None
        self.boiler_valve_comfort_boost = item_status['boiler_valve_comfort_boost'] if 'boiler_valve_comfort_boost' in item_status.keys() else None
        self.boiler_status = item_status['boiler_status'] if 'boiler_status' in item_status.keys() else None
        self.boiler_error = item_status['boiler_error'] if 'boiler_error' in item_status.keys() else None
        self.boiler_control = item_status['boiler_control'] if 'boiler_control' in item_status.keys() else None
        self.anticipating = item_status['anticipating'] if 'anticipating' in item_status.keys() else None
        self.bridge = item_status['bridge'] if 'bridge' in item_status.keys() else None
        self.battery_state = item_status['battery_state'] if 'battery_state' in item_status.keys() else None
        self.battery_level = item_status['battery_level'] if 'battery_level' in item_status.keys() else None
        self.last_seen = datetime.datetime.fromtimestamp(int(item_status['last_seen'])) if 'last_seen' in item_status.keys() else None
        
        
        
    def _resolve_module_type(self, type):
        types = {'NLG':'Gateway',
                 'NLP':'Socket',
                 'NLF':'Switch',
                 'NLT':'Remote',
                 'NLM':'Micromodule',
                 'NLV':'Roller shutter',
                 'NLL':'Italian switch',
                 'NLPC':'Energy meter',
                 'NLPM':'Mobile socket',
                 'NLPO':'Connected contactor',
                 'NLC':'Cable outlet',
                 'BNS':'Smarther with Netatmo',
                 'OTH':'Smart Modulating Thermostat Relay',
                 'OTM':'Smart Modulating Thermostat',
                 'NRV':'Smart Valves'}
        try:
            return types[type]
        except KeyError:
            return type
        
        
    def __str__(self):
        return f"""Name: {self.name}
    Type: {self.type}
    Reachable: {self.reachable}
    Firmware revision: {self.firmware_revision}
    RF strenght: {self.rf_strenght}
    Boiler valve comfort boost: {self.boiler_valve_comfort_boost}
    Boiler status: {self.boiler_status}
    Battery state: {self.battery_state}
    """
        


class Modules(Items):
    Item_Obj = Module
    
    def get_data(self):
        pass     