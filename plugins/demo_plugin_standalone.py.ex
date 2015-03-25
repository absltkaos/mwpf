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
