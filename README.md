# mwpf
A Micro Web Plugin Framework based on Bottle. For standing up multiple web pages within a Bottle application.

This was initially created because I wanted a way to quickly stand up some reporting webpages, and other small web applications. There really was no need for a larger framework like Django. So this was born.

# Requirements
MWPF depends on the following external python modules:

1. [bottle](http://bottlepy.org/docs/dev/index.html) - For the WSGI application
  * Tested with 0.13-dev
1. [daemon](https://pypi.python.org/pypi/python-daemon) - For allowing MWPF to run as a daemon
  * Tested with 2.0.5 (This version requires at least [lockfile](https://pypi.python.org/pypi/lockfile) 0.9)
1. [dynamic_table](https://github.com/absltkaos/python-dynamic-table) - For building and rendering table in text and HTML
  * Tested with 0.8.7
1. [paste](https://bitbucket.org/ianb/paste) - For the actual WSGI server
  * Tested with 1.7.5 (https://pypi.python.org/pypi/Paste)

All of the above requirements can be placed locally within MWPF's "libs/" directory, for inclusion if versions needed aren't available for your platorm

# How it works
1. Uses the python bottle micro framework to create a WSGI Bottle application.
1. It then looks through the 'plugins' directory to find some plugins/webapps. MWPF calls the plugin's 'init' function and passes it a dictionary with a ConfigParser object (with the key 'conf') and a python 'logging' object (With the key 'logger'). The plugin can use the information or not... it doesn't matter
1. After a successful init call, the plugin is mounted using Bottle to a specific mount point, and starts listening for requests using the Paste server.

# Plugin Format
The format of a plugin is pretty straight forward,  First it has to be a file with the '.py' extension and within the 'plugins' directory. Then it just has a couple of variables, and an init function that returns a Bottle object.

## Required Variables
```
mount_point
descr
name
```

The 'name' and 'descr' are what will be presented when browsing to the listening port of MWPF.

The 'mount_point' will be the name of the mount for the plugin to be reached at in the URL.


## Required functions
```
init(dict)
```
There also has to be an "init" function, that can take a single parameter which is a Dictionary.
The dictionary currently only has two keys:
```
conf
logger
```

'conf' is a ConfigParser object. This is so you can choose to have your plugin's configuration in the main mwpf.conf as well.
'logger' is a python logger object

This init function MUST return a "bottle" object.

## Example plugin ##
```python
from bottle import Bottle

mount_point='demo'
descr="Demo plugin to show how plugins work"
name="Demo Plugin"

def init(conf):
  #We don't care about "conf" in this demo so don't do anything with it.
  
  #Create a Bottle object
  app=Bottle()

  #Add some routes
  @app.route("/")
  def callback():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Demo Landing Page</title>
</head>
<body>
  Welcome! This is a demo Landing Page. Here are is a link: <br />
  <a href="/%s/page1">Page 1</a> <br />
</body>
</html>
""" % (mount_point)

  @app.route("/page1")
  def callback():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Page 1</title>
</head>
<body>
  Welcome to Page 1!<br />
</body>
</html>
"""

  #Return our Bottle object
  return app
```

Then just run run mwpf.py pointed at your mwpf.conf
```
./mwpf.py mwpf.conf
```

And open a browser to where mwpf was configure to listen:
![Loaded up plugins](https://raw.githubusercontent.com/absltkaos/mwpf/master/images/loaded_demo.png)

## Example plugin that can also run as a standalone app WITHOUT MWPF
One of the nice things about using Bottle, is you could potentially develop the pluging outside of the MWPF framwork, and add it in as a plugin later. Here is the same example that is above, but written so it could also be run by itself:
```python
#!/usr/bin/python
from bottle import Bottle

mount_point='demo'
descr="Demo plugin to show how plugins work"
name="Demo Plugin"
mount_point_href="/%s" %(mount_point)

def init(conf):
  #We don't care about "conf" in this demo so don't do anything with it.
  
  #Create a Bottle object
  app=Bottle()

  #Add some routes
  @app.route("/")
  def callback():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Demo Landing Page</title>
</head>
<body>
  Welcome! This is a demo Landing Page. Here are is a link: <br />
  <a href="%s/page1">Page 1</a> <br />
</body>
</html>
""" % (mount_point_href)

  @app.route("/page1")
  def callback():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Page 1</title>
</head>
<body>
  Welcome to Page 1!<br />
</body>
</html>
"""

  #Return our Bottle object
  return app

###-Main-###
if __name__ == "__main__":
    #We aren't being imported, so try and run as a standalone app
    from bottle import run

    mount_point_href=""

    bottle_app=init('')
    run(bottle_app,host='0.0.0.0', port=8080, server='paste', debug=True)
```

Then you can either drop the file in plugins, and let mwpf mount it at "demo" or execute the file with the python interpreter and have it run as it's own bottle application
