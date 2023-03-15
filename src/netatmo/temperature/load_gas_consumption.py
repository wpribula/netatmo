import pandas as pd

class GasConsumption:
    def __init__(self)
        self._path = r"C:\Users\Wojciech\OneDrive\Dokumenty\Uczetnictwi\Energie\Spotrzeba plynu.xlsx"
        self.data_df = pd.DataFrame()
        self._laod_data()
        
    def _load_data(self):
        self.data_df = pd.read_excel(self._path)
        
        
if __name__ == "__main__":
    gc = GasConsumption()
    print(gc.data_df)