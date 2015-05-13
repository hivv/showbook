# ............................................................................................... #

from flask  import *
from sqlalchemy import *
from markdown import markdown
import os, hashlib
from sqlalchemy.ext.automap import automap_base

# ............................................................................................... #

app = Flask(__name__)
app.secret_key = os.urandom(256)        

SALT = 'foo#BAR_{baz}^666'              

engine = create_engine('sqlite:///concert.db', echo=False)
metadata = MetaData(engine)

users = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('login', String, nullable=False),
	Column('nom', String),
	Column('prenom', String),
	Column('mail', String),
	Column('password_hash', String, nullable=False),
	Column('date_naissance', Integer),
	Column('telephone', String),	
	sqlite_autoincrement=True)    

events = Table('events', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String, nullable=False),
	Column('description', String),
	Column('date', DateTime),
	Column('salle', Integer, ForeignKey('salles.id')),
	sqlite_autoincrement=True)

salles = Table('salles', metadata,
	Column('id', Integer, primary_key=True),
	Column('numero', String, nullable=False),
	Column('nb_places', Integer, nullable=False),
	sqlite_autoincrement=True)
	
reservations = Table('reservations', metadata,
	Column('id_Event', Integer, ForeignKey('events.id')),
	Column('id_User', Integer, ForeignKey('users.id')),
	Column('places_reserves', Integer, nullable=False))

metadata.create_all(engine)

def hashFor(password):
    salted = '%s @ %s' % (SALT, password)
    return hashlib.sha256(salted).hexdigest()   

db = engine.connect();
db.execute(users.insert().values(login='admin', password_hash=hashFor('admin')))
db.execute(salles.insert().values(numero='S1', nb_places=50))
db.execute(salles.insert().values(numero='S2', nb_places=10))
db.execute(salles.insert().values(numero='S3', nb_places=20))
db.close()

# ............................................................................................... #

#def page_content(name):
	#db = engine.connect()
	#try:
		#row = db.execute(select([pages.c.text]).where(pages.c.name == name)).fetchone()
		#if row is None:
			#return '**(This page is empty or does not exist.)**'
		#return row[0]
	#finally:
		#db.close()

#def delete_page(name):
	#db = engine.connect()
	#try:
		#if db.execute(select([pages.c.name]).where(pages.c.name == name)).fetchone() != None:
			#db.execute(pages.delete().where(pages.c.name == name))
	#finally:
		#db.close()



def authenticate(login, password):
	db = engine.connect()
	print login, password
	
	try:
		if db.execute(select([users.c.login]).where(users.c.login == login)).fetchone() != None:
			sel = select([users]).where(and_(users.c.login == login, users.c.password_hash == hashFor(password)))
			if db.execute(sel).fetchone() != None:
				return (True, "Login Success")
			else:
				return (False, "Mot de passe eronne")
		else:
			return (False, "Utilisateur non existant")
	finally:
		db.close()

def signUp(login, nom, prenom, mail, password, date_naissance,telephone):
	db = engine.connect()
	try:
		if db.execute(select([users.c.login]).where(users.c.login == login)).fetchone() is None:
			print "Hello"
			db.execute(users.insert().values(login=login, nom=nom, prenom=prenom, mail=mail, password_hash=hashFor(password),date_naissance=date_naissance,telephone=telephone))
			return True
		else:
			return False
	finally:
		db.close()

#def updateUser(login, password, nom, prenom, mail, telephone, date_naissance):
	#db = engine.connect()
	#try:
		#if db.execute(select([users.c.login]).where(users.c.login == login)).fetchone() != None:
			#db.execute(users.update().values(nom=nom, prenom=prenom, mail=mail, telephone=telephone, 
			#date_naissance==date_naissance).where(users.c.login == login))
	#finally:
		#db.close()

# ............................................................................................... #

@app.route('/')
def index():
	return redirect('static/index.html')
#@app.route('/<name>')
#def index(name='Main'):
	#return redirect('/pages/' + name)

@app.route('/pages/<name>')
def page(name):
	raw = page_content(name)
	content = markdown(raw)
	return render_template('page.html', name=name, text=content, raw=raw)

@app.route('/save', methods=['POST'])
def save():
	page = request.form['page']
	text = request.form['text']
	if text:
		update_page(page, text)	
	else:
		delete_page(page)
	return redirect('/pages/' + page)

#@app.route('/login', methods=['GET', 'POST'])
#def login():
	#from_page = request.args.get('from', 'Main')
	#if request.method == 'POST':
		#if authenticate_or_create(request.form['login'], request.form['password']):
			#session['username'] = request.form['login']
			#return redirect('/pages/' + from_page)
		#else:
			#flash('Invalid password for login: ' + request.form['login'])
			#return redirect('/login?from=' + from_page)
	#else:
		#return render_template('login.html', from_page=from_page)

@app.route('/login', methods=['POST'])
def login():
	
	if request.method == 'POST':
		content = request.get_json(force=True)
		print content
		print content['Pseudo']
		res = authenticate(content['Pseudo'], content['Password'])
		print "ololo"
		print res
		return json.dumps({'success':res[0]})
	else : 
		return json.dumps({'success':False}), 200, {'ContentType':'application/json'} 

@app.route('/signUp', methods=['POST'])
def signup():
	
	if request.method == 'POST':
		content = request.get_json(force=True)
		print content
		print content['Pseudo']
		print content['Email']
		res = signUp(content['Pseudo'], content['FirstName'], content['Surname'] ,content['Email'], content['Password'], content['YearOfBirth'], content['PhoneNumber'])
		print "ololo2222"
		print res
		return json.dumps({'success':res})
	else : 
		return json.dumps({'success':False}), 200, {'ContentType':'application/json'} 


@app.route('/logout')
def logout():
    from_page = request.args.get('from', 'Main')
    session.clear()
    return redirect('/pages/' + from_page)

# ............................................................................................... #

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)
	

# ............................................................................................... #


