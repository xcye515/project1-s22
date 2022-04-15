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
DB_SERVER = "w4111project1part2db.cisxo09blonu.us-east-1.rds.amazonaws.com"

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

@app.route('/search_player', methods=["GET", "POST"])
def search():
  print(request.args)
  print(request.args["attr"])
  print(request.args["player_name"])
  player_name = request.args["player_name"]
  
  header = []

  if player_name != '':
    player_name_tmp = "%" + player_name + "%"
    if request.args["attr"] == "ability":
      query = text("SELECT p.username, p.ability FROM Player AS p WHERE p.username LIKE '%s'" % player_name_tmp)
    elif request.args["attr"] == "uid":
      query = text("SELECT p.username, p.uid FROM Player AS p WHERE p.username LIKE '%s'" % player_name_tmp)
    elif request.args["attr"] == "wid":
      query = text("SELECT p.username, pinw.world_id FROM Player AS p, Player_in_World as pinw WHERE p.uid = pinw.uid AND p.username LIKE '%s'" % player_name_tmp)
    elif request.args["attr"] == "exp":
      query = text("SELECT p.username, p.exp FROM Player AS p WHERE p.username LIKE '%s'" % player_name_tmp)
    else:
      query = text("SELECT p.username, p.uid, pinw.world_id, p.exp, p.ability FROM Player AS p, Player_in_World AS pinw WHERE p.uid = pinw.uid AND p.username LIKE '%s'" % player_name_tmp)
  else:
    if request.args["attr"] == "ability":
      query = "SELECT p.username, p.ability FROM Player AS p"
    elif request.args["attr"] == "uid":
      query = "SELECT p.username, p.uid FROM Player AS p"
    elif request.args["attr"] == "wid":
      query = "SELECT p.username, pinw.world_id FROM Player AS p, Player_in_World AS pinw WHERE p.uid = pinw.uid"
    elif request.args["attr"] == "exp":
      query = "SELECT p.username, p.exp FROM Player AS p"
    else:
      query = "SELECT p.username, p.uid, pinw.world_id, p.exp, p.ability FROM Player AS p, Player_in_World AS pinw WHERE p.uid = pinw.uid"


  cursor = g.conn.execute(query)
  table = []
  for row in cursor:
    table.append(row) 
  cursor.close()
  context = dict(data = table)
  return render_template("index.html", **context)


@app.route('/add', methods=['GET','POST'])
def add():
  name = request.args['new_player_name']
  uid = request.args['new_uid']
  world_id = request.args['new_world_id']
  exp = request.args['new_exp']
  ability = request.args['new_ability']

  if name == '' or uid == '' or world_id == '' or exp == '' or ability == '':
    message = ["Please do not leave any field blank"]
    context = dict(data = message)
    return render_template("index.html", **context)
  
  check_query = text("SELECT COUNT(*) FROM Player WHERE uid = %s" % uid)
  cursor = g.conn.execute(check_query)
  exists = 0
  for row in cursor:
    exists = row[0]
  cursor.close()

  if exists > 0:
    message = ["Player with the given uid already exists"]
    context = dict(data = message)
    return render_template("index.html", **context)
  
  insert_player_txt = uid + "," + "'" + name + "'" + "," + exp + "," + ability
  insert_player_cmd = text("INSERT INTO Player VALUES (%s);" % insert_player_txt)
  g.conn.execute(insert_player_cmd)

  get_world_coord = text("SELECT upper_x_coord, upper_y_coord FROM World WHERE world_id = %s" % world_id)
  cursor = g.conn.execute(get_world_coord)
  for row in cursor:
    upper_x_coord = row[0]
    upper_y_coord = row[0]
  cursor.close()

  insert_player_inworld = uid + "," + world_id + "," + 1 + "," + 1 + "," + upper_x_coord + "," + upper_y_coord
  insert_player_inworld_cmd = text("INSERT INTO Player_in_World VALUES (%s);" % insert_player_inworld)
  g.conn.execute(insert_player_inworld_cmd)

  message = ["Insert Successful!"]
  context = dict(data = message)
  return render_template("index.html", **context)




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