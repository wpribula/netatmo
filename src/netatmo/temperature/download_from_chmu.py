import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import re
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
    
    
class ChmiStations:
    def __init__(self):
        self._url = r"https://www.chmi.cz/files/portal/docs/meteo/opss/pocasicko_nove/st_zemepis_cz.html"
        self._base_url = r"https://www.chmi.cz"
        self.stations = {}
        self._load_stations()
    
    
    def _load_stations(self) -> list[BeautifulSoup]:
        rows = self._load_rows()
        links = {}
        for row in rows:
            attributes = self._parse_row(row)
            self.stations.update({attributes['name']:Station(attributes)})
        return links
    
        
    def _load_rows(self) -> list[BeautifulSoup]:
        html = requests.get(self._url).content
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all(name='tr', attrs={'class':'nezvyraznit'})
        
        
    def _parse_row(self, row : BeautifulSoup) -> dict:
        cels = row.find_all(name='td')
        return {
            'name':cels[0].text,
            'base_url':self._base_url,
            'url':cels[1].next.attrs['href'],
            'latitude':float(cels[2].text[:-1].replace(',','.')),
            'longitude':float(cels[4].text[:-1].replace(',','.')),
            'height':float(cels[6].text.replace(',','.'))
        }
        
    

    
            
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
            values.append(self._parse_value_cell(cell.text, i))
        data_df = pd.DataFrame(values)
        data_df['value_name'] = cells[0].text
        self.data_df = pd.concat([self.data_df, data_df])
            
            
    def _parse_value_cell(self, cell : str, hour : int) -> dict:
        values = cell.replace(',','.').split(' ')
        return {
            'timestamp' : self.current_time - timedelta(hours=hour),
            'value' : float(values[0]),
            'uom' : values[1]
        }
        
            
        
        
        
if __name__ == "__main__":
    ChmiStations()
    i = 1