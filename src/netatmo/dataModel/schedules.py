import pandas as pd
import numpy as np
import base64
from io import BytesIO
from matplotlib.figure import Figure

from dataModel.items import Items, Item
from dataModel.zones import Zones

        
class Schedule(Item):
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    def _process_data(self, data : dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.type = data['type'] if 'type' in data.keys() else None
        self.default = data['default'] if 'default' in data.keys() else None
        self.away_temp = data['away_temp'] if 'away_temp' in data.keys() else None
        self.hg_temp = data['hg_temp'] if 'hg_temp' in data.keys() else None
        self.selected = data['selected'] if 'selected' in data.keys() else None
        
        self.zones = Zones(self._netatmo_api, data['zones']) if 'zones' in data.keys() else None
        self.time_table_df = self._process_timetable(data['timetable']) if 'timetable' in data.keys() else None
    
    
    def _process_timetable(self, time_table_data):
        time_table = {}
        for item in time_table_data:
            time_table.update({item['m_offset']:item['zone_id']})
        self.time_table_df = pd.DataFrame({'time_offset':time_table.keys(), 'zone_id':time_table.values()})
        self._add_values_at_days_beginnings_and_ends()
        self._calculate_time_columns()
        self._add_zones_information()
        return self.time_table_df
            

    def _add_values_at_days_beginnings_and_ends(self):
        self.time_table_df = pd.concat([self.time_table_df, pd.DataFrame({'time_offset':[i * 24 * 60 for i in range(1,7)]})])
        self.time_table_df.ffill(inplace=True)
        self.time_table_df = pd.concat([self.time_table_df, pd.DataFrame({'time_offset':[(i * 24 * 60) - 1 for i in range(1,8)]})])
        self.time_table_df.ffill(inplace=True)
        self.time_table_df.drop_duplicates(inplace=True)
        self.time_table_df.sort_values(['time_offset'], inplace=True)
        
        
    def _calculate_time_columns(self):
        self.time_table_df['day'] = self.time_table_df['time_offset'] // 1440 + 1
        self.time_table_df['minute'] = self.time_table_df['time_offset'] % 1440
        self.time_table_df['time'] = self.time_table_df['minute'] / 60
        self.time_table_df['hour'] = self.time_table_df['minute'] // 60
            
            
    def _add_zones_information(self):
        zones = []
        for zone in self.zones.items.values():
            for room_id in zone.rooms:
                zones.append([zone.id, zone.name, room_id, zone.rooms[room_id]])
        self.zones_df = pd.DataFrame(zones)
        self.zones_df.columns = ['zone_id', 'zone_name', 'room_id', 'temperature']
        self.time_table_df = self.time_table_df.merge(self.zones_df, how='left', on='zone_id')
            
            
    #======================================================================
    #                              PLOT
    #======================================================================
    def _get_schedule_data_for_room_and_day(self, room_id, day) -> pd.Series:
        schedule_df = self.time_table_df.loc[(self.time_table_df['room_id'] == room_id) & (self.time_table_df['day'] == day), ['time', 'temperature']].copy()
        schedule_df.set_index('time', inplace=True)
        return schedule_df['temperature']
    
    
    
    def get_schedule_plot(self, room_id):
        # Generate the figure **without using pyplot**.,
        fig = Figure()
        fig.set_size_inches(6, 18)
        fig.tight_layout()
        fig.subplots_adjust(hspace=0.5, top=0.98, bottom=0.02)
        axs = fig.subplots(7,1)
        for idx, ax in enumerate(axs):
            data_s = self._get_schedule_data_for_room_and_day(room_id, idx + 1)
            ax.plot(data_s,
                    drawstyle="steps-post",
                    linewidth=4)
            ax.set_title(self.week_days[idx])
            ax.title.set_fontsize(18)
            ax.set_xlim([0,24])
            ax.xaxis.set_tick_params(labelsize=15)
            ax.set_ylim([data_s.min() - 1, data_s.max() + 1])
            ax.set_yticks(np.arange(data_s.min() // 1, data_s.max() + 1, 1.0))
            ax.yaxis.set_tick_params(labelsize=15)
            ax.grid()
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"
    
    
    def __str__(self):
        return f"""Name: {self.name}
    Selected: {self.selected}
    """
        

class Schedules(Items):
    Item_Obj = Schedule

    def get_data(self):
        pass