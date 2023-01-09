import datetime
import pandas as pd
import base64
from io import BytesIO
from matplotlib.figure import Figure

from netatmo.dataModel.rooms import Rooms
from netatmo.dataModel.modules import Modules
from netatmo.dataModel.schedules import Schedules, Schedule
from netatmo.dataModel.items import Items, Item
from netatmo.netatmo_api.netatmo_api import NetatmoApi


class Home(Item):
    def _process_data(self, data: dict):
        self.id = data['id'] if 'id' in data.keys() else None
        self.name = data['name'] if 'name' in data.keys() else None
        self.altitude = data['altitude'] if 'altitude' in data.keys() else None
        self.coordinates = data['coordinates'] if 'coordinates' in data.keys(
        ) else None
        self.country = data['country'] if 'country' in data.keys() else None
        self.timezone = data['timezone'] if 'timezone' in data.keys() else None
        self.temperature_control_mode = data['temperature_control_mode'] if 'temperature_control_mode' in data.keys(
        ) else None
        self.therm_mode = data['therm_mode'] if 'therm_mode' in data.keys(
        ) else None
        self.therm_setpoint_default_duration = data['therm_setpoint_default_duration'] if 'therm_setpoint_default_duration' in data.keys(
        ) else None

        self.schedules_ids = Schedules.add_data(
            self._netatmo_api, data['schedules']) if 'schedules' in data.keys() else None

        self._status_raw = self._get_home_status()
        self.status = self._status_raw['status'] if 'status' in self._status_raw.keys(
        ) else None
        self.time_server = self._status_raw['time_server'] if 'time_server' in self._status_raw.keys(
        ) else None

        try:
            self.modules_ids = Modules.add_data(
                self._netatmo_api, data['modules'], status_data=self._status_raw['body']['home']['modules']) if 'modules' in data.keys() else None
        except KeyError:
            self.modules_ids = Modules.add_data(
                self._netatmo_api, data['modules']) if 'modules' in data.keys() else None

        try:
            self.rooms_ids = Rooms.add_data(
                self._netatmo_api, data['rooms'], status_data=self._status_raw['body']['home']['rooms']) if 'rooms' in data.keys() else None
        except KeyError:
            self.rooms_ids = Rooms.add_data(
                self._netatmo_api, data['rooms']) if 'rooms' in data.keys() else None
        self._add_home_id_and_schdules_to_rooms()
        return

    def _add_home_id_and_schdules_to_rooms(self):
        for room_id in self.rooms_ids:
            Rooms.items[room_id].home_id = self.id
            Rooms.items[room_id].schedules_ids = self.schedules_ids

    def _homestatus_url_data(self) -> dict:
        return {'home_id': self.id}

    def _get_home_status(self):
        return self._netatmo_api.api_request('homestatus', self._homestatus_url_data())

    def get_modules_for_room(self, room_id):
        return [module for module in self.modules_ids.items.values() if module.room_id == room_id]

    def get_active_schedule(self) -> Schedule:
        for schedule_id in self.schedules_ids:
            if Schedules.items[schedule_id].active:
                return Schedules.items[schedule_id]

    # ==========================================================================
    #                             PLOTTING
    # ==========================================================================
    def get_plot(self, from_date: datetime.datetime = None, days=None, plot_type: str = ''):
        if days:
            from_date = datetime.datetime.combine((datetime.datetime.now(
            ) - datetime.timedelta(days=days)).date(), datetime.time.min)
        data_df = Rooms.get_time_series(from_date)
        data_df['days'] = (data_df['datetime'].dt.to_pydatetime(
        ) - datetime.datetime.min).astype('timedelta64[D]').astype(int)
        data_df['hour'] = data_df['datetime'].dt.hour + \
            data_df['datetime'].dt.minute / 60
        data_df.set_index('hour', inplace=True)
        data_df.sort_values('datetime')
        if plot_type == 'cumulative':
            return self._get_cumulative_plot(data_df)
        # else:
        #     return cls._get_day_by_day_plot(data_df, from_date)

    def _get_cumulative_plot(self, data_df: pd.DataFrame):
        colors = {
            'green': 'limegreen',
            'orangered': 'coral',
            'dodgerblue': 'deepskyblue',
            'darkorange': 'orange',
            'navy': 'royalblue',
            'purple': 'violer',
            'godenrod': 'gold',
            'crimson': 'palevioletred'
        }
        num_of_colors = len(colors)
        fig = Figure()
        fig.set_size_inches(20, 10)
        fig.tight_layout()
        fig.subplots_adjust(top=0.95, bottom=0.05)
        axs = fig.subplots(1, 1)
        for color_index, room_id in enumerate(self.rooms_ids):
            room_data_df = data_df.loc[data_df['room_id'] == str(
                room_id)].copy()
            axs = Rooms.add_cumulative_axe(axs, room_data_df, room_id,
                                           color=list(colors.values())[
                                               color_index % num_of_colors],
                                           avg_color=list(colors.keys())[
                                               color_index % num_of_colors],
                                           schedule_color=list(colors.keys())[color_index % num_of_colors])
        axs = Rooms.configure_cumulative_axe(axs, data_df)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"


class Homes(Items):
    Item_Obj = Home
    items = {}

    @staticmethod
    def _get_data(data: dict = None, netatmo_api: NetatmoApi = None):
        data = netatmo_api.api_request('homesdata')
        return data['body']['homes']
