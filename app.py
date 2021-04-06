from flask import Flask, render_template ,request,url_for,redirect,session
import pymongo
import bcrypt
app = Flask(__name__)
app.secret_key="testing"

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client.get_database('FlaskDB')
records = db.users

MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
					'C':'-.-.', 'D':'-..', 'E':'.',
					'F':'..-.', 'G':'--.', 'H':'....',
					'I':'..', 'J':'.---', 'K':'-.-',
					'L':'.-..', 'M':'--', 'N':'-.',
					'O':'---', 'P':'.--.', 'Q':'--.-',
					'R':'.-.', 'S':'...', 'T':'-',
					'U':'..-', 'V':'...-', 'W':'.--',
					'X':'-..-', 'Y':'-.--', 'Z':'--..',
					'1':'.----', '2':'..---', '3':'...--',
					'4':'....-', '5':'.....', '6':'-....',
					'7':'--...', '8':'---..', '9':'----.',
					'0':'-----', ', ':'--..--', '.':'.-.-.-',
					'?':'..--..', '/':'-..-.', '-':'-....-',
					'(':'-.--.', ')':'-.--.-'}

letters = "-ETIANMSURWDKGOHVF*L*PJBXCYZQ**54*3***2**+****16=/*****7***8*90"
def morseToString(morse):
    index = 1
    message = ""
    for i in range(len(morse)):
        if i <len(morse)-1:
            if morse[i] == " ":
                message += letters[index-1]
                index = 1
            elif morse[i] == "." :
                index = 2*index
                if(index >len(letters)):
                    break
            elif morse[i] == "-":
                index = 2*index + 1
                if(index >len(letters)):
                    break
        else:
            if morse[i] == "." :
                index = 2*index
                if(index >len(letters)):
                    break
            elif morse[i] == "-":
                index = 2*index + 1
                if(index >len(letters)):
                    break
            message += letters[index-1]
            index = 1
    return message.replace("*"," ")

def encrypt(message):
	cipher = ''
	for letter in message:
		if letter != ' ':
			cipher += MORSE_CODE_DICT[letter] + ' '
		else:
			cipher += ' '

	return cipher

@app.route("/", methods=[ 'get'])
def home():
    return render_template('home.html')

@app.route("/register", methods=['post', 'get'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password1")
        user_found = records.find_one({"name": user}) 
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'User Already Exists'
            return render_template('index.html', message=message)
        if email_found:
            message = 'Email Already Exists'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', error=message)
        else:
            message = 'Email not found'
            return render_template('login.html', error=message)
    return render_template('login.html')

@app.route('/logged_in', methods=["POST", "GET"])
def logged_in():
    if request.method == "POST":
        decoded=""
        converted=""
        stringconvert=request.form.get("stringconvert")
        morse = request.form.get("morsecode")
        if(morse!=None):
            decoded = morseToString(morse) 
        if(stringconvert!=None):
            converted=encrypt(stringconvert.upper())
        
        return render_template('logged_in.html', decoded=decoded,stringconvert=converted)
    if request.method == "GET":
        if "email" in session:
            # email = session["email"]
            return render_template('logged_in.html',decoded="",stringconvert="")
        else:
            return redirect(url_for("login"))

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')

if __name__ == "__main__":
   app.run()