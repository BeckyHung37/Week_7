from flask import Flask, request, redirect, render_template, session, url_for, json
from flask_sqlalchemy import SQLAlchemy #載入資料庫連線擴充套件
from datetime import datetime
app=Flask(
    __name__,
    static_url_path="/"
) #建立app物件
app.config['SECRET_KEY'] = 'becky' #用來解決flask使用session產生的錯誤

#MySQL Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:becky1qaz2wsx@localhost:3306/website"
# 模型( model )定義
#--------------------database---------------
# 獲取SQLAlchemy例項物件
db = SQLAlchemy() #class在python裡面唯有屬性、行為的物件
db.init_app(app) #SQLAlchemy裡面的一個function
class User(db.Model): #User是class的名稱
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, name, username, password): #class起手式
        self.name = name
        self.username = username
        self.password = password
#-----------------------------------------------        


#建立路徑/對應的處理函式
@app.route("/")
def index(): #用來回應網站首頁連線的函式
    return render_template("index.html")

@app.route("/member")
def member():
    if session["user_status"] == "signin":
        name = session['name']
        return render_template("member.html",name=name)
    else:
        return redirect("/")


@app.route("/error", methods=["GET"])
def error(): 
    errorMessage=request.args.get("message","")
    return render_template("error.html",errorMessage=errorMessage)

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    username_check = User.query.filter_by(username=username).first()
    if username_check:
        return redirect(url_for('error',message='帳號已被註冊'))
    else:
        create_user = User(name=name,username=username,password=password)
        db.session.add(create_user)
        db.session.commit()
        return redirect('/member')    

 


@app.route("/signin", methods=["POST"]) #不寫的話其實預設就是GET
def signin(): 
    username=request.form["username"]
    password=request.form["password"]
    check_username_and_password = User.query.filter_by(username=username,password=password).first() #取找到的第一筆資料 #User是表的意思
    if check_username_and_password:
        name = check_username_and_password.name
        session['username'] = username
        session["user_status"]="signin"
        session['name']=name
        return redirect('/member')
    else:
        return redirect(url_for("error",message='帳號或密碼輸入錯誤'))

@app.route("/signout", methods=["GET"]) 
def signout(): 
    session["user_status"]="signout"
    return redirect("/")


@app.route("/api/users", methods=["GET"]) 
def apiUser():
    username=request.args.get("username")
    print(username)
    search_user = User.query.filter_by(username=username).first()
    if search_user:
        _id = search_user.id
        name = search_user.name
        username = search_user.username
        session['username'] = username
        session["user_status"]="signin"

        return json.dumps({
                "data":{
                    "id":_id,
                    "name":name,
                    "username":username}})
    else:
        return json.dumps({
            "data":None})

app.run(port=3000) #啟動網站伺服器
