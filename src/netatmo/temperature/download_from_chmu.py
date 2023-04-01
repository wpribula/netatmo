import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import re
import pytz
from time import sleep, tzname
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# class ChmiStations:
#     def __init__(self):
#         self._url = r"https://www.chmi.cz/aktualni-situace/aktualni-stav-pocasi/ceska-republika/souhrnny-prehled"
#         self._base_url = r"https://www.chmi.cz"
#         self.links = self._load_links()
    
    
#     def _load_site(self) -> list[BeautifulSoup]:
#         html = requests.get(self._url)
#         soup = BeautifulSoup(html.content, 'html.parser')
#         return soup.find_all(name='ul', attrs={'class':'detached-menu'})
        
        
#     def _load_links(self) -> list[BeautifulSoup]:
#         menu = self._load_site()
#         links = {}
#         for menu_item in menu:
#             links.update(self._extract_links(menu_item.find_all(name='li', attrs={'class':None})))
#         return links
        
        
#     def _extract_links(self, items : list[BeautifulSoup]) -> dict:
#         links = {}
#         for item in items:
#             link = item.find(name='a')
#             links.update({link.text:link.attrs['href']})
#         return self._filter_links(links)
    
    
#     def _filter_links(self, links : dict) -> dict:
#         new_links = {}
#         for key, link in links.items():
#             if 'profesionalni-stanice/prehled-stanic' in link:
#                 new_links.update({key:self._base_url + link})
#         return new_links
    
    
        
    

    
            
class Station:
    def __init__(self, attributes : dict):
        self.name = attributes['name']
        self._base_url = attributes['base_url']
        self.url = self._base_url + attributes['url']
        self.latitude = attributes['latitude']
        self.longitude = attributes['longitude']
        self.height = attributes['height']
        self.url = "https://www.chmi.cz/files/portal/docs/meteo/opss/pocasicko_nove/st_11406_cz.html"
        self.station_number = self._get_station_number()
        self.data_df = pd.DataFrame
        self._load_data()
        
    def _get_station_number(self) -> str:
        html = requests.get(self.url).content
        graf_txt =  BeautifulSoup(html, 'html.parser').find_all(name='img')[-1].attrs['src']
        return re.findall(r"\./st_(\d*)_grafy/graf_10_cz.png", graf_txt)[0]
        
    def _get_station_data_url(self) -> str:
        return self._base_url + f"/files/portal/docs/meteo/opss/pocasicko_nove/st_{self.station_number}_cz.html"
                    
                    
    def _load_data(self):
        html = requests.get(self._get_station_data_url()).content
        tables = BeautifulSoup(html, 'html.parser').find_all(name='table')
        self._parse_time(tables[0])
        self._parse_hourly_data(tables[1])
        self._parse_daily_data(tables[2])
        
        
        i = 1
        
    def _parse_time(self, table : BeautifulSoup) -> dict:
        time_str = table.find_all(name='td')[2].text
        time_str = re.findall("^(\d+. \d+. \d+ \d+:\d+) .*", time_str)[0]
        time = datetime.strptime(time_str, "%d. %m. %Y %H:%M")
        self.current_time = time


    def _parse_hourly_data(self, table : BeautifulSoup) -> dict:
        for row in table.find_all(name='tr')[1:]:
            self._parse_hourly_data_row(row)
    
    
    def _parse_hourly_data_row(self, row : BeautifulSoup) -> pd.DataFrame:
        cells = row.find_all(name='td')
        values = []
        for i, cell in enumerate(cells[2:]):
            values.append(self._parse_cell(cell.text, i))
        data_df = pd.DataFrame(values)
        data_df['value_name'] = cells[0].text
        self.data_df = pd.concat([self.data_df, data_df])
            
            
    def _parse_cell(self, cell : str, hour : int) -> dict:
        if cell[0] in '0123456789':
            self._parse_value_cell(cell, hour)
        else:
            self._parse_text_cell(cell, hour)
        
    def _parse_value_cell(self, cell : str, hour : int) -> dict:
        return {
            'timestamp' : self.current_time - timedelta(hours=hour),
            'value' : cell,
            'uom' : ''
        }
    
            
        
class ChmiStations:
    def __init__(self):
        self._url = r"https://www.chmi.cz/files/portal/docs/meteo/opss/pocasicko_nove/st_zemepis_cz.html"
        self._base_url = r"https://www.chmi.cz"
        self.stations = {}
        self._load_stations()
    
    
    def _load_stations(self) -> dict[str, Station]:
        rows = self._load_rows()
        links = {}
        for row in rows:
            attributes = self._parse_row(row)
            self.stations.update({attributes['name']:Station(attributes)})
            sleep(100)
        return links
    
        
    def _load_rows(self) -> list[BeautifulSoup]:
        html = requests.get(self._url).content
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all(name='tr', attrs={'class':'nezvyraznit'})
        
        
    def _parse_row(self, row : BeautifulSoup) -> dict:
        cells = row.find_all(name='td')
        return {
            'name':cells[0].text,
            'base_url':self._base_url,
            'url':cells[1].next.attrs['href'],
            'latitude':float(cells[2].text[:-1].replace(',','.')),
            'longitude':float(cells[4].text[:-1].replace(',','.')),
            'height':float(cells[6].text.replace(',','.'))
        }
        
        
class DataTable:
    def __init__(self, file : str, hourly_value_columns : list[int] = [], daily_value_columns : list[int] = [], daily_text_column : list[int] = []):
        self._url = r"https://www.chmi.cz/files/portal/docs/meteo/opss/pocasicko_nove/" + file
        self._hourly_value_columns = hourly_value_columns
        self._daily_value_columns = daily_value_columns
        self._daily_text_column = daily_text_column
        self._load_data()
        
    def _load_data(self):
        html = requests.get(self._url).content
        tables = pd.read_html(self._url)
        self._parse_hourly_time(tables[0])
        self._parse_daily_time(tables[0])
        self._parse_data(tables[1])
        self._parse_daily_data(tables[2])
        
        
    def _parse_hourly_time(self, table : BeautifulSoup) -> dict:
        time_str = table.at[1, 0]
        time_str = re.findall("^(\d+. \d+. \d+ \d+:\d+) .*", time_str)[0]
        timestamp = datetime.strptime(time_str, "%d. %m. %Y %H:%M")
        timestamp = pytz.timezone('CET').localize(timestamp)
        self.current_timestamp = timestamp
        
        
    def _parse_daily_time(self, table : BeautifulSoup) -> dict:
        try:
            time_str = table.at[3, 0]
        except KeyError:
            self.current_daily_timestamp = pd.NaT
            return
        time_str = re.findall("^od (\d+. \d+. \d+ \d+:\d+) .*", time_str)[0]
        timestamp = datetime.strptime(time_str, "%d. %m. %Y %H:%M")
        timestamp = pytz.timezone('CET').localize(timestamp)
        self.current_daily_timestamp = timestamp


    def _parse_data(self, table_df : pd.DataFrame) -> dict:
        table_df = self._parse_column_names(table_df)
        self._data_df = pd.DataFrame()
        self._data_df = pd.concat([self._data_df, self._parse_columns(table_df, table_df.columns[self._hourly_value_columns], self.current_timestamp)])
        self._data_df = pd.concat([self._parse_columns(table_df, table_df.columns[self._daily_value_columns], self.current_daily_timestamp)])
        self._data_df = pd.concat([self._parse_columns(table_df, table_df.columns[self._daily_text_column], self.current_timestamp, is_text = True)])
        i = 1
        
        
    def _parse_columns(self, table_df : pd.DataFrame, columns : tuple, timestamp : datetime, is_text : bool = False) -> pd.DataFrame:
        try:
            table_df = self._melt_data(table_df, columns, is_text)
            table_df['timestamp'] = timestamp
            return table_df
        except ValueError:
            return pd.DataFrame()
            
    def _parse_column_names(self, table_df : pd.DataFrame) -> pd.DataFrame:
        table_df.drop(columns=[1], inplace=True)
        table_df.columns = table_df.loc[0]
        return table_df.drop(index=[0])
        
        
    def _melt_data(self, table_df : pd.DataFrame, columns : tuple, is_text : bool = False) -> pd.DataFrame:    
        table_df = table_df.melt(id_vars="Stanice", value_vars=columns, var_name=['type'], ignore_index=True).dropna(subset=['value'])
        if is_text:
            return table_df
        return self._parse_string_to_value_and_uom(table_df)
        
        
    def _parse_string_to_value_and_uom(self, table_df : pd.DataFrame) -> pd.DataFrame:
        table_df['value'].replace('neměřitelné', np.NaN)
        table_df['value'].replace('roztál', '0 cm')
        table_df[['value', 'uom']] = table_df['value'].apply(lambda x: re.findall('(\d+\.?\d*)\s?([^\s\(\)]*)', x.replace(',','.'))[0]).tolist()
        table_df['value'] = table_df['value'].astype(float)
        return table_df
    
    
    def _parse_hourly_data_row(self, row : BeautifulSoup) -> pd.DataFrame:
        cells = row.find_all(name='td')
        values = []
        for i, cell in enumerate(cells[2:]):
            values.append(self._parse_cell(cell.text, i))
        data_df = pd.DataFrame(values)
        data_df['value_name'] = cells[0].text
        self.data_df = pd.concat([self.data_df, data_df])

if __name__ == "__main__":
    # ChmiStations()
    DataTable(r"st_pudni_teploty_cz.html",
              hourly_value_columns = [1,2,3,4,5]
    )
    #TODO parse timestamp from column
    DataTable(r"st_oblacnost_cz.html",
              daily_text_column = [1,2,3],
              hourly_value_columns = [4,5]
    )
    #TODO parse timestamp from column
    DataTable(r"st_srazky_cz.html",
              hourly_value_columns = [1,2,3],
              daily_value_columns = [4,5,6,7]
    )
    DataTable(r"st_vitr_cz.html",
              hourly_value_columns = [1,2,3]
    )
    DataTable(r"st_tlaky_cz.html",
              hourly_value_columns = [1,2,3]
    )
    DataTable(r"st_teploty_cz.html",
              hourly_value_columns = [1,2,3],
              daily_value_columns = [4,5,6,7]
    )
    i = 1