from netatmo.netatmo_api.netatmo_api import NetatmoApi

class Item:
    def __init__(self, data : dict, netatmo_api : NetatmoApi):
        self._netatmo_api = netatmo_api
        self._process_data(data)
     
     
    def _process_data(self, data : dict):
        pass

        
    def add_status(self, status_data : dict):
        pass


class Items:
    Item_Obj = Item
    items = {}
    
    def __init__(self, netatmo_api : NetatmoApi):
        self._netatmo_api = netatmo_api

            
    def add_data(self, data : dict = None, status_data = None):
        ids = []
        data = self._get_data(data)
        for item in data:
            obj = self.Item_Obj(item, self._netatmo_api)
            if status_data:
                obj.add_status(status_data)
            self.__class__.items.update({obj.id:obj})
            ids.append(obj.id)
        return ids
            
            
    def _get_data(self, data : dict):
        if data:
            return data
        
            
    def get_by_id(self, id : str):
        for item in self.items:
            if item.id == id:
                return item
            
            
    def get_by_name(self, name : str):
        for item in self.items:
            if item.name == name:
                return item
            
            
    def __str__(self):
        return '\n\n'.join(str(value) for value in self.items)