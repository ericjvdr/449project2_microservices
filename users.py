import flask
import hashlib
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, make_response, json, jsonify, g

app = flask.Flask(__name__)
app.config.from_envvar("APP_CONFIG")
DATABASE = "twitter-clone.db"

#-----------------------------------------------------#
#------------------[ STATUS CODES ]-------------------#

# status - ok
def status_200(data):
	response = jsonify(data)
	response.status_code = 200
	response.mimetype = "application/json"
	return response

# status - resource created successfully
def status_201(data):
  response = jsonify(data)
  response.status_code = 201
  response.mimetype = "application/json"
  return response

# status - bad request
def status_400():
  err_message = {
    'status: ': 400,
    'message: ': 'Bad Request: ' + request.url
  }
  response = jsonify(err_message)
  response.status_code = 400
  response.mimetype = "application/json"
  return response

# status - password hashes don't match
def status_401():
  err_message = {
    'status: ': 401,
    'message: ': 'Unauthorized: ' + request.url
  }
  response = jsonify(err_message)
  response.status_code = 401
  response.mimetype = "application/jason"
  return response

# status - resource not found
def status_404():
  err_message = {
    'status: ': 404,
    'message: ': 'Not Found: ' + request.url
  }
  response = jsonify(err_message)
  response.status_code = 404
  response.mimetype = "application/json"
  return response

# status - record already exists
def status_409():
	err_message = { 
	'status: ': 409,
	'message: ': 'Conflict: ' + request.url,
	}
	response = jsonify(err_message)
	response.status_code = 409
	response.mimetype = "application/json"
	return response

#-----------------------------------------------------#
#------------------[ HELPER FUNCTS ]------------------#

# cli - creates the database based on provided schema 
@app.cli.command('init')
def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

# funct: executed for every result returned from the database to convert the result
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# funct: get the current open database connection
def get_db():
  db = getattr(g, '_database', None)
  if db is None:
      db = g._database = sqlite3.connect(app.config['DATABASE'])
      db.row_factory = make_dicts
  return db

# funct: combines getting the cursor, executing and fetching the results
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# whenever the context is destroyed the database connection will be terminated.
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#----------------------------------------------#
#------------------[ ROUTES ]------------------#

@app.route('/api', methods=['GET'])
def home():
  # return resource directory
  response = {
    "message": "OK " + request.url,
    "resources": {
        "accounts": {
            "url": request.url + "/accounts"
        },
        "followers": {
            "url": request.url + "/followers"
        },
        "tweets": {
            "url": request.url + "/tweets"
        }
    },
    "status": 200
  }
  return status_200(response)

@app.route('/api/accounts', methods=['GET'])
def getAccounts():

  query = "SELECT * FROM accounts"
  results = []

  for tweet in query_db(query):
    data = {
      'username': tweet['username'],
      'email': tweet['email'],
      'password': tweet['passwrd']
    }
    results.append(data)

  jsonify(results)

  return status_200(results)

@app.route('/api/followers', methods=['GET'])
def getFollowers():

  query = "SELECT * FROM followers"
  results = []

  for tweet in query_db(query):
    data = {
      'user_account': tweet['user_account'],
      'follower_account': tweet['follower_account'],

    }
    results.append(data)

  jsonify(results)

  return status_200(results)

@app.route('/api/accounts', methods=['POST'])
def createUser():

  # get bulk data from request
  req_data = request.get_json()

  # get parameter data
  username = req_data.get('username')
  email = req_data.get('email')
  password = req_data.get('password')

  # check to see if user data already exists
  query= "SELECT username FROM accounts WHERE (username =? OR email=?);"
  check = query_db(query, (username,email,))

  # if user DOES NOT exist, continue
  if check == []:
    # generate a password hash
    passwordHash = generate_password_hash(password, "sha256")

    # create data payload
    inputs = []
    # put the data in there
    inputs.append(username)
    inputs.append(email)
    inputs.append(passwordHash)

    # create query string
    query = "INSERT INTO accounts(id, username, email, passwrd) VALUES (null, ?, ?, ?);"
    # connect to DB
    conn = sqlite3.connect(DATABASE)
    # execute the query with the data
    conn.execute(query, inputs)
    # complete the transaction
    conn.commit()
    conn.close()

    # create response msg
    response = {
      "location": request.url,
      "message": "Created: " + request.url,
      "status": 201,
    }
    # resource created successfully
    return status_201(response)
  # if the user DOES exists, then return conflict
  else: return status_409()

@app.route('/api/accounts', methods=['PUT'])
def authenticateUser():

  # get bulk data from request
  req_data = request.get_json()

  # get parameter data
  username = req_data.get('username')
  password = req_data.get('password')

  # check to see if user already exists
  query= "SELECT username, passwrd FROM accounts WHERE username =?;"
  check = query_db(query, (username,))

  # if the user DOES exist, continue
  if check != []:
    # get the hashed password for the specified account from DB
    user = query_db('SELECT passwrd FROM accounts WHERE username =?;', [username], one=True)
    userPasswordHash = user['passwrd']

    # check if hashes match
    if check_password_hash(userPasswordHash, password):
      # create response msg
      response = {
        "status": 200,
        "message": "OK: " + request.url,
        "details": "authentication successful"
      }
      # password hashes DO match
      return status_200(response)
    # password hashes DON'T match
    else: return status_401()
  # if the user DOES NOT exist
  else: return status_404()

@app.route('/api/followers', methods=['POST'])
def addFollower():

  # get bulk data from request
  req_data = request.get_json()

  # get parameter data
  username = req_data.get('username')
  usernameToFollow = req_data.get('usernameToFollow')
  
  # query db to make sure both users exist
  query = "SELECT username FROM accounts WHERE username =?;"
  checkUsername = query_db(query, (username,))
  checkUsernameToFollow = query_db(query, (usernameToFollow,))

  # query db to make sure the record doesn't already exist
  query2 = "SELECT id FROM followers WHERE (user_account=? AND follower_account =?);"
  checkRecordExists = query_db(query2, (usernameToFollow, username,))

  # check that both users exist
  if checkUsername != [] and checkUsernameToFollow != []:
    # check that record doesn't already exist
    if checkRecordExists == []:
      # make sure that users aren't indentical
      if username != usernameToFollow:
        # create data payload
        inputs = []
        # put the data in there
        inputs.append(usernameToFollow)
        inputs.append(username)

        # create query string
        query = "INSERT INTO followers(id, user_account, follower_account) VALUES (null, ?, ?);"
        # connect to DB
        conn = sqlite3.connect(DATABASE)
        # execute the query with the data
        conn.execute(query, inputs)
        # complete the transaction
        conn.commit()
        conn.close()

        response = {
          "location": request.url,
          "status": 201,
          "message": "Created: " + request.url
        }

        # conditions were met, successful post
        return status_201(response)
      # usernames ARE equal, bad request
      else: return status_400()
    # record already exists
    else: return status_409()
  # if at least one user DOES NOT exist
  else: return status_400()

@app.route('/api/accounts/<usernameToRemove>/followers/<username>', methods=['DELETE'])
def deleteFollower(username, usernameToRemove):

  # make sure the record exists
  query = "SELECT id FROM followers WHERE (user_account=? AND follower_account=?);"
  check = query_db(query, [usernameToRemove, username], one=True)

  # if it exists, continue
  if check != []:

    # get the id of the record
    id = check['id']

    # create data payload
    inputs = []
    # put the data in there
    inputs.append(id)

    # create query string
    query = "DELETE FROM followers WHERE id=?;"
    # connect to DB
    conn = sqlite3.connect(DATABASE)
    # execute the query with the data
    conn.execute(query, inputs)
    # complete the transaction
    conn.commit()
    conn.close()

    response = {
      "message": "OK: " + request.url,
      "status": 200,
    }
    # record successfully deleted
    return status_200(response)
  # record was not found, or already deleted  
  else: return status_404()  

# handles any routes other than the ones specified above
@app.errorhandler(404)	
def route_not_found(error = None):
	message = { 
	'status: ': 404,
	'message: ': 'Route Not Found: ' + request.url
	}
	response = jsonify(message)
	response.status_code = 404
	response.mimetype = "application/json"
	return response  

#app.run()

