import sys, os
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, redirect, request, render_template

from netatmo.netatmo_api.netatmo_api import NetatmoApi
from netatmo.dataModel.netatmo_data import NetatmoData


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
    return render_template('index.j2', homes=data.get_homes_data(netatmo_api))


@app.route("/token/")
def token():
    state  = request.args.get('state', None)
    code  = request.args.get('code', None)
    netatmo_api.new_token(code)
    return redirect('/home/')
    

if __name__ == "__main__":
    app.run(port=80)