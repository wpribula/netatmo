from dataModel.items import Items, Item

        
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
        self.rooms = {}
        for room in rooms_data:
            self.rooms.update({room['id']:room['therm_setpoint_temperature']})
    
    
    def __str__(self):
        return f"""Name: {self.name}
    Selected: {self.selected}
    """
        

class Zones(Items):
    Item_Obj = Zone

    def get_data(self):
        pass