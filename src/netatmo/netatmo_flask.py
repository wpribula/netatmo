import sys, os
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, redirect, request, render_template

from netatmo.netatmo_api.netatmo_api import NetatmoApi
from netatmo.dataModel.netatmo_data import NetatmoData
from netatmo.dataModel.rooms import Rooms
from netatmo.dataModel.homes import Homes


app = Flask("Netatmo", 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'), 
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))
netatmo_api = NetatmoApi()
data = NetatmoData()


@app.route("/")
def login():
    if netatmo_api.is_authenticated():
        return redirect('/home/')
    else:
        return redirect(netatmo_api.get_netatmo_login_page_url())
    
@app.route("/home/")
def home():
    return render_template('index.j2', 
                           simple = False,
                           data=data.load_data(netatmo_api))


@app.route("/token/")
def token():
    state  = request.args.get('state', None)
    code  = request.args.get('code', None)
    netatmo_api.new_token(code)
    return redirect('/home/')


@app.route("/plot/<string:item_type>/<string:plot_type>/<string:item_id>/<int:days>")
def plot(item_type, plot_type, item_id, days):
    data.load_data(netatmo_api)
    if item_type == 'room':
        return render_template('plot.j2', 
                               room_id = item_id, 
                               home_id = Rooms.items[item_id].home_id,
                               item_type = item_type,
                               simple = True,
                               data = data.load_data(netatmo_api),
                               plot_data=Rooms.get_plot(item_id, days=days, plot_type=plot_type))
    elif item_type == 'home':
        return render_template('plot.j2', 
                               home_id = item_id, 
                               item_type = item_type,
                               simple = True,
                               data = data.load_data(netatmo_api),
                               plot_data=Homes.items[item_id].get_plot(days=days, plot_type=plot_type))


if __name__ == "__main__":
    app.run(port=80)