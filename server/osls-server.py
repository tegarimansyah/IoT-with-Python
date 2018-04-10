
# coding: utf-8

# In[1]:


from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# # Flask Config

# In[2]:


user = 'root'
password = 'root'
host = 'localhost'
port = 3306
dbname = 'osls'

db_uri = 'mysql+mysqldb://%s:%s@%s:%d/%s' % (user, password, host, port, dbname)


# In[3]:


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


# # Supporting Function

# In[4]:


import hashlib
def hashit(text):
    text = password.encode('UTF-8')
    hash_object = hashlib.sha256(text)
    hex_dig = hash_object.hexdigest()
    return hex_dig


# # Database

# In[5]:


class Users(db.Model):
    __table_args__ = {'extend_existing': True}  
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    appkey = db.Column(db.String(64), unique=True, nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username


# In[6]:


class Lamps(db.Model):
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    owner =  db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_name = db.Column(db.String(120), index=True, nullable=False)
    state = db.Column(db.Boolean, default=0, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Lamp %r>' % self.device_name


# In[7]:


db.create_all()


# In[8]:


def savedb(data):
    db.session.add(data)
    db.session.commit()


# # Fungsi Operasi

# In[9]:


def registrasi_akun(uname, email, password):
    try:
        import uuid
        password = hashit(password)
        appkey = str(uuid.uuid4())
        newuser = Users(username=uname, email=email, password=password, appkey=appkey)
        savedb(newuser)
        data= {
            'id' : newuser.id,
            'username' : newuser.username,
            'email' : newuser.email,
            'appkey' : newuser.appkey,
            'date_registered' : newuser.date_registered,
            'location' : newuser.location
        }
        return {'status': 'success', 'data': data}, 201
    
    except:
        db.session.rollback()
        return {'status': 'failed', 'data': 'Username atau email sudah digunakan'}, 400


# In[10]:


def registrasi_lampu(device_name, uname):
    try:
        state = False
        newlamp = Lamps(device_name = device_name, state = state, owner = Users.query.filter_by(username=uname).first().id, last_change=datetime.utcnow())
        savedb(newlamp)
        data= {
            'id' : newlamp.id,
            'device_name' : newlamp.device_name,
            'state' : newlamp.state,
            'owner' : newlamp.owner,
            'last_change' : newlamp.last_change
        }
        
        return {'status': 'success', 'data': data}, 201
    except:
        db.session.rollback()
        return {'status': 'failed', 'data': 'Lampu tidak dapat didaftarkan'}, 400


# In[11]:


def list_lampu(uname, lampuid = 0):
    try:
        if lampuid == 0:
            lamps = Lamps.query.filter_by(owner = (Users.query.filter_by(username=uname).first().id)).all()
            data = []
            for lamp in lamps:
                lamp_data = {}
                lamp_data['id'] = lamp.id
                lamp_data['device_name'] = lamp.device_name
                lamp_data['state'] = lamp.state
                lamp_data['last_change'] = lamp.last_change
                data.append(lamp_data)
            return {'status': 'success', 'data': data}, 201
        else:
            lamp = Lamps.query.filter_by(owner = (Users.query.filter_by(username=uname).first().id), id=lampuid).first()
            lamp_data = {}
            lamp_data['id'] = lamp.id
            lamp_data['device_name'] = lamp.device_name
            lamp_data['state'] = lamp.state
            lamp_data['last_change'] = lamp.last_change
            return {'status': 'success', 'data': lamp_data}, 201
    except:
            return {'status': 'failed', 'data': 'Not found'}, 404


# In[12]:


def update_lampu(uname, lampustate, lampuid = 0):
    if not isinstance(lampustate, bool):
        return {'status': 'failed', 'data': 'state error'}, 400
    
    try:

        if lampuid == 0:
            lamps = Lamps.query.filter_by(owner = (Users.query.filter_by(username=uname).first().id)).all()
            data = []
            for lamp in lamps:
                lamp.state = lampustate
                lamp_data = {}
                lamp_data['id'] = lamp.id
                lamp_data['device_name'] = lamp.device_name
                lamp_data['state'] = lamp.state
                lamp_data['last_change'] = lamp.last_change
                data.append(lamp_data)
            db.session.bulk_save_objects(lamps)
            db.session.commit()
            return {'status': 'success', 'data': data}, 201

        else:
            lamp = Lamps.query.filter_by(owner = (Users.query.filter_by(username=uname).first().id), id=lampuid).first()
            lamp.state = lampustate
            lamp_data = {}
            savedb(lamp)

            lamp_data['id'] = lamp.id
            lamp_data['device_name'] = lamp.device_name
            lamp_data['state'] = lamp.state
            lamp_data['last_change'] = lamp.last_change
            return {'status': 'success', 'data': lamp_data}, 201
    
    except:
        return {'status': 'failed', 'data': 'Not found'}, 404        


# # Test Fungsi
registrasi_akun('tegariman','tegar@imansyah.name','masukaja')registrasi_lampu('Kamar mandi', 'tegar')list_lampu('tegar')list_lampu('tegar',1)update_lampu('tegar', False)update_lampu('tegar', True, 1)
# # API

# In[13]:


@app.route('/reg/', methods=['POST'])
def create_accout():
@app.route('/reg/', methods=['POST'])
def create_accout():
    if request.json and 'uname' in request.json and 'email' in request.json and  'password' in request.json:
        response = registrasi_akun(uname, email, password)
    else if  request.json and  'uname' in request.json and 'device_name' in request.json
        response = registrasi_lampu(device_name, uname)
    else:
        response = {'status': 'failed', 'data': 'Bad Reques'}, 400

    return jsonify(response[0]), response[1]


# In[14]:


@app.route('/lampu/<uname>/', methods=['GET', 'POST'])
def semualampu(uname):
    if request.method == 'POST':
        if not request.json or not 'state' in request.json:
            response = {'status': 'failed', 'data': 'Bad Reques'}, 400
        else:
            response = update_lampu(uname, state)
    else:
        response = list_lampu(uname)
        
    return jsonify(response[0]), response[1]


# In[15]:


@app.route('/lampu/<uname>/<int:lampuid>/', methods=['GET', 'POST'])
def lampuspesifik(uname, lampuid):
    if request.method == 'POST':
        if not request.json or not 'state' in request.json:
            response = {'status': 'failed', 'data': 'Bad Reques'}, 400
        else:
            response = update_lampu(uname, state, lampuid)
    else:
        response = list_lampu(uname, lampuid)
    return jsonify(response[0]), response[1]


# In[16]:


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad Requesst'}), 404)


# In[ ]:


if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=False)

