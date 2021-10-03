Project 2: Microservices
CPSC 449-02 FALL 2020
========================
Contributors:

Jason Otter
Eric Van Der Roest
Jordan Wermuth


Project Description:
-Two back-end microservices for a microblogging service similar to Twitter.
-Services included are the Users microservice and the Timelines microservice.
-Both services and all APIs are explained in "Project 2 Documentation".


Must Include These Project Files:
-users.py
-timelines.py
-schema.sql
-Procfile
-app.cfg
-.env


Tools Used:
-sqlite3
-flask
-foreman


To Run:
1. Open a terminal and navigate to the project directory
2. Use the following commands to get started:

$ source env/bin/activate	# Starts virtual environment
$ flask init			# Creates database
$ foreman start 		# Starts services
