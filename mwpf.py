#!/usr/bin/python
# vim:set et ts=4 sw=4:

import ConfigParser
import time
import os
import sys

CONFIG=''
DEFAULT_CONFIG="/etc/mwpf/mwpf.conf"
conf_req={ 'global': ['project_path','plugins_path', 'libs_path' ] }
plugins={}
conf_defaults={
        "listen_address": "0.0.0.0",
        "listen_port": "8080",
        "daemonize": True,
        "pid_file": '/var/run/mwpf.pid'
}
logging_defaults={
        "type": "stdout",
        "level": "NOTSET",
        "format": "",
        "date_format": "",
        "filelog_destination": None,
        "filelog_size_rotate_bytes": 52428800,
        "filelog_rotate_num": 7,
        "syslog_address": "/dev/log",
        "syslog_facility": "user",
        "syslog_proto": "udp",
        "syslog_identifier": ""
}
loggers={
        "app": {},
        "request": {}
}

#-- Some supporting functions --#
def load_logging_conf(conf,conf_section):
    #Load the default options
    logging_conf=dict(logging_defaults)
    #Override any from our config
    for opt in logging_defaults.keys():
        try:
            logging_conf[opt]=conf.get(conf_section,opt)
        except:
            pass
    #Return the merged logging config
    return logging_conf

def initLogger(logging_conf,logger_name):
    import logging
    import logging.handlers
    import socket
    logging_type=logging_conf['type']
    logger=logging.getLogger(logger_name)
    log_formatter=None
    if logging_conf['format'] or logging_conf['date_format']:
        log_formatter=logging.Formatter(logging_conf['format'],logging_conf['date_format'])
    #Set up our different kinds of loggers
    if logging_type in ("stdout","console"):
        #For stdout/console logging
        logging_handler=logging.StreamHandler(sys.stdout)
    elif logging_type == "file":
        #For logging to a file
        if not logging_conf['filelog_destination']:
            raise RuntimeError("Logging to a file must have a filelog_destination")
        logging_handler=logging.handlers.RotatingFileHandler(logging_conf['filelog_destination'], maxBytes=logging_conf['filelog_size_rotate_bytes'], backupCount=logging_conf['filelog_rotate_num'])
    elif logging_type == "syslog":
        #For logging to syslog
        pot_addr=logging_conf['syslog_address']
        addr=pot_addr
        socktype=socket.SOCK_DGRAM
        if ':' in pot_addr:
            addr_split=pot_addr.split(':')
            port=int(addr_split[1])
            addr=(addr_split[0],port)
        if logging_conf['syslog_proto'] == "tcp":
            socktype=socket.SOCK_STREAM
        facility=logging_conf['syslog_facility']
        logging_handler=logging.handlers.SysLogHandler(address=addr,facility=facility,socktype=socktype)
        if logging_conf['syslog_identifier']:
            if not logging_conf['format']:
                log_formatter=logging.Formatter("%s: %%(message)s" % (logging_conf['syslog_identifier']),logging_conf['date_format'])
            else:
                log_formatter=logging.Formatter("%s: %s" % (logging_conf['syslog_identifier'],logging_conf['format']),logging_conf['date_format'])
    else:
        #Unknown logging type
        raise ValueError("Unknown logging type: %s" % logging_type)
    #Set logging formatter
    if log_formatter:
        logging_handler.setFormatter(log_formatter)
    #Set logging level
    logger.setLevel(logging_conf['level'].upper())
    #Add the logging handler type
    logger.addHandler(logging_handler)
    return logger

#-- Do some initial setup --#

if len(sys.argv) > 1:
    CONFIG=sys.argv[1]
if CONFIG:
    REAL_CONFIG=CONFIG
else:
    REAL_CONFIG=DEFAULT_CONFIG

conf = ConfigParser.RawConfigParser()
#Make our config case sensitive
conf.optionxform = str

if conf.read((REAL_CONFIG)) == []:
    print('Could not load config from DEFAULT_CONFIG(%s) or User Supplied CONFIG(%s)' % (DEFAULT_CONFIG,CONFIG))
    sys.exit(1)

#Check that our config has all our required things:
config=dict(conf_defaults)
for section in conf_req.keys():
    for opt in conf_req[section]:
        if not conf.has_option(section,opt):
            print("Missing required option in config file(%s): Section %s Var %s" % (REAL_CONFIG,section,opt))
            sys.exit(2)
        else:
            config[opt]=conf.get(section,opt)
#Set any config global defaults
for opt in conf_defaults.keys():
    try:
        if opt == "daemonize":
            config[opt]=conf.getboolean('global',opt)
        else:
            config[opt]=conf.get('global',opt)
    except:
        pass

#Read conf for any environment variables to set.
if conf.has_section('environment'):
    for v in conf.options('environment'):
        os.environ[v]=conf.get('environment',v)

project_path=conf.get('global','project_path')
plugins_path=conf.get('global','plugins_path')
libs_path=conf.get('global','libs_path')
#Insert our libs path into our path
sys.path.insert(0,libs_path)

#Daemonize as needed
if config['daemonize']:
    import daemon
    import daemon.pidfile
    pidfile=daemon.pidfile.PIDLockFile(config['pid_file'])
    daemon_ctx = daemon.DaemonContext(
            working_directory=project_path,
            pidfile=pidfile,
            detach_process=True)
    daemon_ctx.open()

#Set up loggers
loggers["request"]["config"]=load_logging_conf(conf,"request_logging")
loggers["request"]["logger"]=initLogger(loggers["request"]["config"],"request")
loggers["app"]["config"]=load_logging_conf(conf,"application_logging")
loggers["app"]["logger"]=initLogger(loggers["app"]["config"],"app")

#Load up modules that are in our own libs dir
from bottle import Bottle, template
import dynamic_table

#Redirect console output to loggers
from file_logger import FileLogger
sys.stderr=FileLogger(loggers['app']['logger'],40)
sys.stdout=FileLogger(loggers['app']['logger'],20)

#Create new Bottle Object
main_app = Bottle()

#Load our main routes
@main_app.route('/')
@main_app.route('/index.html')
def callback():
    t=dynamic_table.Table(dynamic_table.RenderHTML(table_attr="class=\"table\""))
    t.set_col_names(['Report Plugin','Description'])
    for p in plugins.keys():
        t.add_row([ '<a href="/%s">%s</a>' % (plugins[p]['mount'],plugins[p]['name']), plugins[p]['descr'] ])
    t_data=str(t)
    del(t)
    return template("""<!DOCTYPE html>
<html>
<head>
    <title>Menu of loaded report plugins</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container">
    <h3>Loaded plugins</h3>
    {{!table_data}}
</div>
</body>
</html>""", table_data=t_data)

#Load plugins
if not os.path.isdir(plugins_path):
    print('ERROR: %s path is not a directory os does not exist' % (path))
    sys.exit(2)

#Create a Dict that will be passed to the plugins "init" function.
conf_dict={
    'logger': loggers["app"]["logger"],
    'conf': conf
}
sys.path.append(plugins_path)
for f in os.listdir(os.path.abspath(plugins_path)):
    plug_name, ext = os.path.splitext(f)
    if ext == '.py':
        try:
            plugin = __import__(plug_name)
            #Init the plugin
            plugin_app=plugin.init(conf_dict)
            #Mount the plugin
            main_app.mount(plugin.mount_point,plugin_app)
            #Register the loaded plugin with our plugins dict
            plugins[plug_name] = { 'mount': plugin.mount_point, 'descr': plugin.descr, 'name': plugin.name, 'plugin_app': plugin_app, 'plugin': plugin }
        except:
            print("ERROR: Doh, problems occured loading plugin: %s" % (plug_name))
            raise

#-- Begin running --#
if __name__ == '__main__':
    print("Starting Application")
    listen_address=config['listen_address']
    listen_port=config['listen_port']
    from paste import httpserver
    from paste.translogger import TransLogger
    main_app = TransLogger(main_app, logger=loggers['request']['logger'])
    httpserver.serve(main_app,host=listen_address,port=listen_port)
