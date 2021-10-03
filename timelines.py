import flask
import hashlib
import sqlite3
from users import status_200, status_201, status_400, status_404
from flask import Flask, request, make_response, jsonify, g

app = flask.Flask(__name__)
app.config.from_envvar("APP_CONFIG")
DATABASE = "twitter-clone.db"

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

#-----------------------------------------------------#
#------------------[ ROUTES ]-------------------------#

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

# post a new tweet
@app.route('/api/tweets', methods=['POST'])
def postTweet():

  # get bulk data from request
  req_data = request.get_json()

  # get parameter data
  username = req_data.get('username')
  text = req_data.get('text')

  # create data payload
  inputs = []
  # put the data in there
  inputs.append(username)
  inputs.append(text)

  # create query string
  query = "INSERT INTO tweets(id, author, content, timestmp) VALUES (null, ?, ?, CURRENT_TIMESTAMP);"
  # connect to DB
  conn = sqlite3.connect(DATABASE)
  # execute the query with the data
  conn.execute(query, inputs)
  # complete the transaction
  conn.commit()
  conn.close()

  response = {
    "status": 201,
    "message": "Created: " + request.url
  }

  return status_201(response)

# get ALL recent tweets
@app.route('/api/tweets', methods=['GET'])
def getPublicTimeline():

  query = "SELECT * FROM tweets ORDER BY timestmp DESC LIMIT 25;"
  results = []

  for tweet in query_db(query):
    data = {
      'author': tweet['author'],
      'content': tweet['content'],
      'timestamp': tweet['timestmp']
    }
    results.append(data)

  jsonify(results)

  return status_200(results)

# get recent tweets by user
@app.route('/api/tweets/<author>', methods=['GET'])
def getUserTimeline(author):

  # make sure the author exists
  query= "SELECT author FROM tweets WHERE author =?;"
  check = query_db(query, [author])

  # if the user DOES exist
  if check != []:

    query = "SELECT * FROM tweets WHERE author =? ORDER BY timestmp DESC limit 25;"
    results = []
  
    for tweet in query_db(query, [author]):
      data = {
        'author': tweet['author'],
        'content': tweet['content'],
        'timestamp': tweet['timestmp']
      }
      results.append(data)

    jsonify(results)

    return status_200(results)
  # if the author DOESN'T exist
  else: return status_404()

# get recent tweets from all accounts a user followers
@app.route('/api/followers/<username>/tweets', methods=['GET'])
def getHomeTimeline(username):

  # make sure the user is following at least one account
  query= "SELECT follower_account FROM followers WHERE follower_account =?;"
  check = query_db(query, [username])

  # if the user DOES exist
  if check != []:

    query = "SELECT tweets.id, followers.user_account, tweets.content, tweets.timestmp FROM tweets INNER JOIN followers ON (tweets.author = followers.user_account AND followers.follower_account =?) ORDER by tweets.timestmp DESC LIMIT 25;"
    results = []

    for tweet in query_db(query, [username]):
      data = {
        'author': tweet['user_account'],
        'content': tweet['content'],
        'timestamp': tweet['timestmp']
      }
      results.append(data)

    jsonify(results)

    return status_200(results)
  # account does NOT exist
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



  # log the if-modified-since header
  # sys.stdout.write('If-Modified-Since Header: ' + str(type(request.headers['If-Modified-Since'])) + '\n')
  # sys.stdout.flush()

  # convert the header time back to a datetime object
  # convertedIfModifiedSince = datetime.strptime(str(request.headers['If-Modified-Since']), '%Y-%m-%d %H:%M:%S.%f')

  # sys.stdout.write('testing strptime(), type should equal datetime: ' + str(type(convertedIfModifiedSince)) + '\n')
  # sys.stdout.flush()

  # sys.stdout.write('supplied If-Modified-By: ' + str(convertedIfModifiedSince) + '\n')
  # sys.stdout.flush()

  # get the current val of lastModified
  # sys.stdout.write('Current lastModified: ' + str(lastModified) + '\n')
  # sys.stdout.flush()
  # add 5 minutes

  # determine response
  # wasModified = False

  # if convertedIfModifiedSince < lastModified:
  #   sys.stdout.write('return a 304 - not modified')
  #   sys.stdout.flush()
  # else:
  #   sys.stdout.write('return a 200 - it was modified')
  #   sys.stdout.flush()

  # wasModified = True


  # isolate the seconds column that we need
  # sys.stdout.write('Current Second: ' + )
  # sys.stdout.flush()