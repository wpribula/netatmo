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
    

    @classmethod
    def add_data(cls, netatmo_api : NetatmoApi = None, data : dict = None, status_data = None):
        ids = []
        data = cls._get_data(data, netatmo_api)
        for item in data:
            obj = cls.Item_Obj(item, netatmo_api)
            if status_data:
                obj.add_status(status_data)
            cls.items.update({obj.id:obj})
            ids.append(obj.id)
        return ids
            
    
    @staticmethod
    def _get_data(data : dict, netatmo_api : NetatmoApi = None):
        if data:
            return data
                   
            
    def __str__(self):
        return '\n\n'.join(str(value) for value in self.items)