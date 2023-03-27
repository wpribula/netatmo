import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class GasConsumption:
    def __init__(self):
        self._path = r"C:\Users\Wojciech\OneDrive\Dokumenty\Uczetnictwi\Energie\Spotrzeba plynu.xlsx"
        self._temp_path = r"F:\Downloads\export.csv"
        self.data_df = pd.DataFrame()
        self._load_data()
        self.sampled_s = self._sample_data()
        self.temperature_s = self._load_temperature()
        
        
    def _load_data(self):
        self.data_df = pd.read_excel(self._path)
        self.data_df.set_index('Time', drop=True, inplace=True)
        
        
    def _sample_data(self):
        start_date = self.data_df.index.date.min()
        index = pd.date_range(start_date, pd.Timestamp.now(), freq='D')
        data_s = pd.Series(np.NaN, index=index)
        data_s = pd.concat([data_s, self.data_df['Value']])
        data_s.sort_index(inplace=True)
        # latest_valid_index = data_s.loc[~data_s.isna()].index[-1]
        data_s.interpolate('time', limit_area='inside', inplace=True)
        # data_s.drop(index=data_s.loc[data_s.index > latest_valid_index].index)
        data_s.drop(index=data_s.loc[data_s.index.hour > 0].index, inplace=True)
        return data_s.diff(1).shift(-1).dropna()
    
    
    def _load_temperature(self) -> pd.Series:
        temp_df = pd.read_csv(self._temp_path)
        temp_df['date'] = pd.to_datetime(temp_df['date'])
        temp_df.set_index('date', drop=True, inplace=True)
        return temp_df['tavg']
    
    
    def get_figure(self) -> Figure:
        fig = plt.figure(figsize=(9,10))
        axs = fig.subplots(1)
        axs.plot(self.sampled_s, label='Gas consumption')
        axs.twinx().plot(self.temperature_s, color='orange', label='Avg temperature')
        axs.grid()
        fig.legend()
        return fig
        
    
        
        
        
if __name__ == "__main__":
    gc = GasConsumption()
    gc.get_figure().show()
    i = 1
