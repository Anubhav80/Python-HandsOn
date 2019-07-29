from flask import Flask,jsonify,request
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash
import base64 as b64
from functools import wraps
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:r********database-1.c3ujrvo0gkwg.us-east-1.rds.amazonaws.com:5432/postgres"
db = SQLAlchemy(app)


class User:
    def __init__(self,username,password):
        self.username=username
        self.password=password

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
        return(self.password_hash)

    def check_password_hash(self,hash,password):
        return check_password_hash(hash,password)

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        print(request.path)
        if request.cookies.get("session") is not None:
            username = b64.b64decode(request.cookies.get("session"))
            query=" select r.role_name,ac.permissions from access ac inner join roles_access ra on ac.access_id = ra.role_id inner join roles r on r.role_id = ra.role_id inner join users_role ur on ur.role_id = r.role_id inner join account a on a.id=ur.user_id where username='{}'".format(username.decode('utf-8'))
            result = db.engine.execute(query)
            result = result.fetchone()
            print(result)       
        else:
            return jsonify({"status":"NO session saved"})
    return wrap


def roles_perms_required(perm_names,role_names):
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            print(perm_names,role_names)
            if request.cookies.get("session") is not None:
                username = b64.b64decode(request.cookies.get("session"))
                query=" select r.role_name,ac.permissions from access ac inner join roles_access ra on ac.access_id = ra.access_id  inner join roles r on r.role_id = ra.role_id inner join users_role ur on ur.role_id = r.role_id inner join account a on a.id=ur.user_id where username='{}'".format(username.decode('utf-8'))
                result = db.engine.execute(query)
                result = result.fetchall()
                print(result,perm_names,role_names)
                for req_role in perm_names:
                    found=False
                    if any(req_role == resp_role[0] for resp_role in result):
                        found = True
                        pass
                if not found:
                    return jsonify({"status":"Unauthorized Access"})
            else:
                return jsonify({"status":"NO session saved"})
            return f(*args, **kwargs)
        return decorator
    return wrapper

@app.route('/',methods = ['GET']) 
# @login_required
@roles_perms_required(['Admin123','health'],['admin'])
def ReadUsers():
    # from sqlalchemy import text
    # sql = text('select * from users')
    # result = db.engine.execute(sql)
    # email = result.fetchone()[3]
    return jsonify({"email":""})

@app.route('/',methods = ['POST'])
def WriteUser():
    
    email = request.form['email']
    name = request.form['name']
    rollno = request.form['rollno']
    query = "INSERT INTO users (name,rollno,email,created_on,last_login) VALUES('{}', '{}', '{}', now(), now());".format(name,rollno,email)
    from sqlalchemy import text
    sql = text(query)
    
    try:
        result = db.engine.execute(sql)
        return jsonify({"email":email})
    except psycopg2.Error as e:
        print(e)
        return jsonify({"status":"something wrong occured"})
    
@app.route('/delete',methods = ['POST'])
def DeleteUser():
    name = request.form['name']
    query1 ="DELETE FROM users WHERE name = '{}';".format(name)
    from sqlalchemy import text
    sql1 = text(query1)

    try:
        result = db.engine.execute(sql1)
        return jsonify({"deleted":"True"})
    except psycopg2.Error as e:
        print(e)
        return jsonify({"status":"something wrong occured with delete"})
    except Exception:
        return jsonify({"status":"something wrong occured"})

@app.route('/SignUp',methods =['POST'])
@login_required
def signup():
    username=request.form['username']
    password=request.form['password']
    user= User(username,password)
    hash1= user.set_password(password)


    query1 ="UPDATE account SET password = '{}' WHERE username = '{}';".format(hash1,username)
    from sqlalchemy import text
    sql1 = text(query1)
    try:
        result = db.engine.execute(sql1)
        return jsonify({"Inserted":"True"})
    except (Exception,psycopg2.Error) as e:
        print(e)
        return jsonify({"status":"something wrong occured "}) 
@app.route('/health',methods=['GET'])
def health():
    return request.cookies.get("session")   

@app.route('/login',methods =['POST'])
def login():
    username=request.form.get('username')
    password=request.form.get('password')

    if username is None:
        return jsonify({"message":"username missing"})
    user = User(username,password)
    query ="SELECT id,password  FROM account WHERE username = '{}';".format(username)
    from sqlalchemy import text
    sql = text(query)
    try:
        result = db.engine.execute(sql)
        data= result.fetchone()
        print(data)
        if data is not None and bool(data) is not False:
            verify= user.check_password_hash(data[1],password)
            if verify is True:
                try:
                    ua = request.headers.get('User-Agent')
                    query = "INSERT INTO session (ua,last_login,account_id) VALUES('{}', now(),'{}');".format(ua,data[0])
                    sql = text(query)
                    res = db.engine.execute(sql)
                    print(res)
                except (Exception,psycopg2.Error) as e:
                    print('yes')
                    print(e)
                    pass
                res = jsonify({"isLogin":"{}".format(str(verify))})
                res.set_cookie("session",b64.b64encode(bytes(username,'utf-8')))
                return res
            else:
                return jsonify({"message":"username or password incorrect"})
        else:
             return jsonify({"message":"username or password incorrect"})
    except (Exception,psycopg2.Error) as e:
        print(e)
        return jsonify({"status":"something wrong occured "})  

@app.route('/getaccount',methods =['GET'])
def getaccountdetails():
    if request.cookies.get("session") is not None:
        username = b64.b64decode(request.cookies.get("session"))
        query = "Select username,email,last_login from account where username = '{}'".format(username.decode('utf-8'))
        try:
            result = db.engine.execute(query)
            result = result.fetchone() #return tuple
            if result is not None and len(result) > 0 :
                return jsonify({"user-details":{
                    "username":result[0],
                    "email":result[1],
                    "last_login":result[2]
                }})
        except (Exception,psycopg2.Error) as e:
            print(e)
            return jsonify({"status":"something wrong occured "})
    else:
        return jsonify({"status":"not logged in"})

@app.route('/getlastlogin',methods =['GET'])
@login_required
def getlastlogindetails():
    if request.cookies.get("session") is not None:
        username = b64.b64decode(request.cookies.get("session"))
        query = "SELECT account.firstname, account.lastname, account.email,session.ua,session.last_login FROM account FULL OUTER JOIN session ON account.id = session.account_id  where username = '{}'".format(username.decode('utf-8'))
       
        try:
          
            result = db.engine.execute(query)
            result = result.fetchall() #return tuple
            resp = [{'last_login':el[4]} for el in result]
           
            if result is not None and len(result) > 0 :
                return jsonify({'resp':{'email':result[0][2],'last_login_details':resp}})
        except (Exception,psycopg2.Error) as e:
            print(e)
            return jsonify({"status":"something wrong occured "})
    else:
        return jsonify({"status":"not logged in"})

@app.route('/role',methods =['GET'])
def verify_role():
    if request.cookies.get("session") is not None:
        username = b64.b64decode(request.cookies.get("session"))
        query="SELECT role from account WHERE  username = '{}'".format(username.decode('utf-8'))
       
        try:
            result = db.engine.execute(query)
            result = result.fetchone() #return tuple
          
            if result is not None and len(result) > 0 and result[0]=='admin':
                query="SELECT username from account WHERE  role = '{}'".format(result[0])
                result = db.engine.execute(query)
                result = result.fetchone() #return tuple
                resp=[ el for el in result]
               
                return jsonify({"user":resp})
            else: 
                return jsonify({"user-role":"Invalid"})
        except (Exception,psycopg2.Error) as e:
            print(e)
            return jsonify({"status":"something wrong occured "})



if __name__ == '__main__':
    app.run()