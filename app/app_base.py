# ............................................................................................... #

from flask  import *
from sqlalchemy import *
from markdown import markdown
import os, hashlib
import datetime
from time import strftime
from sqlalchemy.ext.automap import automap_base
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


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
	Column('date', Date),
	Column('img',String, nullable=False),
	Column('salle', Integer, ForeignKey('salles.id')),
	sqlite_autoincrement=True)

salles = Table('salles', metadata,
	Column('id', Integer, primary_key=True),
	Column('name', String, nullable=False),
	Column('link',String,nullable=False),
	Column('plan',String, nullable=False),
	Column('c1',String, nullable=False),
	Column('c2',String, nullable=True),
	Column('c3',String, nullable=True),
	Column('n1',Integer, nullable=False),
	Column('n2',Integer, nullable=True),
	Column('n3',Integer, nullable=True),
	Column('nb_places', Integer, nullable=False),
	sqlite_autoincrement=True)
	
reservations = Table('reservations', metadata,
	Column('id_Event', Integer, ForeignKey('events.id')),
	Column('id_User', Integer, ForeignKey('users.id')),
	Column('id_Cat', String, nullable=False), 
	Column('Social', Integer, nullable=False),
	Column('places_reserves', Integer, nullable=False))

metadata.create_all(engine)

def hashFor(password):
    salted = '%s @ %s' % (SALT, password)
    return hashlib.sha256(salted).hexdigest()   

db = engine.connect();
db.execute(users.insert().values(login='admin', password_hash=hashFor('admin')))
db.execute(users.insert().values(login='aaa', password_hash=hashFor('aaa')))
db.execute(salles.insert().values(name='Theatre Royal Wakefield', link='http://www.theatreroyalwakefield.co.uk',plan='/static/img/plan1.gif', c1='Stalls', c2='Dress Circle', c3='Upper Circle', n1=200, n2=150, n3=100, nb_places=450))
db.execute(salles.insert().values(name='TBarnfield Theatre', link='http://www.barnfieldtheatre.org.uk/',plan='/static/img/plan2.jpg', c1='Unique Category', n1=300, nb_places=300))
#db.execute(salles.insert().values(numero='S3', nb_places=20))
db.execute(events.insert().values(name='Hearscape',description='Hearscape is cool but unknown', img='/static/img/hearscape.png',date=datetime.date(2015, 06, 21),salle=1))
db.execute(events.insert().values(name='Rolling Stones',description='The Rolling Stones are one of the biggest Rock Band ever',img='/static/img/stones.jpg',date = datetime.date(2015,07,23),salle=2))
db.execute(events.insert().values(name='Archive',description='Archive is an English trip-hop and progressive rock band very appreciated in France',img='/static/img/archive.jpg',date = datetime.date(2015,8,11),salle=2))


db.close()



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
			db.execute(users.insert().values(login=login, nom=nom, prenom=prenom, mail=mail, password_hash=hashFor(password),date_naissance=date_naissance,telephone=telephone))
			return True
		else:
			return False
	finally:
		db.close()

def retrieveProfile(username):
	db = engine.connect()
	try:
		if db.execute(select([users.c.login]).where(users.c.login == username)).fetchone() != None:
			sel = select([users.c.nom, users.c.prenom, users.c.mail, users.c.date_naissance, users.c.telephone,users.c.login]).where(and_(users.c.login == username))
			usr=db.execute(sel)
			for row in usr:
				return row
		else :
			return None
	finally :
		db.close()

def findShows(username):
	db = engine.connect()
	try :
		if db.execute(select([users.c.login]).where(users.c.login == username)).fetchone() != None:
			sel = select([events.c.name, events.c.date, salles.c.name, reservations.c.places_reserves, reservations.c.id_Cat]).where(and_(users.c.login == username, users.c.id == reservations.c.id_User, events.c.id == reservations.c.id_Event, events.c.salle == salles.c.id))
			show = db.execute(sel)
			liste = []
			for row in show :
				liste.append(row)
			return liste
		else :
			return None
	finally :
		db.close()

def newReservation(user, show, nbpl, soc, cat):
	db=engine.connect()
	print('1')
	try:
		db.execute(reservations.insert().values(id_Event=show,id_User=user,places_reserves=nbpl, Social=soc, id_Cat=cat))
		print('2')
		return True
	finally:
		db.close()


					

def generate_token(pseudo,expiration=600):
	s= Serializer(app.config['SECRET_KEY'],expires_in = expiration)
	tok = s.dumps({'Pseudo':pseudo})
	#print verify_auth_token(tok)
	return tok

def verify_auth_token(token):
	s=Serializer(app.config['SECRET_KEY'])
	try:
		userData = s.loads(token)
		user = userData['Pseudo']
		print user
		return user
	except SignatureExpired:
		print "erreur1"
		return None
	except BadSignature:
		print "erreur2"
		return None
	

	
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

@app.route('/book/<name>')
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
	

@app.route('/login', methods=['POST'])
def login():
	content = request.get_json(force=True)
	print content
	print content['Pseudo']
	res = authenticate(content['Pseudo'], content['Password'])
	if res[0]:	
		token = generate_token(content['Pseudo'])
		return json.dumps({'success':True, 'token' : token.decode('ascii')})
	else: 		
		return json.dumps({'success':False, 'result':res[1]})
 

@app.route('/signUp', methods=['POST'])
def signup():
	content = request.get_json(force=True)
	print content
	res = signUp(content['Pseudo'], content['FirstName'], content['Surname'] ,content['Email'], content['Password'], content['YearOfBirth'], content['PhoneNumber'])
	if res :
		tok=generate_token(content['Pseudo'])	
		return json.dumps({'success':True,'token' : tok.decode('ascii')})
	else :
		return json.dumps({'success':False})
	


@app.route('/users', methods=['POST'])
def user():
	content = request.get_json(force=True)
	tok = content['Token']
	user = verify_auth_token(tok)
	if user != None :
		return json.dumps({'username':user})
	else :
		return redirect('/')

@app.route('/profile',methods=['POST'])
def profile():
	content = request.get_json(force=True)
	tok = content['Token']
	user = verify_auth_token(tok)
	if user != None :
		res = retrieveProfile(user)
		print res
		return json.dumps({'name':res[0],'surname':res[1],'email':res[2],'date':res[3],'phone':res[4],'login':res[5]})
	else :
		return redirect('/')

@app.route('/shows', methods=['POST'])
def shows():
	content = request.get_json(force=True)
	tok = content['Token']
	user = verify_auth_token(tok)
	if user != None :
		res = findShows(user)
		print res
		resultat = []
		for row in res:
			resultat.append({'name':row[0], 'date':row[1].strftime("%d/%m/%y"), 'salle':row[2], 'places':row[3], 'categorie':row[4]})
		return json.dumps(resultat, separators=(',',':'))
	else :
		return redirect('/')
	
@app.route('/_get_events_infos/')
def infos():
	db=engine.connect()
	n = request.args.get('n', 0, type=int)
	print('requ$ete numero')
	print(n)
	#db.events.order_by(db.events.date.desc().all())
	s=select([events.c.name, events.c.date, events.c.img, events.c.id])
	result = db.execute(s)
	#result=result.order_by(desc(events.date)).limit(9).all()
	i=0
	
	for row in result :
		if i is n:
			ret_data={"name": row[0], "img": row[2],"date":row[1].strftime('%d/%m/%Y'), "id":row[3]}
			return jsonify(ret_data)
		else:
			i=i+1
	db.close()

@app.route('/_get_events_book/')
def book():
	db=engine.connect()
	idShow=request.args.get('n',0,type=int)
	try :
		s=select([events.c.name, events.c.date, events.c.img, events.c.description, events.c.salle]).where(events.c.id==idShow)
		result=db.execute(s)
		row_one=result.fetchone()
		salle=select([salles.c.name, salles.c.link, salles.c.plan, salles.c.c1,salles.c.c2, salles.c.c3]).where(salles.c.id==row_one[4])
		salle_res=db.execute(salle)
		row_two=salle_res.fetchone()
	finally :
		db.close()
	ret_data={"name":row_one[0], "date":row_one[1].strftime('%d/%m/%Y'), "img":row_one[2], "desc":row_one[3], "nomSalle":row_two[0], "link":row_two[1], "plan":row_two[2], "c1":row_two[3], "c2":row_two[4], "c3":row_two[5]}
	return jsonify(ret_data)

@app.route('/booking_engine', methods=['POST'])
def bookEngine():
	db=engine.connect()
	content = request.get_json(force=True)
	print content
	s=select([events.c.id]).where(events.c.name==content['Show'])
	show=db.execute(s).fetchone()
	u=select([users.c.id]).where(users.c.login==content['Pseudo'])
	user=db.execute(u).fetchone()
	us=user[0]
	sh=show[0]
	try:
		db.execute(reservations.insert().values(id_Event=sh,id_User=us,places_reserves=content['nbPlaces'], Social=content['social'], id_Cat=content['cat']))
		mess='The reservation has been processed and is now visible on your profile'
	except :
		mess='The reservation has failed. We apologize for the error.'
	finally:
		db.close()
	return json.dumps({'success':True, 'token' : "coucou", 'result':mess})
	#else: 		
	#	return json.dumps({'success':False, 'result':res[1]})

# ............................................................................................... #

if __name__ == '__main__':
	app.run(debug=True)
	#use_reloader=False

# ............................................................................................... #


