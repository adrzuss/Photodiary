from flask import current_app, g, flash, redirect, url_for, session
import mariadb
import sys
import configparser
import decimal

def get_db():
  if 'db' not in g:
    try:
      g.db = mariadb.connect(
        host = 'localhost',
        port = 3306,
        user = 'root',
        password = 'frgigi202009',
        database = 'photodiary'
      )
      g.cur = g.db.cursor()
    except mariadb.Error as e:
      flash(f"Error de conección a la base de datos:{e}", "error")
      print(f"error: {e}")
      return redirect(url_for("index"))  
  return g.db, g.cur

def close_db(e=None):
  db = g.pop('db', None)
  if db is not None:
    db.close()


def init_app(app):
  app.teardown_appcontext(close_db)    

def my_dict(row, cur):
  d = {}
  for i, col in enumerate(cur.description):
    if isinstance(row[i], decimal.Decimal):
      d[col[0]] = float(row[i])
    elif (isinstance(row[i], str)):
      d[col[0]] = row[i]     
    else:
      d[col[0]] = row[i]
  return d  


#Registro de base de datos
configdb = configparser.ConfigParser()
configdb.read('config.ini')
host = configdb['base']['host']
#user = configdb['base']['username']
#password = configdb['base']['password']
server = configdb['base']['server']
databasefile = configdb['base']['databasefile']
port = configdb['base']['port']
user = 'db_user'
password = 'frgigi202009'

