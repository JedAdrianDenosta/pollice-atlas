import os
import sys
import re
import datetime as dt
from flask import (
    render_template,
    url_for,
    redirect,
    request,
    make_response,
    abort,
    jsonify,
    session,
    flash)
import random
import pymongo
import bcrypt
from pymongo import collection
from app import app, db, user_records, candidates_records, admins_records, posts_records, votes_records, voting_status
from app.helpers import *
from app.forms import *
from app.models import *



model = Models()  # instance of the Model Class

# client = pymongo.MongoClient("mongodb://fynmn:October05@cluster0-shard-00-00.2fb7q.mongodb.net:27017,cluster0-shard-00-01.2fb7q.mongodb.net:27017,cluster0-shard-00-02.2fb7q.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-192j1z-shard-0&authSource=admin&retryWrites=true&w=majority")
#client = pymongo.MongoClient("mongodb+srv://fynmn:October05@cluster0.2fb7q.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


# client = pymongo.MongoClient('localhost', 27017)
# db = client.get_database('election-system-test')


# admins_records = db.admins
# candidates_records = db.candidates
# posts_records = db.posts
# user_records = db.users
# votes_records = db.votes
# voting_status = db.voting_status

user_created = False
voted = False


@app.errorhandler(404)
def resource_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def resource_not_found(e):
    return render_template('404.html'), 403

@app.errorhandler(410)
def resource_not_found(e):
    return render_template('404.html'), 410

@app.errorhandler(500)
def resource_not_found(e):
    return render_template('404.html'), 500

@app.route("/", methods=['post', 'get'])
def landing_page():
    if request.method == "POST":
        return redirect(url_for('create_account'))
    
    else:
        return render_template('landingPage.html')


@app.route("/create_account", methods=['post', 'get'])
def create_account():
    global voted
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    elif request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        course = request.form.get("course")
        section = request.form.get("section")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        domain_allowed = ["wvsu.edu.ph"]
        email_domain = email.split('@')[-1]
        

        user_found = user_records.find_one({"name": user})
        email_found = user_records.find_one({"email": email})
        
        def hasNumbers(inputString):
            return any(char.isdigit() for char in inputString)
    
        if user_found:
            message = 'There already is a user by that name'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2)
        if email_found:
            message = 'This email already exists in database'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2)
        if email_domain not in domain_allowed:
            email_message = 'Only valid wvsu email addresses are allowed to register.'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2, email_message=email_message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2)
        if len(password1) < 6:
            message = 'The length of password should contain at least 6 characters'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2)
        if not any([char.isupper() for char in password1]):
            message = 'The password should contain atleast one uppercase letter'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2)
        if not hasNumbers(password1):
            message = 'The password should contain atleast one number'
            return render_template('userCreateAccount.html', message=message, user=user, email=email, password1=password1, password2=password2)
        
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email,
                'password': hashed, 'course' : course, 'section': section, 'about': "Insert descrption here", 'birthday': "None", 'address': "None", 'voted': False}
            user_records.insert_one(user_input)

            user_data = user_records.find_one({"email": email})
            new_email = user_data['email']
            session["email"] = new_email
            session["section"] = section
            session["name"] = user
            # session["voted"] = False
            username = session["name"].split(" ")
            usn = username[0]

            return redirect(url_for('logged_in'))
            # return render_template('userHome.html', email=new_email, user=usn)
    return render_template('userCreateAccount.html')


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        section = session["section"]
        user = session["name"].split(" ")
        usn = user[0]
        posts = model.getPosts()
        # print(posts)
        return render_template('userHome.html', posts=posts, email=email, section=section, user=usn)
        
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    global voted
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # returns the document of the user
        email_found = user_records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            section_val = email_found['section']
            user_val = email_found['name']
            # print(email_val)
            # print(section_val)
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["section"] = section_val
                session["name"] = user_val
                # session["voted"] = False
                # print(voted)

                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('userLogin.html', message=message, email=email)
        else:
            message = 'Email not found'
            return render_template('userLogin.html', message=message)
    return render_template('userLogin.html', message=message)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.clear()

        return redirect(url_for('login'))
    else:
        return redirect(url_for('create_account'))


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if "admin_username" in session:
        return redirect(url_for("admin_panel"))

    else:
        return redirect(url_for("admin_login"))


@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    message = ''

    if request.method == "POST":
        username = request.form.get("admin_username")
        password = request.form.get("admin_password")

        username_found = admins_records.find_one({"username": username})
        session["admin_username"] = username
        admin_username = session["admin_username"]

        if username_found:
            username_val = username_found['username']
            passwordcheck = username_found['password']

            if passwordcheck:
                session["admin_username"] = username

                return redirect(url_for('admin_panel'))
            else:
                    # if "admin_username" in session:
                    #     return redirect(url_for("admin_panel"))
                message = 'Wrong password'
                return render_template('adminLogin.html', message=message, admin_username=admin_username)
        else:
            message = 'Username not found'
            return render_template('adminLogin.html', message=message, admin_username=admin_username)
    else:
        return render_template('adminLogin.html', message=message)


@app.route("/admin_panel", methods=["POST", "GET"])
def admin_panel():
    if "admin_username" in session:
        return redirect(url_for("addCandidate"))
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin_logout", methods=["POST", "GET"])
def admin_logout():
    if "admin_username" in session:
        session.clear()

        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('admin_login'))


@app.route("/admin/view", methods=["POST", "GET"])
def viewCandidate():
    if "admin_username" in session:
        admin_username = session["admin_username"].title()
        from bson.json_util import dumps, loads
        result = list(model.pullListOfCandidates())
        # print(result)

        party1 = []
        party2 = []
        party3 = []

        for i in result:
            if i.get("party") == "party1":
                candidate = {k: i[k] for k in i.keys() - {'party'} - {'_id'}}
                party1.append(candidate)
            elif i.get("party") == "party2":
                candidate = {k: i[k] for k in i.keys() - {'party'} - {'_id'}}
                party2.append(candidate)
            elif i.get("party") == "party3":
                candidate = {k: i[k] for k in i.keys() - {'party'} - {'_id'}}
                party3.append(candidate)

        party1_list = []
        party2_list = []
        party3_list = []


        for i in range(len(party1)):
            party1Item = [[party1[i]["id"]], [party1[i]["name"].upper()],
            [" ".join(party1[i]["position"].split("_")).upper()]]
            party1_list.append((party1Item))

        for i in range(len(party2)):
            party2Item = [[party2[i]["id"]], [party2[i]["name"].upper()],
                [" ".join(party2[i]["position"].split("_")).upper()]]
            party2_list.append(party2Item)

        for i in range(len(party3)):
            party3Item = [[party3[i]["id"]], [party3[i]["name"].upper()],
                [" ".join(party3[i]["position"].split("_")).upper()]]
            party3_list.append(party3Item)

        # print(party1_list)
        # print(party2_list)
        # print(party3_list)
        # return render_template("admin_viewCan.html")

        return render_template("adminView.html", admin_username=admin_username, party1=party1_list, party2=party2_list, party3=party3_list)
    
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/add", methods=["POST", "GET"])
def addCandidate():
    if "admin_username" in session:
        admin_username = session["admin_username"].title()
        # model.getPosts()

        #get specific voting enabled status in mongodb
        #if true then check is = checked
        #if false then check is empty
        status = voting_status.find_one({"voting_status_id": "0001"})

        if status['voting_enabled'] == 'true':
            check = 'checked'
        
        else:
            check = ''

        if request.method == "POST":
            if request.form.get("toggle_submit") == "Submit Status":
                voting_enabled = request.form.get("toggle_switch")
                # print("vt: ", voting_enabled)

                if voting_enabled:
                    check = 'checked'

                    updateRecordQuery = {"voting_status_id": "0001"}
                    newvalues = {"$set": {"voting_enabled": voting_enabled}}
                    voting_status.update_one(updateRecordQuery, newvalues)

                    print(voting_enabled)

                
                else:
                    check = ''

                    updateRecordQuery = {"voting_status_id": "0001"}
                    newvalues = {"$set": {"voting_enabled": "false"}}
                    voting_status.update_one(updateRecordQuery, newvalues)
                
                return render_template("adminAdd.html", check=check, admin_username=admin_username)
                
            

            elif request.form.get("submit_btn") == "Add Candidate":
                candidate_name = request.form.get("candidate_name")
                candidate_position = request.form.get("candidate_position")
                candidate_party = request.form.get("candidate_party")
                candidate_course = request.form.get("candidate_course")
                candidate_year = request.form.get("candidate_year")

                session['candidate_name'] = candidate_name
                session['candidate_position'] = candidate_position
                session['candidate_party'] = candidate_party

                can_name = session['candidate_name']
                can_pos = session['candidate_position'].split("_")
                can_party = session['candidate_party'].title()
                can_position = " ".join(can_pos).title()


                last_record = candidates_records.find().sort([('_id', -1)]).limit(1)
                id_num = int(last_record[0]['id']) + 1
                # id = "00"+str(id_num)
                id = str(id_num)

                admin_add = {"id": id, 'party': candidate_party, 'course': candidate_course,
                    'year': candidate_year, "position": candidate_position, "name": candidate_name}
                candidates_records.insert_one(admin_add)

                # print(candidate_name, candidate_position, candidate_party, candidate_course, candidate_year)

                return render_template("adminAdd.html", admin_username=admin_username, can_name=can_name, can_party=can_party, can_position=can_position)

            # triggeres when post is clicked
            elif request.form.get("submit_post_btn") == "Submit Post":
                if posts_records.find_one({'post_id': '0001'}):
                    last_record = posts_records.find().sort([('_id', -1)]).limit(1)
                    id_num = int(last_record[0]['post_id']) + 1
                    if id_num < 10:
                        post_id = "000"+str(id_num)
                    else:
                        post_id = "00"+str(id_num)
                    post_details = request.form.get("new_post") # gets the text from the textarea named new_post
                    post_name = request.form.get("post_name")
                    # make code that adds these details to a new document in mongodb, post_id(make one), post_name(make one or require one) and the text for the post itself
                    post_add = {"post_id": post_id, "post_name": post_name, "post_details": post_details}
                    posts_records.insert_one(post_add)

                    return render_template("adminAdd.html", admin_username=admin_username, check=check)
                
                else:
                    post_details = request.form.get("new_post") # gets the text from the textarea named new_post
                    post_name = request.form.get("post_name")
                    # make code that adds these details to a new document in mongodb, post_id(make one), post_name(make one or require one) and the text for the post itself
                    post_add = {"post_id": "0001", "post_name": post_name, "post_details": post_details}
                    posts_records.insert_one(post_add)
                    return render_template("adminAdd.html", admin_username=admin_username, check=check)

                # return redirect(url_for("admin/add"))
        
        return render_template("adminAdd.html", admin_username=admin_username, check=check)

        
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/update", methods=["POST", "GET"])
def updateCandidate():
    if "admin_username" in session:
        admin_username = session['admin_username'].title()
        if request.method == "POST":
            candidate_id = request.form.get("candidate_id")
            candidate_name = request.form.get("candidate_name")
            candidate_position = request.form.get("candidate_position")
            candidate_party = request.form.get("candidate_party")
            candidate_course = request.form.get("candidate_course")
            candidate_year = request.form.get("candidate_year")


            updateRecordQuery = {"id": candidate_id}
            newvalues = {"$set": {"id": candidate_id, 'party': candidate_party, 'course': candidate_course,
                'year': candidate_year, "position": candidate_position, "name": candidate_name}}
            candidates_records.update_one(updateRecordQuery, newvalues)
            return render_template("adminUpdate.html", admin_username=admin_username, can_name=candidate_name.title(), can_position=candidate_position.title(), can_party=candidate_party.title())

        return render_template("adminUpdate.html", admin_username=admin_username)
    
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/delete", methods=["POST", "GET"])
def deleteCandidate():
    if "admin_username" in session:
        admin_username = session['admin_username'].title()
        if request.method == "POST":
            candidate_id = request.form.get("candidate_id")

            deleteRecordQuery = {"id": candidate_id}
            candidates_records.find_one_and_delete(deleteRecordQuery)

            return render_template("adminDelete.html", admin_username=admin_username, delete_candidate=candidate_id)
        return render_template("adminDelete.html",admin_username=admin_username)
    
    else:
        return redirect(url_for("admin_login"))




@app.route("/vote", methods=["POST", "GET"])
def vote():
    global voted
    if "email" in session:
        user = session["name"]
        the_user = session["name"].split(" ")
        usn = the_user[0]
        votes = model.getVotes()
        positions = model.getPositions()
        # print(votes)
        # print(positions)

        if request.method == "GET":
            status = voting_status.find_one({"voting_status_id": "0001"})
            if status['voting_enabled'] == 'true':
            
                if model.getVoted(str(user)):
                    voted = True

                else:
                    voted = False
            
            else:
                voted = True
            
            

        
        
        # listOfCandidates = model.pullCandidates()
        # print(listOfCandidates)
        # chairperson = []
        # vice_chairperson = []
        # secretary = []
        # assistant_secretary = []
        # treasurer = []
        # assistant_treasurer = []
        # auditor = []
        # assistant_auditor = []
        # business_manager = []
        # assistant_business_manager = []
        # pio = []
        # assistant_pio = []
        # representative1 = []
        # representative2 = []

        # x = True
        # while x:
        #     for num, i in enumerate(listOfCandidates):
        #         if i[1] == "chairperson":
        #             chairperson.append(i[0])
        #         elif i[1] == "vice_chairperson":
        #             vice_chairperson.append(i[0])
        #         elif i[1] == "secretary":
        #             secretary.append(i[0])
        #         elif i[1] == "assistant_secretary":
        #             assistant_secretary.append(i[0])
        #         elif i[1] == "treasurer":
        #             treasurer.append(i[0])
        #         elif i[1] == "assistant_treasurer":
        #             assistant_treasurer.append(i[0])
        #         elif i[1] == "auditor":
        #             auditor.append(i[0])
        #         elif i[1] == "assistant_auditor":
        #             assistant_auditor.append(i[0])
        #         elif i[1] == "business_manager":
        #             business_manager.append(i[0])
        #         elif i[1] == "assistant_business_manager":
        #             assistant_business_manager.append(i[0])
        #         elif i[1] == "pio":
        #             pio.append(i[0])
        #         elif i[1] == "assistant_pio":
        #             assistant_pio.append(i[0])
        #         elif i[1] == "representative1":
        #             representative1.append(i[0])
        #         elif i[1] == "representative2":
        #             representative2.append(i[0])
        #     x = False


        if request.method == "POST":
            if "okay_btn" in request.form:

                # v = request.form["position"]
                # print(v)
                chairperson_vote = request.form.get("Chairperson")
                vice_chairperson_vote = request.form.get("Vice Chairperson")
                secretary_vote = request.form.get("Secretary")
                assistant_secretary_vote = request.form.get("Assistant Secretary")
                treasurer_vote = request.form.get("Treasurer")
                assistant_treasurer_vote = request.form.get("Assistant Treasurer")
                auditor_vote = request.form.get("Auditor")
                assistant_auditor_vote = request.form.get("Assistant Auditor")
                business_manager_vote = request.form.get("Business Manager")
                assistant_business_manager_vote = request.form.get("Assistant Business Manager")
                pio_vote = request.form.get("P.I.O.")
                assistant_pio_vote = request.form.get("Assistant P.I.O.")
                representative1_vote = request.form.get("Representative 1")
                representative2_vote = request.form.get("Representative 2")

                # print("chairperson: ", chairperson_vote, "vice_chairperson: ", vice_chairperson_vote, "secretary: ", secretary_vote, "assistant_secretary: ", assistant_secretary_vote, "treasurer: ", treasurer_vote, "assistant_treasurer: ", assistant_treasurer_vote, "auditor: ",
                        #   auditor_vote, "assistant_auditor: ", assistant_auditor_vote, "business_manager: ", business_manager_vote, "assistant_business_manager: ", assistant_business_manager_vote, "pio_vote: ", pio_vote, "assistant_pio_vote", assistant_pio_vote,  "representative1: ", representative1_vote, "representative2: ", representative2_vote)

                candidate_id = model.getIDbyName(str(user))
                updateRecordQuery = {"_id": candidate_id}
                newvalues = {"$set": {"voted": True}}
                user_records.update_one(updateRecordQuery, newvalues)

                votes_add = {"name": str(user), "chairperson": chairperson_vote, "vice_chairperson" : vice_chairperson_vote, "secretary" : secretary_vote, "assistant_secretary" : assistant_secretary_vote, "treasurer" : treasurer_vote, "assistant_treasurer" : assistant_treasurer_vote, "auditor":
                          auditor_vote, "assistant_auditor" : assistant_auditor_vote, "business_manager" : business_manager_vote, "assistant_business_manager" : assistant_business_manager_vote, "pio" : pio_vote, "assistant_pio" : assistant_pio_vote, "representative1" : representative1_vote, "representative2" :representative2_vote}
                    
                votes_records.insert_one(votes_add)

                if model.getVoted(str(user)):
                    voted = True
                    # print("true")
                else:
                    voted = False
                    # print('false')
                    
                return redirect(url_for('results'))
                    

        return render_template('userVote.html', votes=votes, positions=positions, user=usn, voted=voted)
    else:
        return redirect(url_for("login"))


@app.route("/results", methods=["POST", "GET"])
def results():
    if "email" in session:
        user = session["name"].split(" ")
        usn = user[0]
        
        votes = model.getVotes()
        positions = model.getPositions()

        return render_template("userResults.html", votes=votes, positions=positions, user=usn)
    
    else:
        return redirect(url_for("login"))




@app.route("/about", methods=["POST", "GET"])
def about():
    user = session["name"].split(" ")
    usn = user[0]
    return render_template("userAbout.html", user=usn)



@app.route("/admin_profile", methods=["POST", "GET"])
def admin_profile():

    if "admin_username" in session:
        admin_username = session['admin_username'].title()
        return render_template('adminProfile.html', admin_username=admin_username)
    else:
        return redirect(url_for('admin_login'))


@app.route("/user_profile", methods=["POST", "GET"])
def user_profile():
    email = session["email"]
    email_found = user_records.find_one({"email":email})
    user = session["name"]
    username = session["name"].split(" ")
    usn = username[0]
    
    if email_found:
        user_val = email_found['name']
        email_val = email_found['email']
        section_val = email_found['section']
        course_val = email_found['course']
        birthday_val = email_found['birthday']
        address_val = email_found['address']
        about_val = email_found['about']
        year = 0
    
    if section_val == "1A" or section_val == "1B":
        year = 1
    elif section_val == "2A" or section_val == "2B":
        year = 2
    elif section_val == "3A" or section_val == "3B":
        year = 3
    elif section_val == "4A" or section_val == "4B":
        year = 4
    else:
        year = 0

    if year == 1:
        section = "1st year"
    elif year == 2:
        section = "2nd year"
    elif year == 3:
        section = "3rd year"
    elif year == 4:
        section = "4th year"
    else:
        section = "None"


    return render_template('userProfile.html', name=user_val, email=email_val, school_year=section, course=course_val, birthday=birthday_val, address=address_val, about=about_val, user=usn, username=user)

@app.route("/edit_profile", methods=["POST", "GET", "PUT"])
def edit_profile():
    if "email" in session:
        email = session["email"]
        user = session["name"]
        username = session["name"].split(" ")
        usn = username[0]
        
        if request.method == "POST":
            if "update_btn" in request.form:
                IdQuery = {"email": email}
                about = request.form.get("about")
                address = request.form.get("address")
                birthday = request.form.get("birthday")
                new_vals = {"$set": {"about": about, "address" : address, "birthday" : birthday}}
                user_records.update_one(IdQuery, new_vals)

            return redirect(url_for('user_profile', user=usn))
    
        return render_template("userEditProfile.html", user=usn)
    else:
        return redirect(url_for("/login"))
