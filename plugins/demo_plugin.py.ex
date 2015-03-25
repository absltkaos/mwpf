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
