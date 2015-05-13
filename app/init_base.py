from sqlalchemy import *
import hashlib

SALT = 'foo#BAR_{baz}^666'

def hashFor(password):
    salted = '%s @ %s' % (SALT, password)
    return hashlib.sha256(salted).hexdigest() 

engine = create_engine('sqlite:///concert.db', echo=True)
metadata = MetaData(engine)

users = Table('users', metadata,
	Column('id', Integer, primary_key=True),
	Column('login', String, nullable=False),
	Column('password_hash', String, nullable=False),
	Column('nom', String),
	Column('prenom', String),
	Column('mail', String),
	Column('telephone', String),
	Column('date_naissance', Date),
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

db = engine.connect();

db.execute(users.insert().values(login='admin', password_hash=hashFor('admin')))
db.execute(salles.insert().values(numero='S1', nb_places=50))
db.execute(salles.insert().values(numero='S2', nb_places=10))
db.execute(salles.insert().values(numero='S3', nb_places=20))

db.close()
