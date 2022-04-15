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
#DB_SERVER = "w4111project1part2db.cisxo09blonu.us-east-1.rds.amazonaws.com"

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
def search_player():
  print(request.args)
  player_name = request.args["player_name"]
  
  header = []

  if player_name != '':
    player_name_tmp = "%" + player_name + "%"
    if request.args["attr"] == "ability":
      header = ['Username', 'Ability']
      query = text("SELECT p.username, p.ability FROM Player AS p WHERE p.username LIKE '%s'" % player_name_tmp)
    elif request.args["attr"] == "uid":
      header = ['Username', 'UID']
      query = text("SELECT p.username, p.uid FROM Player AS p WHERE p.username LIKE '%s'" % player_name_tmp)
    elif request.args["attr"] == "wid":
      header = ['Username', 'World ID']
      query = text("SELECT p.username, pinw.world_id FROM Player AS p, Player_in_World as pinw WHERE p.uid = pinw.uid AND p.username LIKE '%s'" % player_name_tmp)
    elif request.args["attr"] == "exp":
      header = ['Username', 'EXP Point']
      query = text("SELECT p.username, p.exp FROM Player AS p WHERE p.username LIKE '%s'" % player_name_tmp)
    else:
      header = ['Username', 'UID', 'World ID', 'EXP Point', 'Ability']
      query = text("SELECT p.username, p.uid, pinw.world_id, p.exp, p.ability FROM Player AS p, Player_in_World AS pinw WHERE p.uid = pinw.uid AND p.username LIKE '%s'" % player_name_tmp)
  else:
    if request.args["attr"] == "ability":
      header = ['Username', 'Ability']
      query = "SELECT p.username, p.ability FROM Player AS p"
    elif request.args["attr"] == "uid":
      header = ['Username', 'UID']
      query = "SELECT p.username, p.uid FROM Player AS p"
    elif request.args["attr"] == "wid":
      header = ['Username', 'World ID']
      query = "SELECT p.username, pinw.world_id FROM Player AS p, Player_in_World AS pinw WHERE p.uid = pinw.uid"
    elif request.args["attr"] == "exp":
      header = ['Username', 'EXP Point']
      query = "SELECT p.username, p.exp FROM Player AS p"
    else:
      header = ['Username', 'UID', 'World ID', 'EXP Point', 'Ability']
      query = "SELECT p.username, p.uid, pinw.world_id, p.exp, p.ability FROM Player AS p, Player_in_World AS pinw WHERE p.uid = pinw.uid"


  cursor = g.conn.execute(query)
  table = []
  table.append(header)
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


  insert_player_inworld = uid + "," + world_id + "," + str(1) + "," + str(1) + "," + str(upper_x_coord) + "," + str(upper_y_coord)
  insert_player_inworld_cmd = text("INSERT INTO Player_in_World VALUES (%s);" % insert_player_inworld)
  
  g.conn.execute(insert_player_inworld_cmd)
  message = ["Insert Successful!"]
  context = dict(data = message)
  return render_template("index.html", **context)

@app.route('/modify', methods=['GET', 'POST'])
def modify():
  uid = request.args['exist_uid']
  exp = request.args['exist_exp']

  if uid == '' or exp == '':
    message = ["Please do not leave any field blank"]
    context = dict(data=message)
    return render_template("index.html", **context)

  check_query = text("SELECT COUNT(*) FROM Player WHERE uid = %s" % uid)
  cursor = g.conn.execute(check_query)
  exists = 0
  for row in cursor:
    exists = row[0]
  cursor.close()

  if exists == 0:
    message = ["Player with the given uid does not exist. If you want to add this player, please use the add player function."]
    context = dict(data=message)
    return render_template("index.html", **context)

  delete_temp = "SET exp = " + exp
  delete_cmd = text("UPDATE Player %s WHERE uid = %s" % (delete_temp, str(uid)))
  g.conn.execute(delete_cmd)
  
  message = ["Modify Successful!"]
  context = dict(data=message)
  return render_template("index.html", **context)


@app.route('/search')
def search_all():
  return render_template("search.html")

@app.route('/search_item', methods=['GET', 'POST'])
def item():
  tool_type = request.args['tool_type']
  if tool_type == "":
    item_q = "SELECT * FROM Tool"
  else:
    tool_type = "'"+tool_type+"'"
    item_q = text("SELECT * FROM Tool WHERE tool_type = %s" % tool_type)
  cursor = g.conn.execute(item_q)
  table = []
  header = ['Tool ID', 'Tool Type']
  table.append(header)
  for row in cursor:
    table.append(row)
  cursor.close()
  context = dict(data=table)
  return render_template("search.html", **context)

@app.route('/search_creature', methods=['GET', 'POST'])
def creature():
  type = request.args["type"]
  if type == "":
    if request.args["attr"] == "monster":
      query = "SELECT * from Creature WHERE animal_type is NULL"
    elif request.args["attr"] == "animal":
      query = "SELECT * from Creature WHERE monster_type is NULL"
    else:
      query = "SELECT * from Creature"
  else:
    type = "'"+type+"'"
    if request.args["attr"] == "monster":
      query = text("SELECT * from Creature WHERE monster_type=%s"%type)
    elif request.args["attr"] == "animal":
      query = text("SELECT * from Creature WHERE animal_type=%s"%type)
    else:
      query = text("SELECT * from Creature WHERE animal_type=%s or monster_type=%s"%(type,type))
  cursor = g.conn.execute(query)
  table = []
  header = ['Creature ID', 'Animal Type', 'Monster Type', 'Name']
  table.append(header)
  for row in cursor:
    table.append(row)
  cursor.close()
  context = dict(data=table)
  return render_template("search.html", **context)

@app.route('/search_achievement', methods=['GET', 'POST'])
def achievement():
  achievement_title = request.args["achievement_title"]
  if achievement_title == "":
    query = "SELECT * from Achievement"
  else:
    achievement_title = "'"+achievement_title+"'"
    query = text("SELECT * from Achievement WHERE achievement_title=%s"%achievement_title)
  cursor = g.conn.execute(query)
  table = []
  header = ['Achievement Title', 'Description']
  table.append(header)
  for row in cursor:
    table.append(row)
  cursor.close()
  context = dict(data=table)
  return render_template("search.html", **context)

@app.route('/search_world', methods=['GET', 'POST'])
def world():
  world_id = request.args["world_id"]
  if world_id == "":
    query = "SELECT * from World"
  else:
    query = text("SELECT * from World WHERE world_id=%s" % world_id)
  cursor = g.conn.execute(query)
  table = []
  header = ['World ID', 'World Upper x Coord', 'World Upper y Coord']
  table.append(header)
  for row in cursor:
    table.append(row)
  cursor.close()
  context = dict(data=table)
  return render_template("search.html", **context)

@app.route('/search_terrain', methods=['GET', 'POST'])
def terrain():
  terrain_type = request.args["terrain_type"]
  if terrain_type == "":
    query = "SELECT * from terrain"
  else:
    terrain_type = "'" + terrain_type + "'"
    query = text("SELECT * from terrain WHERE terrain_type=%s" % terrain_type)
  cursor = g.conn.execute(query)
  table = []
  header = ['Terrain ID', 'Terrain Type', 'Initial Altitude']
  talbe.append(header)
  for row in cursor:
    table.append(row)
  cursor.close()
  context = dict(data=table)
  return render_template("search.html", **context)

@app.route('/search_by_player')
def search_by_p():
  return render_template("search_by_player.html")	

@app.route('/search_by_player_implement', methods=['GET', 'POST'])
def search_by_player_implement():
  print(request.args)
  player_name = request.args["player_name"]

  if player_name == '':
    message = ["Please do not leave any field blank"]
    context = dict(data = message)
    return render_template("search_by_player.html", **context)

  player_name_tmp = "'" + player_name + "'"
  get_uid = text("SELECT uid FROM Player WHERE username = %s" % player_name_tmp)
  cursor = g.conn.execute(get_uid)
  uid = ''
  for row in cursor:
    uid = row[0]
  cursor.close()
  if uid == None or uid == '':
    message = ["Player does not exist"]
    context = dict(data = message)
    return render_template("search_by_player.html", **context)

  get_world_id = text("SELECT world_id FROM Player_in_World WHERE uid = %s" % uid)
  cursor = g.conn.execute(get_world_id)
  for row in cursor:
    world_id = row[0]
  cursor.close()

  header = []
  if player_name != '':
    if request.args["attr"] == "msg":
      query = text("SELECT content, time FROM send_message WHERE uid = %s" % uid)
      header = ['Content', 'Time']
    elif request.args["attr"] == "item":
      query = text("SELECT tool_id, since FROM player_owns_tool WHERE uid = %s" % uid)
      header = ['Tool_ID', 'Since When']
    elif request.args["attr"] == "achive":
      query = text("SELECT achievement_title, time FROM player_achieves WHERE uid = %s" % uid)
      header = ['achievement_title', 'Since When']
    elif request.args["attr"] == "others":
      query = text("SELECT uid, x_coordinate, y_coordinate FROM Player_In_World WHERE world_id = %s" % world_id)
      header = ['Player UID', 'x_coord', 'y_coord']

  cursor = g.conn.execute(query)
  table = []
  table.append(header)
  for row in cursor:
    table.append(row) 
  cursor.close()
  context = dict(data = table)

  return render_template("search_by_player.html", **context)



"""
@app.route('/alter_terrain', methods=['GET', 'POST'])
def alter():
  return render_template("alter_terrain.html")
"""

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