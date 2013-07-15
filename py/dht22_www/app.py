# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template
from daemon import SpreadsheetHandler
from utils import DataKeeper

STATIC_FILE_ROOT = os.path.join(os.path.dirname(__file__), 'static')


app = Flask(__name__, static_folder=STATIC_FILE_ROOT)
"""An application object"""

@app.before_request
def before_request():
    """ Creating a DataKeeper object.
    Still don't works as should"""
    #dk = DataKeeper(40)
    #app.data_storange = dk

@app.route("/")
def index():
    """Render the template"""
    return render_template('templates/index.html')


def create_app():
    return app
