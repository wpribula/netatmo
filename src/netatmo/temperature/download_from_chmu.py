import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Temperature:
    def __init__(self, stanice : str):
        # self.url = f"https://www.chmi.cz/files/portal/docs/meteo/ok/denni_data/Denni_data_ze_stanic/files/{stanice}.xlsx"
        self.url = "F:\Downloads\O1MOSN01.xlsx"
        self._read_temperature()
        
        
    def _read_temperature(self):
        self.data_df = pd.read_excel(self.url, 1)
        self.data_df.drop([0,1,2], inplace=True)
        self.data_df.columns = ['year', 'month'] + [i for i in range(1,32)]
        self.data_df = self.data_df.melt(id_vars=['year','month'], var_name='day', value_name='temperature')
        self.data_df.dropna(inplace=True)
        self.data_df['year'] = self.data_df['year'].astype(int)
        self.data_df['month'] = self.data_df['month'].astype(int)
        self.data_df['day'] = self.data_df['day'].astype(int)
        self.data_df['timestamp'] = self.data_df.apply(lambda row: pd.Timestamp(year=int(row['year']), month=int(row['month']), day=int(row['day'])), axis=1)
        self.data_df.set_index('timestamp', drop=True, inplace=True)
        self.data_df.sort_index(inplace=True)
    
    def getTemperature(self) -> pd.Series:
        return self.data_df['temperature']
        
        
if __name__ == "__main__":
    stanice = "O1MOSN01"
    t = Temperature(stanice)
    # t.getTemperature().plot()
    # plt.show()
    
    
    fig = plt.figure(figsize=(8,8))
    min_year = t.data_df['year'].min()
    for year, data in t.data_df.groupby('year'):
        data = data.groupby('month').agg({'temperature':'mean', 'day':'min'})
        # theta = (data.apply(lambda row: (row.name - pd.Timestamp(year=int(row['year']), month=1, day=1)).days + 0, axis=1) / 365 * 2 * np.pi).values
        theta = np.linspace(0,2*np.pi,12)
        r = data['temperature'].values
        ax1 = plt.subplot(111,projection="polar")
        ax1.plot(theta, r, c=plt.cm.viridis((year - min_year) * 10))
    ax1.set_xticklabels([str(month) for month in range(1,13)])
    ax1.set_xticks(np.linspace(0,2*np.pi,13))
    fig.set_facecolor("#323331")
    ax1.set_facecolor("#000100")
    plt.show()
    i = 1