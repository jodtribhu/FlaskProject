from flask import Flask, render_template ,request,url_for,redirect,session
import pymongo
import bcrypt
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key="testing"


#WebScrapping

URL = "https://en.wikipedia.org/wiki/Morse_code"
r = requests.get(URL)
morse_text_wikipedia=[]
morse_text_wikipedia_needed=""
soup = BeautifulSoup(r.content, 'html5lib') 
for para in soup.find_all('p'):
    l=para.get_text(strip=True)
    l = re.sub(r"/?\[\d+]", "", l)
    morse_text_wikipedia.append(l)

#Getting only first 3 paragraphs from wikipedia
morse_text_wikipedia_needed=morse_text_wikipedia_needed+morse_text_wikipedia[2]+morse_text_wikipedia[3]+morse_text_wikipedia[4]

#Getting images  from wikipedia
imagesrc=""
URL2="https://commons.wikimedia.org/wiki/File:Morse-code-tree.svg"
r2 = requests.get(URL2)
soup2= BeautifulSoup(r2.content, 'html5lib') 
pc = soup2.find('img')
imagesrc=pc['src']

imagesrc4=""
URL4="https://commons.wikimedia.org/wiki/File:Sorted_binary_tree.png"
r4 = requests.get(URL4)
soup4= BeautifulSoup(r4.content, 'html5lib') 
pc4 = soup4.find('img')
imagesrc4=pc4['src']

#Getting text for binary tree
btree_text=[]
req_btree_text=[]
URL3="https://www.studytonight.com/data-structures/introduction-to-binary-trees"
r3 = requests.get(URL3)
soup3= BeautifulSoup(r3.content, 'html5lib') 
for para2 in soup3.find_all('p'):
    l2=para2.get_text(strip=True)
    btree_text.append(l2)
req_btree_text.append(btree_text[0])
t=[]

for ul in soup3.find_all('ul',{"class": "content"}):
    lis=ul.find_all('li')
    for elem in lis:
        t.append(elem.text.strip())
terminologies=[]
terminologies.append(t[0])
terminologies.append(t[1])
terminologies.append(t[2])
terminologies.append(t[3])
terminologies.append(t[4])
terminologies.append(t[5])
terminologies.append(t[6])

print(req_btree_text)

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
    return render_template('home.html',morsetext=morse_text_wikipedia_needed,imagesrc=imagesrc,btree=req_btree_text[0],li1=terminologies[0],li2=terminologies[1],li3=terminologies[2],
    li4=terminologies[3],li5=terminologies[4],li6=terminologies[5],li7=terminologies[6],imagesrc4=imagesrc4)

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
            stringconvert=""
        elif(stringconvert!=None):
            converted=encrypt(stringconvert.upper())
            morse=""
            
        
        return render_template('logged_in.html', decoded=decoded,stringconvert=converted,mor=morse,str=stringconvert)
    if request.method == "GET":
        if "email" in session:
            # email = session["email"]
            return render_template('logged_in.html',decoded="",stringconvert="",mor="",str="")
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