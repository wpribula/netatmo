from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.defaulttags import register

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'src'))

from netatmo.netatmo_api.netatmo_api import NetatmoApi
from netatmo.dataModel.netatmo_data import NetatmoData
from netatmo.dataModel.rooms import Rooms
from netatmo.dataModel.homes import Homes

netatmo_api = NetatmoApi()
data = NetatmoData()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def home(request):
    return render(request, 'home/index.html', {'data' : data.load_data(netatmo_api)})


def token(request):
    state  = request.args.get('state', None)
    code  = request.args.get('code', None)
    netatmo_api.new_token(code)
    return redirect('/home/')


# def plot(request, item_type, plot_type, item_id, days):
#     data.load_data(netatmo_api)
    # if item_type == 'room':
    #     return render_template('plot.j2', 
    #                            room_id = item_id, 
    #                            home_id = Rooms.items[item_id].home_id,
    #                            item_type = item_type,
    #                            simple = True,
    #                            data = data.load_data(netatmo_api),
    #                            plot_data=Rooms.get_plot(item_id, days=days, plot_type=plot_type))
    # elif item_type == 'home':
    #     return render_template('plot.j2', 
    #                            home_id = item_id, 
    #                            item_type = item_type,
    #                            simple = True,
    #                            data = data.load_data(netatmo_api),
    #                            plot_data=Homes.items[item_id].get_plot(days=days, plot_type=plot_type))