from ConfigParser import SafeConfigParser
from cloudmesh.inventory.inventory import FabricImage, FabricServer, \
    FabricService, Inventory
from cloudmesh.util.webutil import setup_imagedraw, setup_plugins, setup_noderenderers
from cloudmesh.provisioner.provisioner import *
from cloudmesh.util.util import table_printer
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory
from flask.ext.autoindex import AutoIndex
from flask.ext.wtf import Form
from flask_flatpages import FlatPages
from hostlist import expand_hostlist
from modules.workflow import workflow_module
from modules.flatpages import flatpages_module
from modules.inventory import inventory_module
from modules.provisioner import provisioner_module
from modules.keys import keys_module
from modules.menu import menu_module
from modules.profile import profile_module
from modules.view_git import git_module
from os.path import isfile, join
from pprint import pprint
from wtforms import TextField, SelectField
import base64
import hashlib
import json
import os
import pkg_resources
import struct
import sys
import time
import types
import yaml


debug = False


with_cloudmesh = False

sys.path.insert(0, '.')
sys.path.insert(0, '..')


server_config = SafeConfigParser(
    {'name': 'flasktest'})  # Default database name
server_config.read("server.config")




if with_cloudmesh:
    from cloudmesh.config.cm_keys import cm_keys
    from cloudmesh.config.cm_projects import cm_projects
    from cloudmesh.config.cm_config import cm_config
    from cloudmesh.cloudmesh import cloudmesh

# from menu.server_keys import menu_module



try:
    from sh import xterm
except:
    print "xterm not suppported"

    # TODO: THERE SHOULD BE A VARIABLE SET HERE SO THAT THE ARROW
    # START UP BUTTON CAN RETURN MEANINGFULL MESSAGE IF NOT SUPPORTED


# ============================================================
# allowing the yaml file to be written back upon change
# ============================================================
with_write = True

# ============================================================
# setting up reading path for the use of yaml
# ============================================================

default_path = '.futuregrid/cloudmesh.yaml'
home = os.environ['HOME']
filename = "%s/%s" % (home, default_path)

# ============================================================
# global vars
# ============================================================

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

version = pkg_resources.get_distribution("cloudmesh").version


# ============================================================
# CLOUDMESH
# ============================================================

if with_cloudmesh:

    config = cm_config()
    configuration = config.get()
    prefix = config.prefix
    index = config.index

    clouds = cloudmesh()
    # refresh, misses the search for display

    clouds.refresh()
    clouds.refresh_user_id()

    # clouds.load()
    # clouds.refresh("openstack")
    # clouds.clouds

    # DEFINING A STATE FOR THE CHECKMARKS IN THE TABLE

    """
    for name in clouds.active():

            config.data['cloudmesh']['clouds']

    for name in clouds.active():
        try:
            a = config.data['cloudmesh']['clouds'][name]['default']['filter']['state']
            print "- filter exist for cloud", name
        except:
            config.create_filter(name, clouds.states(name))
            config.write()
    """

    print config

    clouds.all_filter()




# pp.pprint (pages.__dict__['app'].__dict__)

# ============================================================
# STARTING THE FLASK APP
# ============================================================

app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True
pages = FlatPages(app)
app.register_blueprint(keys_module, url_prefix='',)
app.register_blueprint(inventory_module, url_prefix='',)
app.register_blueprint(provisioner_module, url_prefix='',)
app.register_blueprint(git_module, url_prefix='',)
app.register_blueprint(profile_module, url_prefix='',)
app.register_blueprint(menu_module, url_prefix='',)
app.register_blueprint(flatpages_module, url_prefix='',)
app.register_blueprint(workflow_module, url_prefix='',)


SECRET_KEY = 'development key'
app.secret_key = SECRET_KEY

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))
            
# @app.context_processor
# def inject_pages():
#    return dict(pages=pages)
# app.register_blueprint(menu_module, url_prefix='/', )
if debug:
    AutoIndex(app, browse_root=os.path.curdir)

# ============================================================
# VESRION
# ============================================================


@app.context_processor
def inject_version():
    return dict(version=version)


# ============================================================
# ROUTE: sitemap
# ============================================================

"""
@app.route("/site-map/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        print"PPP>",  rule, rule.methods, rule.defaults, rule.endpoint, rule.arguments
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        try:
            if "GET" in rule.methods and len(rule.defaults) >= len(rule.arguments):
                url = url_for(rule.endpoint)
                links.append((url, rule.endpoint))
                print "Rule added", url, links[url]
        except:
            print "Rule not activated"
    # links is now a list of url, endpoint tuples
"""


# ============================================================
# ROUTE: /
# ============================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/workflow')
def display_diagram():
    return render_template('workflow.html')


# ============================================================
# ROUTE: REFRESH
# ============================================================
@app.route('/cm/refresh/')
@app.route('/cm/refresh/<cloud>/')
def refresh(cloud=None, server=None):
    # print "-> refresh", cloud, server
    clouds.refresh()
    clouds.all_filter()
    return table()

# ============================================================
# ROUTE: Filter
# ============================================================


@app.route('/cm/filter/<cloud>/', methods=['GET', 'POST'])
def filter(cloud=None):
    # print "-> filter", cloud

    #
    # BUG: when cloud is none
    #
    name = cloud
    if request.method == 'POST':
        query_states = []
        state_table = {}
        for state in clouds.states(name):
            state_name = "%s:%s" % (name, state)
            state_table[state] = state_name in request.form
            if state_table[state]:
                query_states.append(state)
        config.set_filter(name, state_table, 'state')

        clouds.state_filter(name, query_states)

    return redirect("/table/")


# ============================================================
# ROUTE: KILL
# ============================================================
@app.route('/cm/kill/')
def kill_vms():
    print "-> kill all"
    r = cm("--set", "quiet", "kill", _tty_in=True)
    return table()

# ============================================================
# ROUTE: DELETE
# ============================================================


@app.route('/cm/delete/<cloud>/<server>/')
def delete_vm(cloud=None, server=None):
    print "-> delete", cloud, server
    # if (cloud == 'india'):
    #  r = cm("--set", "quiet", "delete:1", _tty_in=True)
    clouds.delete(cloud, server)
    time.sleep(5)
    #    clouds.refresh()
    return redirect("/table/")
#    return table()

# ============================================================
# ROUTE: DELETE GROUP
# ============================================================


@app.route('/cm/delete/<cloud>/')
def delete_vms(cloud=None):
# donot do refresh before delete, this will cause all the vms to get deleted
    f_cloud = clouds.clouds[cloud]
    for id, server in f_cloud['servers'].iteritems():
        print "-> delete", cloud, id
        clouds.delete(cloud, id)
    time.sleep(7)
    f_cloud['servers'] = {}
    return redirect("/table/")


# ============================================================
# ROUTE: ASSIGN PUBLIC IP
# ============================================================


@app.route('/cm/assignpubip/<cloud>/<server>/')
def assign_public_ip(cloud=None, server=None):
    try:
        if configuration['clouds'][cloud]['cm_automatic_ip'] is False:
            clouds.assign_public_ip(cloud, server)
            clouds.refresh(names=[cloud])
            return redirect("/table/")
        else:
            return "Manual public ip assignment is not allowed for %s cloud" % cloud
    except Exception, e:
        return str(e) + "Manual public ip assignment is not allowed for %s cloud" % cloud

# ============================================================
# ROUTE: START
# ============================================================

#
# WHY NOT USE cm_keys as suggested?
#


@app.route('/cm/start/<cloud>/')
def start_vm(cloud=None, server=None):
    print "*********** STARTVM", cloud
    print "-> start", cloud
    # if (cloud == 'india'):
    #  r = cm("--set", "quiet", "start:1", _tty_in=True)
    key = None

    if configuration.has_key('keys'):
        key = configuration['keys']['default']

    # THIS IS A BUG
    vm_flavor = clouds.default(cloud)['flavor']
    vm_image = clouds.default(cloud)['image']

    print "STARTING", config.prefix, config.index
    result = clouds.create(
        cloud, config.prefix, config.index, vm_image, vm_flavor, key)
    # print "PPPPPPPPPPPP", result
    clouds.vm_set_meta(cloud, result['id'], {'cm_owner': config.prefix})
    config.incr()
    config.write()

    return table()

'''
#gregors test
@app.route('/cm/metric/<startdate>/<enddate>/<host>')
def list_metric(cloud=None, server=None):
    print "-> generate metric", startdate, endadte
    #r = fg-metric(startdate, enddate, host, _tty_in=True)
    return render_template('metric1.html',
                           startdate=startdate,
                           endate=enddate)
    #return table()
'''

# ============================================================
# ROUTE: SAVE
# ============================================================


@app.route('/save/')
def save():
    print "Saving the cloud status"
    clouds.save()
    return table()

# ============================================================
# ROUTE: LOAD
# ============================================================


@app.route('/load/')
def load():
    print "Loading the cloud status"
    clouds.load()
    return table()

# ============================================================
# ROUTE: TABLE
# ============================================================


@app.route('/table/')
def table():
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    filter()
    return render_template('table.html',
                           updated=time_now,
                           keys="",  # ",".join(clouds.get_keys()),
                           cloudmesh=clouds,
                           clouds=clouds.clouds,
                           config=config)


# ============================================================
# ROUTE: VM Login
# ============================================================


@app.route('/cm/login/<cloud>/<server>/')
def vm_login(cloud=None, server=None):
    message = ''
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    server = clouds.clouds[cloud]['servers'][server]

    if len(server['addresses'][server['addresses'].keys()[0]]) < 2:
        mesage = 'Cannot Login Now, Public IP not assigned'
        print message

    else:
        message = 'Logged in Successfully'
        ip = server['addresses'][server['addresses'].keys()[0]][1]['addr']
        # THIS IS A BUG AND MUST BE SET PER VM, E.G. sometimesvm type probably
        # decides that?
        print "ssh", 'ubuntu@' + ip
        xterm('-e', 'ssh', 'ubuntu@' + ip, _bg=True)

    return redirect("/table/")
# ============================================================
# ROUTE: VM INFO
# ============================================================


@app.route('/cm/info/<cloud>/<server>/')
def vm_info(cloud=None, server=None):

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    clouds.clouds[cloud]['servers'][server]['cm_vm_id'] = server
    clouds.clouds[cloud]['servers'][server]['cm_cloudname'] = cloud

    return render_template('vm_info.html',
                           updated=time_now,
                           keys="",
                           server=clouds.clouds[cloud]['servers'][server],
                           id=server,
                           cloudname=cloud,
                           table_printer=table_printer)

# ============================================================
# ROUTE: FLAVOR
# ============================================================

# @app.route('/flavors/<cloud>/' )


@app.route('/flavors/', methods=['GET', 'POST'])
def display_flavors(cloud=None):

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if request.method == 'POST':
        for cloud in config.active():
            configuration['clouds'][cloud]['default'][
                'flavor'] = request.form[cloud]
            config.write()

    return render_template(
        'flavor.html',
        updated=time_now,
        cloudmesh=clouds,
        clouds=clouds.clouds,
        config=config)


# ============================================================
# ROUTE: IMAGES
# ============================================================
# @app.route('/images/<cloud>/')
@app.route('/images/', methods=['GET', 'POST'])
def display_images():
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if request.method == 'POST':
        for cloud in config.active():
            configuration['clouds'][cloud][
                'default']['image'] = request.form[cloud]
            config.write()

    return render_template(
        'images.html',
        updated=time_now,
        clouds=clouds.clouds,
        cloudmesh=clouds,
        config=config)

@app.template_filter()
def timesince(dt, format="float", default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if dt == "None" or dt == "" or dt == None or dt == "completed":
        return "completed"
    
    #now = datetime.utcnow()
    now = datetime.now()
    if format == 'float':
        diff = now - datetime.fromtimestamp(dt)
    else:
        diff = now - dt
        
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default

@app.template_filter()
def get_tuple_element_from_string(obj,i):
    l = obj[1:-1].split(", ")
    return l[i][1:-1]

@app.template_filter()
def is_list(obj):
    return isinstance(obj, types.ListType)

@app.template_filter()
def only_numbers(str):
    return ''.join(c for c in str if c.isdigit())

@app.template_filter()
def simple_date(d):
    return str(d).rpartition(':')[0]


@app.template_filter()
def state_color(state):
    s = state.lower()
    if s == "active":
        color = "#336600"
    else:
        color = "#FFCC99"
    return color

@app.template_filter()
def state_style(state):
    color = state_color(state)
    return 'style="background:{0}; font:bold"'.format(color)



# ============================================================
# ROUTE: METRIC
# ============================================================
# @app.route('/metric/<s_date>/<e_date>/<user>/<cloud>/<host>/<period>/<metric>')
@app.route('/metric/main', methods=['POST', 'GET'])
def metric():
    args = {"s_date": request.args.get('s_date', ''),
            "e_date": request.args.get('e_date', ''),
            "user": request.args.get('user', ''),
            "cloud": request.args.get('cloud', ''),
            "host": request.args.get('host', ''),
            "period": request.args.get('period', ''),
            "metric": request.args.get('metric', '')}

    return render_template('metric.html',
                           clouds=clouds.get(),
                           metrics=clouds.get_metrics(args))

# ============================================================
# ROUTE: PAGES
# ============================================================



@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)


@app.route('/workflows/<filename>')
def retrieve_files(filename):
    """    Retrieve files that have been uploaded    """
    return send_from_directory('workflows',filename)

if __name__ == "__main__":
    setup_imagedraw()
    #setup_plugins()
    #setup_noderenderers()
    app.run()
