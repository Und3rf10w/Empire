import sqlite3
from pushover import Client as pushover_client

def get_notifications(fields):
	"""
	Helper to pull common db config info outside of the normal menu execution.

	Fields should be comma separated.
		i.e. 'version,install_path'
	"""

	conn = sqlite3.connect('./data/empire.db', check_same_thread=False)
	conn.isolation_level = None

	cur = conn.cursor()
	cur.execute("SELECT %s FROM notifications" %(fields))
	results = cur.fetchone()
	cur.close()
	conn.close()

	return results

def create_notification_tables():
	"""
	Schema for notifications table:
	################################################
	# id | notetype | credentials | notes #
	################################################

	Notificaiton type is tied to notifysystems table
	"""
	conn = sqlite3.connect('./data/empire.db', check_same_thread=False)
	conn.isolation_level = None

	cur = conn.cursor()
	cur.execute("CREATE TABLE if not exists main.notifications(ID INTEGER PRIMARY KEY AUTOINCREMENT, NOTETYPE INT NOT NULL, CREDS TEXT NOT NULL, NOTES CHAR(256))")
	"""
	Schema for notifysystems:
	###############
	# id | system #
	###############
	"""
	cur.execute("CREATE TABLE if not exists main.notifysystems(ID INTEGER PRIMARY KEY AUTOINCREMENT, SYSTEM CHAR(256) NOT NULL)")
	cur.execute("INSERT INTO notifysystems(system) VALUES (\"pushover\")")
	cur.close()
	conn.commit()
	conn.close()

def add_notification(notetype, creds, *args):
	notes = args[0]

	conn = sqlite3.connect('./data/empire.db', check_same_thread=False)
	conn.isolation_level = None
	cur = conn.cursor()

	if notes != None:
		insert_string = "INSERT INTO notifications(NOTETYPE,CREDS,NOTES) VALUES (\"%s\", \"%s\", \"%s\")" % (str(notetype), str(creds), str(notes))
		cur.execute(insert_string)
	else:
		insert_string = "INSERT INTO notifications(NOTETYPE,CREDS) VALUES (\"%s\", \"%s\")" % (str(notetype), str(creds))
		cur.execute(insert_string)

	cur.close()
	conn.commit()
	conn.close()

def new_pushover_user():
	user_key = raw_input("Enter the pushover user key: ")
	app_key = raw_input("Enter the application key: ")
	creds = user_key + "," + app_key
	notes = raw_input("Enter notes for this entry: ")
	print("Credentials: %s, Notes: %s") % (creds,notes)

	if notes == ("" or None):
		add_notification("pushover",creds)
	else:
		add_notification("pushover",creds,notes)

def send_pushover(message, *args):
	title = args[0]
	conn = sqlite3.connect('./data/empire.db', check_same_thread=False)
	conn.isolation_level = None
	cur = conn.cursor()
	cur.execute("SELECT * FROM notifications WHERE notetype=\"pushover\"")
	results = cur.fetchall()
	for result in results:
		creds = result[2]
		user_key = creds.split(',')[0]
		app_key = creds.split(',')[1]
		pclient = pushover_client(str(user_key), api_token=str(app_key))
		pclient.send_message(str(message), title=str(title))

	cur.close()
	conn.close()

def pushover_setup():
 	create_notification_tables()
	new_pushover_user()
	send_pushover("Pushover setup complete", "Empire Test Message")
