#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases Spring 2022
Webserver for Project 1

Author: Estella Ye (xy2527), Will Wang (hw2869)

"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# Use the DB credentials you received by e-mail
DB_USER = "xy2527"
DB_PASSWORD = "helloworld"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/search_player', Method=["GET"])
def search():
  print(request.args)

  player_name = request.args["player_name"]
  if player_name == "null":
    if request.args["attr"] == "ability":
      query = "SELECT p.username, p.ability FROM Player AS p"
    elif request.args["attr"] == "uid":
      query = "SELECT p.username, p.uid FROM Player AS p"
    elif request.args["attr"] == "wid":
      query = "SELECT p.username, pinw.world_id FROM Player AS p, Player_in_World AS pinw WHERE p.uid == pinw.uid"
    elif request.args["attr"] == "exp":
      query = "SELECT p.username, p.exp FROM Player AS p"
    else:
      query = "SELECT p.username, p.uid, pinw.world_id, p.exp, p.ability FROM Player AS p, Player_in_World AS pinw WHERE p.uid == pinw.uid"
  else:
    if request.args["attr"] == "ability":
      query = "SELECT p.username, p.ability FROM Player AS p"
    elif request.args["attr"] == "uid":
      query = "SELECT p.username, p.uid FROM Player AS p"
    elif request.args["attr"] == "wid":
      query = "SELECT p.username, pinw.world_id FROM Player AS p, Player_in_World AS pinw WHERE p.uid == pinw.uid"
    elif request.args["attr"] == "exp":
      query = "SELECT p.username, p.exp FROM Player AS p"
    else:
      query = "SELECT p.username, p.uid, pinw.world_id, p.exp, p.ability FROM Player AS p, Player_in_World AS pinw WHERE p.uid == pinw.uid"

  cursor = g.conn.execute(query)
  table = []
  for row in cursor:
    table.append(row) 
  cursor.close()
  context = dict(data = table)
  return render_template("index.html", **context)


@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)'
  g.conn.execute(text(cmd), name1 = name, name2 = name)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
