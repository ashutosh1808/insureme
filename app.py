from flask import Flask,render_template,request,redirect,url_for,session
import pickle
from sqlite3 import *
import hashlib
from forex_python.converter import CurrencyRates
#hashlib for encryption
app=Flask(__name__)
app.secret_key="insuremerocks"

@app.route("/logout",methods=["GET","POST"])
def logout():
	session.clear()
	return redirect(url_for('login'))

@app.route("/",methods=["GET","POST"])
def home():
	if "username" in session:
		return render_template("home.html",name=session["username"])
	else:
		return redirect(url_for("login"))


@app.route("/login",methods=["GET","POST"])
def login():
	if request.method=="POST":
		un=request.form["username"]
		pw=request.form["password"]
		res=hashlib.sha256(pw.encode())
		pw3=res.hexdigest()
		con=None
		try:
			con=connect("auth.db")
			cursor=con.cursor()
			sql="select * from users where username='%s' and password='%s'"
			cursor.execute(sql%(un,pw3))
			data=cursor.fetchall()
			if len(data)==0:
				return render_template("login.html",msg="invalid login")
			else:
				session["username"]=un
				return redirect(url_for("home"))
		except Exception as e:
			return render_template("login.html",msg=e)
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
	if request.method=="POST":
		username=str(request.form["username"])
		pw1=str(request.form["pw1"])
		pw2=str(request.form["pw2"])
		if pw1==pw2:
			con=None
			try:
				con=connect("auth.db")
				cursor=con.cursor()
				res=hashlib.sha256(pw1.encode())
				pw3=res.hexdigest()
				sql="insert into users values('%s','%s')"
				cursor.execute(sql%(username,pw3))
				con.commit()
				return redirect(url_for('login'))
			except IntegrityError:
			    con.rollback()
			    return render_template("signup.html",msg="User already exists")
			except Exception as e:
				con.rollback()
				return render_template("signup.html",msg=e)
			finally:
				if con is not None:
					con.close()
		else:
			return render_template("signup.html",msg="Passwords do not match")
	else:
		return render_template("signup.html")


@app.route("/predict",methods=["GET","POST"])
def predict():
	if request.method=="POST":
		age=float(request.form["age"])
		bmi=float(request.form["bmi"])
		ch=int(request.form["ch"])
		db=request.form["db"]
		bp=request.form["bp"]
		cd=request.form["cd"]
		ka=int(request.form["ka"])
		ms=int(request.form["ms"])
		sx=request.form["sx"]
		smk=request.form["smk"]
		raw_text=u"\u20B9"
		with open("is.model","rb") as f:
			model=pickle.load(f)
		data=[[age,bmi,ch,db,bp,cd,ka,ms,sx,smk]]
		res=model.predict(data)
		c=CurrencyRates()
		res_in_inr=c.convert("USD","INR",res)
		cost=round(res_in_inr[0],0)
		con=None
		try:
			con=connect("insurance.db")
			cursor=con.cursor()
			sql="insert into details values('%f','%f','%d','%s','%s','%s','%d','%d','%s','%s','%f')"
			cursor.execute(sql%(age,bmi,ch,db,bp,cd,ka,ms,sx,smk,cost))
			con.commit()
			return render_template("predict.html",msg="Your medical insurance cost for this year is "+str(raw_text)+str(cost))
		except Exception as e:
			con.rollback()
			return render_template("predict.html",msg=e)
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("predict.html")

@app.route("/bmi",methods=["GET","POST"])
def bmi():
	if request.method=="POST":
		ht=float(request.form["ht"])
		wt=float(request.form["wt"])
		ans=wt/ht**2
		res=round(ans,2)
		return render_template("bmi.html",msg=str(res))
	else:
		return render_template("bmi.html")
if __name__=="__main__":
	app.run(debug=True,use_reloader=True)
