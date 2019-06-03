from __future__ import absolute_import
from flask import Flask, abort, render_template, json, request, redirect
from test.lib.support_utils import facilities
from datetime import datetime
from .db import make_marker_tables
import logging
import StringIO
import re
import os

APP_NAME = 'marker_work'
r = re.compile("([a-zA-Z]+)([0-9]+)")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def init():
    facilities.setup_app(APP_NAME)
    cfg = facilities.get_default_config()
    return cfg.config_dict


config_dict = init()
TEMPL_DIR = config_dict.get('TEMPL_DIR', '/tmp')
app = Flask(__name__, static_folder=os.path.join(TEMPL_DIR, 'static'),
            template_folder=os.path.join(TEMPL_DIR, 'templates'), instance_path=TEMPL_DIR,
            instance_relative_config=False)


class MarkerException(Exception):
    pass


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/getfile", methods=['GET', 'POST'])
def getfile():
    try:
        if request.method == 'POST':
            result = request.files['myfile']
            in_markers = result.read()
            markers = StringIO.StringIO(in_markers)
            for marker in markers:
                marker_as_string = marker
                marker = marker.split()
                title_validation(marker, marker_as_string)
                asset_validation(marker, marker_as_string)
                type_validation(marker, marker_as_string)
                date_validation(marker, marker_as_string)
        else:
            return
        transfer(in_markers)
        insert_db(in_markers,'SUCCESS')
        #return 'Validation Successful and file has been uploaded'
        return render_template('index.html', success = 'SUCCESS')
    except Exception, e:
        insert_db(in_markers, str(e))
        return render_template('index.html', error=str(e))


def insert_db(markers, status):
    try:
        copy_marker = make_marker_tables().copy_marker
        copy_marker.rec = [markers, status]
        return
    except Exception:
        raise MarkerException("{0} , Problem with inserting data into Marker DB".format(markers))


def transfer(markers):
    try:
        destination_file = config_dict['destination'] + "test.txt"
        file = open(destination_file, 'w')
        file.write(markers)
        file.close()
    except Exception:
        raise MarkerException("{0} , Failed to Upload".format(markers))


def date_validation(marker, marker_as_string):
    try:
        date = datetime.strptime(marker[3], '%m-%d-%Y')
    except ValueError:
        raise MarkerException(" {0} -- Invalid date entered , the format should be mm-dd-yyyy format. {1}".format(marker_as_string, marker[3]))


def title_validation(marker, marker_as_string):
    try:
        if len(marker) >= 7:
            title = marker[0]
            if 1 < len(str(title)) < 100:
                return
            else:
                raise MarkerException("{0} , title has to be btw 1 and 100".format(marker_as_string))
        else:
            raise MarkerException(
                "{0} , Missing Mandatory fields (Title , Asset ID , Material Type, Date , In , Out, In pair or Out "
                "pair) ".format(
                    marker))
    except Exception:
        raise MarkerException("{0} , Please check the title {1}".format(marker_as_string, marker[0]))


def asset_validation(marker, marker_as_string):
    try:
        assetid = marker[1]
        if len(assetid) == 13:
            assets_id = r.match(assetid)
            if len(str(assets_id.group(1))) == 4 and len(assets_id.group(2)) == 9:
                return
            else:
                raise MarkerException("{0} has invalid Asset ID {1}".format(marker_as_string, marker[1]))
        else:
            raise MarkerException("{0} has invalid Asset ID {1}".format(marker_as_string, marker[1]))
    except Exception:
        raise MarkerException("{0} has invalid Asset ID {1}".format(marker_as_string, marker[1]))


def type_validation(marker, marker_as_string):
    try:
        if marker[2] in config_dict['type']:
            return
        else:
            raise MarkerException(
                "{0} , Please check the Material Type and it should match any of these values {1}".format(marker_as_string,
                                                                                                           config_dict[
                                                                                                               'type']))
    except Exception:
        raise MarkerException(
            "{0} , Please check the Material Type and it should match any of these values {1}".format(marker_as_string,
                                                                                                      config_dict[
                                                                                                          'type']))


# Paster Entry Points
def make_app(global_conf={}, debug=False):
    config_dict = init()
    globals().update(config_dict)
    app.config.update(config_dict)
    return app


def make_debug(global_conf={}, **conf):
    return make_app(debug=True)


if __name__ == '__main__':
    # app.debug = True
    app.run()
    # host='0.0.0.0',port=8080
