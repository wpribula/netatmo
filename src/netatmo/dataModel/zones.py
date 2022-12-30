from dataModel.items import Items, Item
from netatmo.netatmo_api.netatmo_api import NetatmoApi

        
class Zone(Item):
    zone_types = ["day", "night", "away", "frost guard", "custom", "eco", "", "", "comfort"]
    
    def _process_data(self, data : dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.type = self.zone_types[data['type']] if 'type' in data.keys() else None
        # self.room_temp = data['room_temp'] if 'room_temp' in data.keys() else None
        # self.modules = data['modules'] if 'modules' in data.keys() else None
        self._process_rooms(data['rooms']) if 'rooms' in data.keys() else None
        
        
    def _process_rooms(self, rooms_data):
        self.rooms_setpoints = {}
        for room in rooms_data:
            self.rooms_setpoints.update({room['id']:room['therm_setpoint_temperature']})
            

class Zones(Items):
    Item_Obj = Zone
    