# /source/server.py
# the web server that serves the short links.

from werkzeug.exceptions import HTTPException
from flask import Flask, request, render_template, redirect, url_for, abort, g
from cuid2 import Cuid

import sqlite3

# create a flask application. a flask application listens for http reqeusts at a certain
# port on `localhost`, and responds to them.
app = Flask(__name__)

# instantiate the id generator. if the user doesn't provide a name for the short url, we
# generate a short, user friendly one instead. note that the smaller the id, the more the
# chances of collisions. with a length of 7, we can generate approximately 237900 ids -
# `sqrt(36^{n-1} * 26)` - before a 50% chance of collision. see the following article for
# more information on this formula - https://en.wikipedia.org/wiki/Birthday_problem#Square_approximation
ids = Cuid(length=7)

# this function returns a database connection whenever required.
def get_db():
  # check if we have already created a database connection. 
  db = getattr(g, '_database', None)

  # if we haven't, then create a new in-memory database, and connect to it. the in-memory
  # database means that it'll reset whenever you restart the server. you might want to
  # replace this with a file name, or a proper remote database. 
  if db is None:
    db = g._database = sqlite3.connect('source/database/urls.db')
    db.row_factory = sqlite3.Row

  # initialise the database by creating the `urls` table if it doesn't already exist.
  db.cursor().execute("""
    create table if not exists urls (
      id varchar(255) not null primary key,
      name varchar(255) not null,
      long_url varchar(255) not null,
      short_url varchar(255) not null
    );
  """)
  db.commit()

  # return the database connection.  
  return db

# this function closes the database connection when the server is shutdown.
@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

# if a `post` request is made to this endpoint, then it stores the shortened url in the
# database, and returns a redirect to the `/urls/` list page.
@app.route("/urls", methods=["post"])
def create_url():
  # the form passed in the request contains the name of the record, as well as the URL
  # to shorten. we generate the ID and the shortened URL ourselves.
  content = request.form
  id = ids.generate()  

  # get a database handle, called a `cursor`. use the cursor to run a query to insert the
  # new record into the `urls` table, then close the handle.
  db = get_db()
  db.cursor().execute(
    "insert into urls values (?, ?, ?, ?);",
    (id, content["name"], content["long_url"], f"{request.url_root}urls/{id}")
  )
  db.commit()

  # redirect the user to the list page.
  return redirect(url_for("list_urls"))

# making a `get` request to this endpoint returns an html page displaying a list of
# shortened urls retrieved from the sql database.
@app.route("/urls/")
def list_urls():
  # get a database handle, called a `cursor`. use the cursor to run a query to fetch
  # all the records in the `urls` table, then close the handle.
  cursor = get_db().cursor()
  rows = cursor.execute('select * from urls').fetchall()
  cursor.close()

  # convert the `sqlite3.Row` objects into normal python dictionaries.
  url_list = [dict(row) for row in rows]

  # render the html page using the fetched data, which looks something like this:
  #  url_list = [{
  #   "id": "kvkgn8m",
  #   "name": "My GitHub",
  #   "long_url": "https://github.com/octocat",
  #   "short_url": "https://localhost:5000/urls/kvkgn8m",
  #  }]
  return render_template("list.html", url_list=url_list)

# this function handles any requests to the `/urls/<id>` endpoint. this endpoint queries
# the database for the shortened url, and redirects the user to the long url.
@app.route("/urls/<id>")
def handle_url(id):
  if request.args.get('Delete') == 'Delete':
    return delete_url(id)
  
  # get a database handle, called a `cursor`. use the cursor to run a query to fetch
  # the record with an id that matches the id passed in the request, then close the handle.
  cursor = get_db().cursor()
  rows = cursor.execute('select * from urls where id = ?', (id,)).fetchall()
  cursor.close()

  # if there is no such record in our database, return a 404 not found error.
  if len(rows) == 0:
    abort(404)
  else:
    # otherwise, redirect them to the original url.
    url_data = dict(rows[0])

    return redirect(url_data['long_url']), 302

# if a `delete` request is made to this endpoint, then it deletes the record for that url
# from the database, and returns a redirect to the `/urls/` list page.
@app.route("/urls/<id>", methods=["delete"])
def delete_url(id):
  # get a database handle, called a `cursor`. use the cursor to run a query to delete the
  # record from the `urls` table, then close the handle.
  db = get_db()
  db.cursor().execute(
    "delete from urls where id = ?;",
    (id,)
  )
  db.commit()

  # redirect the user to the list page.
  return redirect(url_for("list_urls"))

# if a `get` request is made to this endpoint, then it returns the html page for creating
# a new shortened url.
@app.route("/create")
def create_url_view():
  return render_template("create.html")

# shows the error page whenever something goes wrong.
@app.errorhandler(HTTPException)
def handle_exception(error):
  app.logger.error(error)
  return render_template("error.html", code=error.code)
