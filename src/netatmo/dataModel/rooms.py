import os
import datetime
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from matplotlib.figure import Figure

from dataModel.items import Items, Item
from dataModel.schedules import Schedules, Schedule

    
class Room(Item):
    def _process_data(self, data : dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.type = data['type'] if 'type' in data.keys() else None
        self.modules_ids = data['module_ids'] if 'module_ids' in data.keys() else None
        self.home_id = None
        self.schedules_ids = None
        
    def add_status(self, status_data : dict):
        for item_status in status_data:
            if item_status['id'] == self.id:
                self._process_status(item_status)
    
    
    def _process_status(self, item_status : dict):
        self.reachable = item_status['reachable'] if 'reachable' in item_status.keys() else None
        self.heating_power_request = item_status['heating_power_request'] if 'heating_power_request' in item_status.keys() else None
        self.therm_measured_temperature = item_status['therm_measured_temperature'] if 'therm_measured_temperature' in item_status.keys() else None
        self.therm_setpoint_temperature = item_status['therm_setpoint_temperature'] if 'therm_setpoint_temperature' in item_status.keys() else None
        self.therm_setpoint_mode = item_status['therm_setpoint_mode'] if 'therm_setpoint_mode' in item_status.keys() else None
        self.therm_setpoint_fp = item_status['therm_setpoint_fp'] if 'therm_setpoint_fp' in item_status.keys() else None
        self.therm_setpoint_start_time = item_status['therm_setpoint_start_time'] if 'therm_setpoint_start_time' in item_status.keys() else None
        self.therm_setpoint_end_time = item_status['therm_setpoint_end_time'] if 'therm_setpoint_end_time' in item_status.keys() else None
        self.anticipating = item_status['anticipating'] if 'anticipating' in item_status.keys() else None
        self.open_windows = item_status['open_windows'] if 'open_windows' in item_status.keys() else None
        
        
    def _getroommeasure_url_data(self, type : str, from_time : datetime.datetime) -> dict:
        header = {'home_id':self.home_id,
                  'room_id':self.id,
                  'scale':'30min',
                  'type':type,
                  # 'date_end':self.id,
                  # 'limit':1024,
                  'optimize':'false'
                }
        try:
            header.update({'date_begin':(int(from_time.timestamp()) + 1)})
        except AttributeError:
            pass
        except TypeError:
            pass
        return header
        
    #=======================================================================================
    #                         TIMESERIES
    #=======================================================================================
    def load_room_timeseries_data(self, type : str, from_time : datetime.datetime):
        data_json = self._netatmo_api.api_request('getroommeasure', self._getroommeasure_url_data(type, from_time))
        data_df = self._parse_temperature_response_real_time(data_json)
        data_df['room_id'] = self.id
        data_df['type'] = type
        return data_df
    
    
    def _parse_temperature_response_real_time(self, response):
        values = []
        times = []
        try:
            for key, value in response['body'].items():
                values.append(value[0])
                times.append(datetime.datetime.fromtimestamp(int(key)))
        except AttributeError:
            pass
        return pd.DataFrame({'datetime':times, 'value':values})
    
    
    def _parse_temperature_response(self, response):
        values = []
        value_time = datetime.datetime.fromtimestamp(response['body']['home']['beg_time'])
        step = datetime.timedelta(seconds=response['body']['home']['step_time'])
        for value in response['body']['home']['values']:
            values.append([value_time, value])
            value_time = value_time + step
            
    #=================================================================================
    #                      SCHEDULE
    #=================================================================================
    def get_active_schedule(self) -> Schedule:
        for schedule_id in self.schedules_ids:
            if Schedules.items[schedule_id].selected:
                return Schedules.items[schedule_id]
    
    
    def get_schedule_data_for_day(self, day) -> pd.Series:
        return self.get_active_schedule().get_schedule_data_for_room_and_day(self.id, day)
        
        
    def __str__(self):
        return f"""Room: {self.name}
    Type: {self.type}
    Reachable: {self.reachable}
    Heating power request: {self.heating_power_request}
    Setpoint temperature: {self.therm_setpoint_temperature}
    Setpoint mode: {self.therm_setpoint_mode}
    Setpoint start time: {self.therm_setpoint_start_time}
    Setpoint end time: {self.therm_setpoint_end_time}
    """
    
        
class Rooms(Items):
    Item_Obj = Room
    _data_path =  os.path.join(os.path.dirname(__file__), r"temperature_data.csv")
    _timeseries_df = pd.DataFrame()
    _timeseries_types = ['temperature', 'sp_temperature']
    
    def add_home_id(self, home_id):
        for room_id in self.items:
            self.items[room_id].home_id = home_id
            
            
    @classmethod
    def get_timeseries(cls, from_date : datetime.datetime):
        cls._add_timeseries_data_all()
        cls._save_timeseries_data()
        if from_date:
            return cls._timeseries_df.loc[cls._timeseries_df['datime'] > from_date].copy()
        return cls._timeseries_df.copy()
    
    
    @classmethod
    def get_timeseries_for_room_id(cls, room_id : int, from_date : datetime.datetime = None):
        cls._add_timeseries_data_for_room_id(room_id)
        cls._save_timeseries_data()
        if from_date:
            return cls._timeseries_df.loc[(cls._timeseries_df['room_id'] == int(room_id)) & (cls._timeseries_df['datetime'] > from_date)].copy()
        return cls._timeseries_df.loc[cls._timeseries_df['room_id'] == room_id].copy()
            

    @classmethod
    def _save_timeseries_data(cls):
        cls._timeseries_df.drop_duplicates(inplace=True)
        cls._timeseries_df.to_csv(cls._data_path, index=False)
        
        
    @classmethod
    def _check_timeseries_data(cls):
        if cls._timeseries_df.empty:
            cls._load_temperatures_from_file()
            
    
    @classmethod
    def _load_temperatures_from_file(cls):
        try:
            cls._timeseries_df = pd.read_csv(cls._data_path)
        except FileNotFoundError:
            cls._timeseries_df = pd.DataFrame({'room_id':[], 'type':[], 'datetime':[], 'value':[]})
        cls._timeseries_df['datetime'] = pd.to_datetime(cls._timeseries_df['datetime'])
        
    
    @classmethod
    def _add_new_timeseries_data(cls, new_data_df : pd.DataFrame):
        cls._check_timeseries_data()
        cls._timeseries_df = pd.concat([cls._timeseries_df, new_data_df])
            
    
    @classmethod
    def _add_timeseries_data_all(cls):
        for room_id in cls.items:
            cls._add_timeseries_data_for_room_id(room_id)
    
    
    @classmethod
    def _add_timeseries_data_for_room_id(cls, room_id):
        for type in cls._timeseries_types:
            new_data_df = cls._load_new_timeseries_data_for_type(room_id, type)
            cls._add_new_timeseries_data(new_data_df)

    
    @classmethod
    def _load_new_timeseries_data_for_type(cls, room_id, type):
        from_date = cls._get_latest_value_date(room_id, type)
        if (datetime.datetime.now() - from_date) > datetime.timedelta(minutes=30):
            return cls.items[room_id].load_room_timeseries_data(type, from_date)
        
        
    @classmethod
    def _get_latest_value_date(cls, room_id, type) -> datetime.datetime:
        cls._check_timeseries_data()
        filt = (cls._timeseries_df['room_id'] == int(room_id)) & (cls._timeseries_df['type'] == type)
        return cls._timeseries_df.loc[filt, 'datetime'].max()
           
    
    @classmethod
    def get_plot(cls, room_id, from_date : datetime.datetime = None, days = None, plot_type : str = ''):
        if days:
            from_date = datetime.datetime.combine((datetime.datetime.now() - datetime.timedelta(days=days)).date(), datetime.time.min)
        data_df = cls.get_timeseries_for_room_id(room_id, from_date)
        data_df['days'] = (data_df['datetime'].dt.to_pydatetime() - datetime.datetime.min).astype('timedelta64[D]').astype(int)
        data_df['hour'] = data_df['datetime'].dt.hour + data_df['datetime'].dt.minute / 60
        data_df.set_index('hour', inplace=True)
        data_df.sort_index(inplace=True)
        if plot_type == 'cumulative':
            return cls._get_cumulative_plot(data_df, room_id)
        else:
            return cls._get_day_by_day_plot(data_df, from_date, room_id)

        
    @classmethod
    def _get_cumulative_plot(cls, data_df : pd.DataFrame, room_id):
        fig = Figure()
        fig.set_size_inches(20, 10)
        fig.tight_layout()
        fig.subplots_adjust(top=0.95, bottom=0.05)
        axs = fig.subplots(1, 1)
        axs = cls.add_cumulative_axe(axs, data_df, room_id)
        axs = cls.configure_cumulative_axe(axs, data_df)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"
    
    
    @classmethod
    def add_cumulative_axe(cls, axs, data_df : pd.DataFrame, 
                            room_id, color="limegreen", avg_color="green", schedule_color="blue"):
        for _, day_data_df in data_df.groupby('days'):
            week_day = day_data_df['datetime'].min().weekday() + 1
            axs.plot(day_data_df.loc[day_data_df['type'] == 'temperature', ['value']],
                    color=color,
                    linewidth=0.5)
            axs.plot(cls.items[room_id].get_schedule_data_for_day(week_day),
                     color=schedule_color,
                     drawstyle="steps-post",
                     linewidth=4)
        axs.plot(cls._get_average_for_days(data_df),
                 color=avg_color,
                 linewidth=4)
        return axs
    
    
    @classmethod
    def _get_average_for_days(self, data_df : pd.DataFrame) -> pd.DataFrame:
        resampled_df = data_df.loc[data_df['type'] == 'temperature', ['value', 'datetime']].copy()
        resampled_df.set_index('datetime', inplace=True)
        new_index = pd.date_range(resampled_df.index.min(), resampled_df.index.max(), freq='30min')
        resampled_df = resampled_df.reindex(resampled_df.index.union(new_index)).interpolate('index').reindex(new_index)
        resampled_df.index = resampled_df.index.hour + resampled_df.index.minute / 60
        return resampled_df.groupby(resampled_df.index).mean()
    
    
    @classmethod
    def configure_cumulative_axe(cls, axs, data_df : pd.DataFrame):
        axs.set_title("Cumulative")
        axs.title.set_fontsize(28)
        axs.set_xlim([0,24])
        axs.xaxis.set_tick_params(labelsize=20)
        axs.set_xticks(range(0,25))
        axs.set_ylim([data_df['value'].min() - 1, data_df['value'].max() + 1])
        axs.set_yticks(np.arange(data_df['value'].min() // 1, data_df['value'].max() + 1, 0.5))
        axs.yaxis.set_tick_params(labelsize=20)
        axs.grid(True)
        return axs
    
    
    @classmethod
    def _get_day_by_day_plot(cls, data_df : pd.DataFrame, from_date : datetime.datetime, room_id : str):
        number_of_plots = (datetime.datetime.now() - from_date).days + 1 
        fig = Figure()
        fig.set_size_inches(20, (number_of_plots) * 6)
        fig.tight_layout()
        fig.subplots_adjust(hspace=0.2, top=0.99, bottom=0.01)
        axs = fig.subplots(number_of_plots, 1)
        #generate individual plots
        ax_idx = number_of_plots - 1
        for _, day_data_df in data_df.groupby('days'):
            week_day = day_data_df['datetime'].min().weekday() + 1
            axs[ax_idx].plot(day_data_df.loc[day_data_df['type'] == 'temperature', ['value']],
                             color='green',
                             linewidth=4)
            axs[ax_idx].plot(day_data_df.loc[day_data_df['type'] == 'sp_temperature', ['value']],
                             color='red',
                             drawstyle="steps-post",
                             linewidth=4)
            axs[ax_idx].plot(cls.items[room_id].get_schedule_data_for_day(week_day),
                             color='blue',
                             drawstyle="steps-post",
                             linewidth=4)
            axs[ax_idx].set_title(day_data_df['datetime'].dt.to_pydatetime().min().strftime("%A %d.%m.%Y"))
            axs[ax_idx].title.set_fontsize(28)
            axs[ax_idx].set_xlim([0,24])
            axs[ax_idx].xaxis.set_tick_params(labelsize=20)
            axs[ax_idx].set_xticks(range(0,25))
            axs[ax_idx].set_ylim([day_data_df['value'].min() - 1, day_data_df['value'].max() + 1])
            axs[ax_idx].set_yticks(np.arange(day_data_df['value'].min() // 1, day_data_df['value'].max() + 1, 1.0))
            axs[ax_idx].yaxis.set_tick_params(labelsize=20)
            axs[ax_idx].grid(True)
            ax_idx -= 1
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"
