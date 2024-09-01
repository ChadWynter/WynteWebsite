# importing Flask and other modules
from contextlib import redirect_stderr
from flask import Flask, redirect, url_for, render_template, request, session, flash, make_response
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import hashlib
import random, os
from datetime import timedelta, date #permanent sessions
from werkzeug.utils import secure_filename #getting files

  
# Flask constructor
app = Flask(__name__)

#mysql setup
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Fundamentals09!'
app.config['MYSQL_DB'] = 'vote_info'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#email service setup
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'SEF2022Team9@gmail.com'
app.config['MAIL_PASSWORD'] = 'Team9!2022'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
mysql = MySQL(app)
#secret key to encrypt and ecrypt session data
app.secret_key = "Fundamentals"
#length of permanent session
app.permanent_session_lifetime = timedelta(minutes=5) 
# A decorator used to tell the application which URL is associated function

@app.route('/')
def home():
   return render_template("index.html")



#setting up session data
@app.route("/login", methods=["POST", "GET"])
def login():
   if request.method == "POST":
      user = request.form["nm"]
      password = request.form["pword"]
      #hashing the password for comparison to db value
      salt = "Team9"
      db_password = password + salt
      h = hashlib.sha512(db_password.encode())
      #checking against msyql data
      cur = mysql.connection.cursor()
      query_string="SELECT password,first_name,locked,email,account_type FROM users WHERE id=%s"
      cur.execute(query_string,[user])
      results = cur.fetchall()

      #checking if id exists
      if len(results) == 0:
         flash("Incorrect ID", category='danger') 
         return redirect(url_for("login"))
      name = results[0]['first_name']

      #checking if password matches password in database
      if(h.hexdigest() == results[0]['password']):
         #checking to see if account is locked
         if results[0]['locked'] >= 3:
            flash("Too many incorrect attempts. Please select forgot password to change password", category='danger') 
            return redirect(url_for("login"))
         else:
            #checking to see if account is in pending status 
            cur3 = mysql.connection.cursor()
            query_string="SELECT id FROM pending WHERE id=%s"
            cur3.execute(query_string,[user])
            results1 = cur3.fetchall()
            if len(results1) == 0:
            #setting locked back to zero then adding user to session
               cur2 = mysql.connection.cursor()
               query2="UPDATE users SET locked=0 WHERE id=%s"
               cur2.execute(query2,[user])
               mysql.connection.commit()
               session.permanent = True
               session["user"] = user
               flash(f"Login Succesful! Welcome {name}",category="success") #flashing messages
               type = results[0]["account_type"]
               if type == "admin":
                  return redirect(url_for("admin"))
               elif type =="manager":
                  return redirect(url_for("manager"))
               else:
                  return redirect(url_for("user"))
            else:
               flash(f"Account has not been verified. Please wait 1-3 business days for verification to occur")
               return redirect(url_for("login"))

      else:
         #checking if account is locked
         if results[0]['locked'] >= 3:
            flash("Too many incorrect attempts. Please select forgot password to change password", category='danger') 
            return redirect(url_for("login"))
         else:
            #incrementing locked variable in database
            new_locked = results[0]['locked'] + 1
            cur3 = mysql.connection.cursor()
            query3="UPDATE users SET locked=%s WHERE id=%s"
            cur3.execute(query3,(str(new_locked),user))
            mysql.connection.commit()
            print(results)
            em = results[0]['email']
            msg = Message("Login Alert", sender = 'SEF2022Team9@gmail.com', recipients = [em])
            msg.body = "Login Alert! There has been an attempt to Login to your Elect-Me account\nIf this was not you, please change your password"
            mail.send(msg)
            flash("incorrect password, please try again", category='danger') 
            return redirect(url_for("login"))
     
   else:
      if "user" in session:
         flash("Already logged in", category="warning")
         return redirect(url_for("decide"))   
      return render_template("login.html")


#sign up page
@app.route("/sign-up", methods=["POST", "GET"])
def sign_up():
   if request.method == "POST":
      age=request.form["age"]
      fname=request.form["fname"]
      lname=request.form["lname"]
      email=request.form["email"]
      addy=request.form["addy"]
      zip=request.form["zip"]
      id1=request.form['id1'] #need to add these to database
      id2=request.form['id2']
      id1type=request.form['idtype1']
      id2type=request.form['idtype2']
      security1=request.form["s1"]
      security2=request.form["s2"]
      security3=request.form["s3"]
      password=request.form["pword"]
      type=request.form["role"]
      print(type)
      #hashing the password
      salt = "Team9"
      db_password = password + salt
      h = hashlib.sha512(db_password.encode())


      cur = mysql.connection.cursor()
      query_string="SELECT first_name FROM users WHERE email=%s"
      cur.execute(query_string,[email])
      results = cur.fetchall()
      if len(results) != 0:
         flash(f"This email address is already registered, please Login, {results[0]['first_name']}", category="warning")
         return redirect(url_for("login"))
      else:
         #creating account
         cur2 = mysql.connection.cursor()
         query_string="INSERT INTO users (first_name,last_name,email,password,security_question,locked,age,address,zip,Security_question2,Security_question3,id1_type,id2_type,id1_number,id2_number,account_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
         cur2.execute(query_string,[fname,lname,email,h.hexdigest(),security1,'0',age,addy,zip,security2,security3,id1type,id2type,id1,id2,type])
         mysql.connection.commit()
         cur3 = mysql.connection.cursor()
         query_string="SELECT id FROM users WHERE email=%s"
         cur3.execute(query_string,[email])
         results = cur3.fetchall()
         #adding id to pending table for verification
         cur4 = mysql.connection.cursor()
         query_string="INSERT INTO pending (id) VALUES (%s)"
         cur4.execute(query_string,[str(results[0]["id"])])
         mysql.connection.commit()
         #sending email
         msg = Message("Account Creation Alert", sender = 'SEF2022Team9@gmail.com', recipients = [email])
         msg.body = "Welcome to ElectMe! If you have not created an account please ignore this email\n Your Voter ID is:  " + str(results[0]['id']) + "   Please keep that number stored in a safe place."
         mail.send(msg)
         flash("Account created, an verification email has been sent. Please view the email to access Voter ID", category="success")
         return redirect(url_for("login"))

   else:
      return render_template("sign-up.html")


#forgot password page
@app.route("/forgotpassword", methods=["POST", "GET"])
def forgotpassword():
   #random security question generator
   questions={"What was the first car you drove?","What street did you live on in first grade?","What city were you born in?"}

   displayquestion=random.sample(questions,2)
   displayquestion1=displayquestion[0]
   displayquestion2=displayquestion[1]

   if request.method == "POST":
      voterid=request.form["voterid"]
      security1=request.form["s-1"]
      security2=request.form["s-2"]
      password=request.form["pword"]
      salt = "Team9"
      db_password = password + salt
      h = hashlib.sha512(db_password.encode())
      
      cur = mysql.connection.cursor()
      query_string="SELECT Security_question,Security_question2,Security_question3 FROM users WHERE Id=%s"
      cur.execute(query_string,[voterid])
      results = cur.fetchall()
      if len(results) == 0:
         flash(f"Voterid doesn't exist", category="warning")
         return render_template("login.html")
      else:
         q1 = results[0]['Security_question']
         q2 = results[0]['Security_question2']
         q3 = results[0]['Security_question3']

         if (security1.lower() == q1.lower() or security1.lower() == q2.lower() or security1.lower() == q3.lower()):
            if(security2.lower() == q1.lower() or security2.lower() == q2.lower() or security2.lower() == q3.lower()):
               cur2 = mysql.connection.cursor()
               query_string="UPDATE users SET password=%s WHERE id=%s"
               cur2.execute(query_string,[h.hexdigest(),voterid])
               cur3 = mysql.connection.cursor()
               query_string="UPDATE users SET locked=0 WHERE id=%s"
               cur3.execute(query_string,[voterid])
               mysql.connection.commit()
               flash(f"Password changed successfully", category="success")
               return redirect(url_for('login'))
            else:
               flash(f"Change password failed", category="warning")
               return redirect(url_for('login'))
         else:
            flash(f"Change password failed", category="warning")
            return redirect(url_for('login'))


   else:
      return render_template("forgotpassword.html", displayquestion1=displayquestion1, displayquestion2=displayquestion2)
      

#forgot voter ID page
@app.route("/forgotvoterid", methods=["POST", "GET"])
def forgotvoterid():
   #random security question generator
   questions={"What was the first car you drove?","What street did you live on in first grade?","What city were you born in?"}

   displayquestion=random.sample(questions,2)
   displayquestion1=displayquestion[0]
   displayquestion2=displayquestion[1]

   if request.method == "POST":
      email=(request.form["email"])
      security1=request.form["s-1"]
      security2=request.form["s-2"]
      
      cur = mysql.connection.cursor()
      query_string="SELECT Security_question,Security_question2,Security_question3,id FROM users WHERE email=%s"
      cur.execute(query_string,[email])
      results = cur.fetchall()
      if len(results) == 0:
         flash(f"Email doesn't exist", category="warning")
         return render_template("login.html")
      else:
         q1 = results[0]['Security_question']
         q2 = results[0]['Security_question2']
         q3 = results[0]['Security_question3']

         if (security1.lower() == q1.lower() or security1.lower() == q2.lower() or security1.lower() == q3.lower()):
            if(security2.lower() == q1.lower() or security2.lower() == q2.lower() or security2.lower() == q3.lower()):
               msg = Message("Account Creation Alert", sender = 'SEF2022Team9@gmail.com', recipients = [email])
               msg.body = "Id look up requested\n Your Voter ID is:  " + str(results[0]['id']) + "   Please keep that number stored in a safe place."
               mail.send(msg)
               flash("Please view the email to access Voter ID", category="success")
               return redirect(url_for('login'))
            else:
               flash(f"Change password failed", category="warning")
               return redirect(url_for('login'))
         else:
            flash(f"Change password failed", category="warning")
            return redirect(url_for('login'))


   else:
      return render_template("forgotvoterid.html", displayquestion1=displayquestion1, displayquestion2=displayquestion2)

#search user information
#voterid here means voter info, including ID,zip,name,etc
@app.route("/searchuser", methods=["POST", "GET"])
def searchuser():
   if request.method == "POST":
      voterid=request.form["voterid"]
      cur = mysql.connection.cursor()
      query_string="SELECT first_name,last_name,email,age,address,id FROM users WHERE Id=%s" #search user by ID
      cur.execute(query_string,[voterid])
      results = cur.fetchall()
      if len(results) == 0:
         query_string="SELECT first_name,last_name,email,age,address,id FROM users WHERE zip=%s" #search user by zip
         cur.execute(query_string,[voterid])
         results = cur.fetchall()
         if len(results) ==0:
            query_string="SELECT first_name,last_name,email,age,address,id FROM users WHERE first_name=%s" #search user by name
            cur.execute(query_string,[voterid])
            results = cur.fetchall()
            if len(results) ==0:
               flash(f"Voter doesn't exist", category="warning")
               return redirect(url_for('searchuser'))
            else:
               return render_template("searchuser.html", results = results)
         else:
            return render_template("searchuser.html", results = results)
      else:
         return render_template("searchuser.html", results = results)

   else:
      return render_template("searchuser.html")


#changing user information if logged in 
@app.route("/address-change.html", methods=["POST", "GET"])
def change():
   id = session['user']
   if request.method == "POST":
      fname = request.form["fname"]
      lname = request.form["lname"]
      email = request.form["email"]
      number = request.form["number"]
      addy = request.form["addy"]
      zip = request.form["zip"]

      cur2 = mysql.connection.cursor()
      query_string="UPDATE users SET first_name=%s,last_name=%s,email=%s,number=%s,address=%s,zip=%s WHERE id=%s"
      cur2.execute(query_string,[fname,lname,email,number,addy,zip,id])
      cur2 = mysql.connection.cursor()
      mysql.connection.commit()

      flash(f"Account information changed successfully", category="success")
      return redirect(url_for("decide"))
   else:
      if "user" in session:  
         cur = mysql.connection.cursor()
         query_string="SELECT first_name,last_name,email,number,address,zip FROM users WHERE id=%s"
         cur.execute(query_string,[id])
         results = cur.fetchall()
         return render_template("address-change.html", content = results)
      else:
         return redirect(url_for("login"))
   
#user session
@app.route("/user")
def user():
   if "user" in session:
      user = session["user"]
      return render_template("user.html", user=user)
   else:
      flash("You are not logged in", category='danger')
      return redirect(url_for(login))



#closing user session
@app.route("/logout")
def logout():
   if "user" in session:
      user = session["user"]
      session.pop("user", None) #removing user from dictionary
      #flashing a logout message for succesful logout
      flash(f"you have been logged out successfully, {user}", category="info")
   return redirect(url_for("login"))


#ignoring favicon.ico
@app.route("/favicon.ico")  
def ignore():
   return("<p>Invalid routing.. continue</p>")

#taking in argument
@app.route("/<id>", methods=["POST", "GET"])  
def usertest(id):
   if request.method == "POST":
      print(id)
   else:
      if (id == "favicon.ico"):
         print("Do Nothing")
      else: 
         print("id taken from url: " +  id)
         res = make_response(redirect(url_for(("confirm"))))
         res.set_cookie('userChosen', id)
         return res
      #return redirect(url_for("confirm",content=id))

#populating html page from the argument taken in above. using get arguments
@app.route("/confirm", methods=["POST", "GET"])  
def confirm():
   id = request.cookies.get('userChosen', 0)
   if request.method == "POST":
      
      #remove id from pending and switch status to go if value = confirm
      #remove id from pending and switch status to stop if value = deny
      choice = request.form["confirm-deny"]
      if(choice == "confirm"):
         cur = mysql.connection.cursor()
         query_string="DELETE FROM pending WHERE id=%s"
         cur.execute(query_string,[id])
         results = cur.fetchall()
         mysql.connection.commit()

         cur2 = mysql.connection.cursor()
         query_string="SELECT email FROM users WHERE id=%s"
         cur2.execute(query_string,[id])
         results = cur2.fetchall()
         email = results[0]['email']
         #sending confirmation message
         msg = Message("Account Verified", sender = 'SEF2022Team9@gmail.com', recipients = [email])
         msg.body = "Your account has been verified and is ready to use!"
         mail.send(msg)
         return redirect(url_for("decide"))
      else: 
         #notifying user that account has been denied,
         msg = Message("Account Denied", sender = 'SEF2022Team9@gmail.com', recipients = [email])
         msg.body = "Your account has been declined. Please visit our website or contact us to obtain more information."
         mail.send(msg)
         return redirect(url_for("decide"))
   else:
      if "user" in session:
         #search database to fill fields
         cur = mysql.connection.cursor()
         query_string="SELECT first_name,last_name,address,zip,id1_type,id2_type,id1_number,id2_number FROM users WHERE id=%s"
         cur.execute(query_string,[id])
         results = cur.fetchall()

         return render_template("confirm.html", content=results)
      else:
         flash(f"Please login", category='danger')
         return redirect(url_for("login"))



@app.route("/test", methods=["POST", "GET"])  
def test():
   if request.method == "GET":
      print("testing")
      return redirect(url_for("decide"))


@app.route("/vote", methods=["GET", "POST"])
def vote():
   if "user" not in session:
         return redirect(url_for("login"))
   user=session["user"]
   cur = mysql.connection.cursor()
   query_string="SELECT * FROM users WHERE id=%s"
   cur.execute(query_string,[user])
   userRes = cur.fetchall()
   voted = userRes[0]["voted"]
   accountType = userRes[0]["account_type"]
   if accountType != "voter":
      flash("Only voter accounts can vote.", category='danger')
      return redirect(url_for("decide"))
   if voted == 1:
      flash("You have already voted.", category='danger')
      return redirect(url_for("decide"))

   returnVals = []
   zipCode = userRes[0]["zip"]
   zipFour = userRes[0]["zip_four"]
   #print(zipCode)
   #print(zipFour)
   #Get all the precincts
   cur = mysql.connection.cursor()
   query_string = "SELECT * FROM precincts"
   cur.execute(query_string)
   results = cur.fetchall()
   idPre = None
   #Go through all of them and see if the precinct has a ziprange matching our zipcode+4
   for val in results:
      count = 1
      zipFiveS = "zip_five"
      zipFourS = "zip_four"
      cont = True
      while cont:
         try:
            zfi = zipFiveS + str(count)
            zfo = zipFourS + str(count)
            zipFiveT = int(val[zfi])
            zipFourSt = int(val[zfo][0:4])
            zipFourEnd = int(val[zfo][4:8])
            if zipCode == zipFiveT and (zipFour >= zipFourSt and zipFour <= zipFourEnd):
               idPre = val["idprecincts"]
               cont = False
            count += 1
         except:
            cont = False
   #If we found a precinct that matched
   if idPre != None:
      cur = mysql.connection.cursor()
      query_string = "SELECT * FROM ballots where idprecincts=%s"%(idPre)
      cur.execute(query_string)
      results = cur.fetchall()
      if len(results) == 0:
         flash("There are currently no ongoing ballots to vote in.", category='danger')
         return redirect(url_for("decide"))
      ballot = results[0]
      #Make sure we only include races from the election since we did not stop them
      #From putting whatever races they wanted with the election
      election = ballot["election"]
      cont = True
      count = 1
      #Go through every race associated with the ballot
      while cont:
         try:
            raceString = "race" + str(count)
            race = ballot[raceString]
            cur = mysql.connection.cursor()
            query_string = "SELECT * FROM race where race_title=\"%s\""%(race)
            cur.execute(query_string)
            results = cur.fetchall()
            raceDict = results[0]
            #Only include it if it is in the election we are focusing on
            if raceDict["election_title"] == election:
               candCount = (len(raceDict.keys()) - 4)/2
               count2 = 1
               while (count2 < candCount+1):
                  if raceDict["election_candidate" + str(count2)] == None:
                     break
                  else:
                     count2 += 1
               #Return a tuple of the race dictionary and the number of candidates so we know what to count to when
               #creating the html
               returnVals.append((raceDict, count2-1))
            count += 1
         except:
            cont = False
   if request.method == "POST":
      if request.form['choose'] == 'vote':
         candVotes = []
         for race in returnVals:
            raceDict = race[0]
            title = raceDict["race_title"]
            id = raceDict["idraces"]
            vote = request.form[title]
            candVotes.append((title, vote))
            numCands = race[1]
            count = 1
            while (count < numCands + 1):
               candString = "election_candidate" + str(count)
               candName = raceDict[candString]
               if candName == vote:
                  break
               count += 1
            candString = "cand_votes" + str(count)
            query_string = "SELECT * FROM race WHERE race_title=%s"
            cur.execute(query_string, [title])
            results = cur.fetchall()
            curVotes = int(results[0][candString])
            query_string="UPDATE race SET %s=\"%s\" WHERE idraces=%s"%(candString, str(curVotes+1), id)
            cur.execute(query_string)
            mysql.connection.commit()
            query_string="INSERT into voteaudit (userid, race_title, cand_vote) VALUES (%s, %s, %s)"
            cur.execute(query_string, [user, title, vote])
            mysql.connection.commit()
         cur = mysql.connection.cursor()
         query_string="UPDATE users SET voted=1 WHERE id=%s"%(user)
         cur.execute(query_string)
         mysql.connection.commit()
         return render_template("summary.html", results=candVotes)
      else:
         races = []
         currCand = request.form['choose']
         cur = mysql.connection.cursor()
         query_string="SELECT * FROM race"
         cur.execute(query_string)
         raceRes = cur.fetchall()
         for race in raceRes:
            count = 1
            cont = True
            while cont:
               try:
                  candString = 'election_candidate' + str(count)
                  name = race[candString]
                  if name == currCand:
                     candCount = (len(race.keys()) - 4)/2
                     count2 = 1
                     while (count2 < candCount+1):
                        if race["election_candidate" + str(count2)] == None:
                           break
                        else:
                           count2 += 1
                     races.append((race, count2-1))
                     cont = False
                  count += 1
               except:
                  cont = False
         return render_template("cand_profile.html", results=[currCand, races])
   else:
      return render_template("vote.html", results = returnVals)

@app.route("/declare", methods=["POST", "GET"])
def declare():
   if "user" not in session:
         return redirect(url_for("login"))
   user=session["user"]
   cur = mysql.connection.cursor()
   query_string="SELECT * FROM users WHERE id=%s"
   cur.execute(query_string,[user])
   userRes = cur.fetchall()
   voted = userRes[0]["voted"]
   accountType = userRes[0]["account_type"]
   # if accountType != "manager":
   #    flash("Only managers can declare an election.", category='danger')
   #    return redirect(url_for("decide"))
   query_string="SELECT * FROM election"
   cur.execute(query_string)
   elecRes = cur.fetchall()
   if request.method == "POST":
      electitle = request.form["election"]
      query_string="SELECT * FROM election WHERE election_title=\"%s\""%(electitle)
      cur.execute(query_string)
      decElec = cur.fetchall()
      elecId = decElec[0]['idelections']
      query_string="UPDATE election SET status=\"finished\" WHERE idelections=%s"%(elecId)
      cur.execute(query_string)
      mysql.connection.commit()
      flash("%s has been declared finished."%(electitle), category='danger')
      return redirect(url_for("decide"))
   else:
      displayElec = []
      todayDate = str(date.today())
      dateSplit = todayDate.split('-')
      print(dateSplit)
      for election in elecRes:
         print(election)
         # elecDate = (election['election_date']).split('-')
         # if (elecDate[0] > dateSplit[0] or (elecDate[0] == dateSplit[0] and elecDate[1] > dateSplit[1]) or (elecDate[0] == dateSplit[0] and elecDate[1] == dateSplit[1] and elecDate[2] > dateSplit[2])):
         #    skip = True
         if (election['status'] == "finished"):
            skip = True
         else:
            displayElec.append(election)
      return render_template("declare.html", results=displayElec)

      
@app.route("/viewelections", methods=["GET"])
def viewelections():
   if request.method == "GET":
      cur = mysql.connection.cursor()
      query_string="SELECT * FROM election"
      cur.execute(query_string)
      elecRes = cur.fetchall()

      finishedElec = []
      for election in elecRes:
         if election['status'] == "finished":
            query_string="SELECT * FROM race WHERE election_title=\"%s\""%(election["election_title"])
            cur.execute(query_string)
            raceRes = cur.fetchall()
            raceList = []
            for race in raceRes:
               candCount = (len(race.keys()) - 4)/2
               count = 1
               winner = None
               winnerVotes = float('-inf')
               while (count < candCount+1):
                  if race["election_candidate" + str(count)] == None:
                     break
                  else:
                     if int(race["cand_votes" + str(count)]) > winnerVotes:
                        winnerVotes = int(race["cand_votes" + str(count)])
                        winner = race["election_candidate" + str(count)]
                     count += 1
               raceList.append((race, count-1, (winner, winnerVotes))) 
            finishedElec.append((election["election_title"], raceList))
      return render_template("view_elections.html", results=finishedElec)




   

@app.route("/setuprace", methods=["GET", "POST"])
def setuprace():
   if request.method == "POST":
         zipFiveList = []
         count = 1
         #Build the list of zip 5s and their ranges using try except
         cont = True
         while cont:
            zipFiveS = "zipFive" + str(count)
            try:
               zipFiveList.append(request.form[zipFiveS])
            except:
               cont = False
            count += 1

         electiontitle=request.form["electiontitle"] #this is the race title
         election=request.form['election']
         electiondate=request.form["electiondate"]
         electioncandidate1=request.form["zipFive1"]
         #Insert the base information of the precinct once we have guaranteed it will fit
         #This will automatically leave all extra zip_five and zip_four columns as null to be changed later

         cur = mysql.connection.cursor()
         query_string="INSERT INTO race (race_title,election_candidate1, cand_votes1, race_term,election_title) VALUES (%s,%s,%s,%s,%s)"
         firstZipFive = zipFiveList[len(zipFiveList)-1]

         cur.execute(query_string, [electiontitle,firstZipFive, "0", electiondate,election])
         mysql.connection.commit()

         #if(len(zipFiveList) == 2):
            #print(zipFiveList)

         #We want to find the precinct id for easier reference and to let the admin know at the end
         cur = mysql.connection.cursor()
         query_string = "SELECT * FROM race WHERE race_title = '%s'"%(electiontitle)
         cur.execute(query_string)
         results = cur.fetchall()
         id = results[0]["race_title"]
         #Start at 2 because 1 is already in the table
         zipCount = 2
         while (zipCount < len(zipFiveList) + 1):
            #Create the respective string for the column
            zipFiveS = "election_candidate" + str(zipCount)
            zipFive = zipFiveList[zipCount-1]
            candVoteS = "cand_votes" + str(zipCount)
            #This try except block tries to update preexisting columns of zip_five and zip_four if they exist
            #otherwise it goes into the except block where it creates these columns if they dont
            try:
               cur = mysql.connection.cursor()
               query_string = "UPDATE race SET %s = \"%s\" WHERE race_title = '%s'"%(zipFiveS, zipFiveList[zipCount-2], id)
               cur.execute(query_string)
               mysql.connection.commit()
               zipCount += 1

            except:
               cur = mysql.connection.cursor()
               query_string = "ALTER TABLE race ADD COLUMN %s VARCHAR(45)"%(zipFiveS)
               cur.execute(query_string)
               query_string = "ALTER TABLE race ADD COLUMN %s VARCHAR(45) DEFAULT \"0\""%(candVoteS)
               cur.execute(query_string)
               mysql.connection.commit() 
         
         return redirect(url_for("setuprace")) 

   else:
      cur = mysql.connection.cursor()
      query_string="SELECT election_title FROM election"
      cur.execute(query_string)
      results = cur.fetchall()
      #print(results)
      return render_template("setuprace.html", results = results)

@app.route("/newsetupelection", methods=["GET", "POST"])
def newsetupelection():
   if request.method == "POST":
      zipFourList = []
      count1 = 1
      #Build the list of zip 5s and their ranges using try except
      cont = True
      while cont:
         zipFourS = "zipFour" + str(count1)
         try:
            zipFourList.append(request.form[zipFourS])
         except:
            cont = False
         count1 += 1

      print(zipFourList)

      electiontitle=request.form["electiontitle"]
      electiondate=request.form["electiondate"]
         #electioncandidate1=request.form["zipFive1"]
         #Insert the base information of the precinct once we have guaranteed it will fit
         #This will automatically leave all extra zip_five and zip_four columns as null to be changed later

      cur = mysql.connection.cursor()
      query_string="INSERT INTO election (election_title,election_date,precinct_id1) VALUES (%s,%s,%s)"
      firstZipFour = zipFourList[len(zipFourList)-1]
         #print(electioncandidate1)
         #print(firstZipFive)
         #print(firstZipFive)

      cur.execute(query_string, [electiontitle,electiondate,firstZipFour])
      mysql.connection.commit()

         #if(len(zipFiveList) == 2):
            #print(zipFiveList)

         #We want to find the precinct id for easier reference and to let the admin know at the end
      cur = mysql.connection.cursor()
      query_string = "SELECT * FROM election WHERE election_title = '%s'"%(electiontitle)
      cur.execute(query_string)
      results = cur.fetchall()
      print(results)
      id = results[0]["election_title"]
      print(id)
         #print(zipFiveList)

         
      zipCount1 = 2
      while (zipCount1 < len(zipFourList) + 1):
            #Create the respective string for the column
         zipFourS = "precinct_id" + str(zipCount1)
         zipFour = zipFourList[zipCount1-1]
         print(zipFour)
            #This try except block tries to update preexisting columns of zip_five and zip_four if they exist
            #otherwise it goes into the except block where it creates these columns if they dont
         try:
            cur = mysql.connection.cursor()
            query_string = "UPDATE election SET %s = \"%s\" WHERE election_title = '%s'"%(zipFourS, zipFourList[zipCount1-2], id)
            cur.execute(query_string)
            mysql.connection.commit()
            print(2)
            zipCount1 += 1

         except:
            cur = mysql.connection.cursor()
            query_string = "ALTER TABLE election ADD COLUMN %s VARCHAR(25)"%(zipFourS)
            cur.execute(query_string)
            mysql.connection.commit() 

      return redirect(url_for("newsetupelection")) 
   else:
      cur = mysql.connection.cursor()
      query_string="SELECT idprecincts FROM precincts"
      cur.execute(query_string)
      results = cur.fetchall()
      return render_template("newsetupelection.html", results = [results])

@app.route("/newballot", methods=["POST", "GET"])
def newballot():
   if request.method == "POST":
      election = request.form["election"]
      precinctId = request.form["precinct"]
      raceList = []
      count = 1
      cont = True
      while cont:
         raceS = "race" + str(count)
         try:
            raceList.append(request.form[raceS])
         except:
            cont = False
         count += 1
      firstRace = request.form["race1"]

      #Make sure that a ballot for this precinct is not already created
      cur = mysql.connection.cursor()
      query_string="SELECT idprecincts FROM ballots"
      cur.execute(query_string)
      results = cur.fetchall()
      for idR in results:
         id = str(idR["idprecincts"])
         if precinctId == id:
            flash(f"Error: A Ballot for precinct id %s has already been created."%(precinctId), category="danger")
            return redirect(url_for("newballot"))
      cur2 = mysql.connection.cursor()
      query_string="SELECT idprecincts FROM precincts"
      cur2.execute(query_string)
      results = cur2.fetchall()
      for idR in results:
         id = str(idR["idprecincts"])
         #If we found a match, create the ballot
         if precinctId == id:
            cur3 = mysql.connection.cursor()
            query_string="INSERT INTO ballots (election, race1, idprecincts,active) VALUES (%s, %s, %s, %s)"
            cur3.execute(query_string, [election, firstRace, precinctId,"false"])
            mysql.connection.commit()
            #Get ballot id
            cur = mysql.connection.cursor()
            query_string = "SELECT * FROM ballots WHERE idprecincts = %s"%(id)
            cur.execute(query_string)
            results = cur.fetchall()
            ballotId = results[0]["idballots"]
            raceCount = 2
            while (raceCount < len(raceList) + 1):
               #Create the respective string for the column
               raceS = "race" + str(raceCount)
               race = raceList[raceCount-1]
               #This try except block tries to update preexisting columns of race and if it doesnt
               #find one, it creates a new one
               try:
                  cur = mysql.connection.cursor()
                  query_string = "UPDATE ballots SET %s = \"%s\" WHERE idballots = %s"%(raceS, race, ballotId)
                  cur.execute(query_string)
                  mysql.connection.commit()
                  raceCount += 1
               except:
                  cur = mysql.connection.cursor()
                  query_string = "ALTER TABLE ballots ADD COLUMN %s VARCHAR(45)"%(raceS)
                  cur.execute(query_string)
                  mysql.connection.commit()
            flash(f"A Ballot for election %s in precinct %s has been created."%(election, precinctId), category="success")
            return redirect(url_for("newballot"))
      flash(f"Error: A precinct with id %s does not exist."%(precinctId),category="danger")
      return redirect(url_for("newballot"))
   else:
      cur = mysql.connection.cursor()
      query_string="SELECT election_title FROM election"
      cur.execute(query_string)
      results1 = cur.fetchall()
      cur = mysql.connection.cursor()
      query_string="SELECT race_title FROM race"
      cur.execute(query_string)
      results2 = cur.fetchall()
      cur = mysql.connection.cursor()
      query_string="SELECT idprecincts FROM precincts"
      cur.execute(query_string)
      results3 = cur.fetchall()
      return render_template("newballot.html", results = [results1, results2, results3])
      

#rerouting with argument example
@app.route("/admin", methods=["POST", "GET"])
def admin():
   if request.method == "POST":
      zipFiveList = []
      zipFourList = []
      count = 1
      #Build the list of zip 5s and their ranges using try except
      cont = True
      while cont:
         zipFiveS = "zipFive" + str(count)
         zipFourS = "zipFour" + str(count)
         try:
            zipFiveList.append(request.form[zipFiveS])
            zipFourList.append(request.form[zipFourS])
         except:
            cont = False
         count += 1
      location = request.form["location"]
      pollingManager = request.form["pollingManager"]
      officeContact = request.form["officeContact"]
      #Test all of the zip codes and their ranges to make sure they overlap with
      #none of the prexisting ones
      zipCount = 0
      while (zipCount < len(zipFiveList)):
         columnCount = 1
         zipFive = zipFiveList[zipCount]
         zipFourStart = zipFourList[zipCount][0:4]
         zipFourEnd = zipFourList[zipCount][5:9]
         #Need another try except since we do not know how many
         #zip_five and zip_four columns are in the table
         cont = True
         while cont:
            try:
               zipFiveCol = "zip_five" + str(columnCount)
               zipFourCol = "zip_four" + str(columnCount)
               cur = mysql.connection.cursor()
               query_string= "SELECT %s, %s FROM precincts"%(zipFiveCol, zipFourCol)
               cur.execute(query_string)
               results = cur.fetchall()
               #Go through all the zip fives in that column and their associated ranges
               for zipR in results:
                  if zipFive == zipR[zipFiveCol]:
                     zipStart = zipR[zipFourCol][0:4]
                     zipEnd = zipR[zipFourCol][4:8]
                     #Check if there is any overlaps
                     if zipFourStart >= zipStart and zipFourStart <= zipEnd:
                        flash(f"Error: The zip range including zip %s with +4 %s is already registered in a precinct."%(zipFive,zipFourStart), category="danger")
                        return redirect(url_for("admin"))
                     if zipFourEnd >= zipStart and zipFourEnd <= zipEnd:
                        flash(f"Error: The zip range including zip %s with +4 %s is already registered in a precinct."%(zipFive, zipFourEnd),category="danger")
                        return redirect(url_for("admin"))
               columnCount += 1
            except:
               cont = False
         zipCount += 1
      #Insert the base information of the precinct once we have guaranteed it will fit
      #This will automatically leave all extra zip_five and zip_four columns as null to be changed later
      cur = mysql.connection.cursor()
      query_string="INSERT INTO precincts (location,polling_manager,office_contact, zip_five1, zip_four1) VALUES (%s, %s, %s, %s, %s)"
      firstZipFive = zipFiveList[0]
      firstZipFour = zipFourList[0][0:4] + zipFourList[0][5:9]
      cur.execute(query_string, [location, pollingManager, officeContact, firstZipFive, firstZipFour])
      mysql.connection.commit()
      #We want to find the precinct id for easier reference and to let the admin know at the end
      cur = mysql.connection.cursor()
      query_string = "SELECT * FROM precincts WHERE zip_five1 = %s"%(firstZipFive)
      cur.execute(query_string)
      results = cur.fetchall()
      id = results[0]["idprecincts"]
      #Start at 2 because 1 is already in the table
      zipCount = 2
      while (zipCount < len(zipFiveList) + 1):
         #Create the respective string for the column
         zipFiveS = "zip_five" + str(zipCount)
         zipFourS = "zip_four" + str(zipCount)
         zipFive = zipFiveList[zipCount-1]
         zipFour = zipFourList[zipCount-1][0:4] + zipFourList[zipCount-1][5:9]
         #This try except block tries to update preexisting columns of zip_five and zip_four if they exist
         #otherwise it goes into the except block where it creates these columns if they dont
         try:
            cur = mysql.connection.cursor()
            query_string = "UPDATE precincts SET %s = %s WHERE idprecincts = %s"%(zipFiveS, zipFive, id)
            cur.execute(query_string)
            query_string = "UPDATE precincts SET %s = %s WHERE idprecincts = %s"%(zipFourS, zipFour, id)
            cur.execute(query_string)
            mysql.connection.commit()
            zipCount += 1
         except:
            cur = mysql.connection.cursor()
            query_string = "ALTER TABLE precincts ADD COLUMN %s VARCHAR(5)"%(zipFiveS)
            cur.execute(query_string)
            cur = mysql.connection.cursor()
            query_string = "ALTER TABLE precincts ADD COLUMN %s VARCHAR(9)"%(zipFourS)
            cur.execute(query_string)
            mysql.connection.commit()
      flash(f"A new precinct with id %s has been created."%(str(id)),category="success")
      return redirect(url_for("admin"))
   else:
      if "user" in session:
         cur = mysql.connection.cursor()
         query_string="SELECT id FROM users where account_type=%s"
         cur.execute(query_string,["manager"])
         results = cur.fetchall()
         print(results)
         return render_template("admin.html", user=session["user"], results=[results])
      else:
         flash("You are not logged in", category='danger')
         return redirect(url_for("login"))

@app.route("/manager", methods=["POST", "GET"])
def manager():
   if request.method == "POST":
      activate=request.form["activate"]
      ballot = request.form["ballot"]
      time = request.form["date-time"]
      print(activate,ballot,time)
      if(activate == "activate"):
         cur = mysql.connection.cursor()
         query_string = "update ballots set active_time=%s,active=%s where idballots=%s"
         cur.execute(query_string,[time,'true',ballot])
         cur2 = mysql.connection.cursor()
         mysql.connection.commit()
      if(activate == "deactivate"):
         cur = mysql.connection.cursor()
         query_string = "update ballots set deactivate_time=%s where idballots=%s"
         cur.execute(query_string,[time,ballot])
         cur2 = mysql.connection.cursor()
         mysql.connection.commit()
      return redirect(url_for("manager"))
   else: 
      if "user" in session:
         user = session["user"]
         cur = mysql.connection.cursor()
         query_string="SELECT idprecincts FROM precincts where polling_manager=%s"
         cur.execute(query_string,[user])
         results= cur.fetchall()
         precinct_id = results[0]["idprecincts"]
         #precinct_id="1"
         cur2 = mysql.connection.cursor()
         query_string="Select idballots,election,active,active_time,deactivate_time FROM ballots where idprecincts=%s"
         cur2.execute(query_string,[precinct_id])
         results2=cur2.fetchall()
         #I think this should do it?
         return render_template("manager.html", content=results2)
      else:
          return redirect(url_for("login"))




@app.route("/approve-requests")
def approve_deny():
   if request.method == "POST":
      print("testing")
   else: 
      if "user" in session:
         cur = mysql.connection.cursor()
         query_string="SELECT * FROM pending"
         cur.execute(query_string)
         results = cur.fetchall()
         return render_template("approve-requests.html",len = len(results),content = results)
      else:
         flash("You are not logged in", category='danger')
         return redirect(url_for("login"))

@app.route("/decide")
def decide():
   #code to choose whether to redirect to admin or user page
   if "user" in session:
      user=session["user"]
      cur = mysql.connection.cursor()
      query_string="SELECT account_type FROM users WHERE id=%s"
      cur.execute(query_string,[user])
      results = cur.fetchall()
      if results[0]['account_type'] == "admin":
         return redirect(url_for("admin", user=user))
      if results[0]['account_type'] == "manager":
         return redirect(url_for("manager"))
      else:
         return redirect(url_for("user"))

   else:
      flash("You are not logged in", category='danger')
      return redirect(url_for("login"))



@app.route("/addToPrecinct", methods=["POST", "GET"])
def addToPrecinct():
   if request.method == "POST":
      precinct = request.form["precinct"]
      manager = request.form["manager"]
      cur = mysql.connection.cursor()
      query_string="update precincts set polling_manager=%s where idprecincts=%s"
      cur.execute(query_string,[manager,precinct])
      mysql.connection.commit()

      return(redirect(url_for("admin")))
   else:
      if "user" in session: 
         cur = mysql.connection.cursor()
         query_string="SELECT id FROM users where account_type=%s"
         cur.execute(query_string,["manager"])
         managers = cur.fetchall()
         print(managers)

         cur2 = mysql.connection.cursor()
         query_string="SELECT idprecincts FROM precincts"
         cur2.execute(query_string)
         precincts=cur2.fetchall()
         print(precincts)
         return render_template("addToPrecinct.html", managers = managers,precincts = precincts)

if __name__=='__main__':
   app.run()(debug=True)