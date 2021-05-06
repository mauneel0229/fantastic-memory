from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
#from . import db
from flask_login import login_user, login_required, logout_user, current_user
import mysql.connector
from mysql.connector.constants import ClientFlag
import webbrowser
import time
from .views import home
from . import views
from datetime import date

'''
config = {
    'user': 'root',
    'password': 'Bew810808!',
    'host': '130.211.122.222',
    'client_flags': [ClientFlag.SSL],
}
config['database'] = 'CS348Project'
'''


config = {
    'user': 'root',
    'password': 'mauneel02',
    'host': '34.67.42.223',
    'client_flags': [ClientFlag.SSL],
}
config['database'] = 'db1'

# now we establish our connection
cnxn = mysql.connector.connect(**config)
cursor = cnxn.cursor()
setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"

cursor.execute(setIso)


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    session['temp1'] = "workout name"
    session['temp2'] = "no workout plan created"
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #userCheckQuery = "SELECT email, password, first_name FROM `user_info` WHERE `email` = " + "'" + email + "'" + ";"
        setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
        cursor.execute(setIso)
        stTranx = "START TRANSACTION;"
        cursor.execute(stTranx)
        cursor.callproc('GetUserInfo', [str(email), ])
        cnxn.commit()            
                
        templist = []

        for result in cursor.stored_results():

            templist.append(result.fetchall())


        tp = templist[0][0]

        userList = {}
        fname = ""

        userList[tp[0]] = tp[1]
        fname = tp[2]

        #user = User.query.filter_by(email=email).first()
        if len(userList.keys()) != 0:
            if check_password_hash(userList[email], password):
                flash('Logged in successfully!', category='success')
                #login_user(userObj, remember=True)
                session['email'] = email
                session['name'] = fname

                #checkUserStats = "SELECT * FROM `user_stats` WHERE `email` = " + "'" + email + "'" + ";"

                setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
                cursor.execute(setIso)
                stTranx = "START TRANSACTION;"
                cursor.execute(stTranx) 
                cursor.callproc('GetUserStat', [str(email), ])
                cnxn.commit()  
                templist = []

                for result in cursor.stored_results():

                    templist.append(result.fetchall())

                tp = templist[0][0]


                session['age'] = tp[1]
                session['height'] = tp[2]
                session['weight'] = tp[3]
                
                return render_template("profile.html", user=current_user, Profile = [session['name'], session['email']])
                
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')


    session.clear()
    return render_template("login.html", user=current_user)

@auth.route('/stats', methods=['GET', 'POST'])
def stats():
    if request.method == 'POST':
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')  
        email = session['email']

        setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
        cursor.execute(setIso)
        stTranx = "START TRANSACTION;"
        cursor.execute(stTranx)
        insertQuery = "INSERT INTO `user_stats` (`email` ,`age`, `height`, `weight`)VALUES(" + "'" + email + "'"+ "," + age + "," + height+ "," + weight +");"
        cursor.execute(insertQuery)

        cnxn.commit()
        session['height'] = height
        session['weight'] = weight
        session['age'] = age

        return render_template("profile.html", user=current_user, Profile = [session['name'], session['email']])


    return render_template("stats.html", user=current_user, Profile = [session['name'], session['email']])

@auth.route('/profile', methods=['GET', 'POST'])
def profile():
    setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
    cursor.execute(setIso)
    stTranx = "START TRANSACTION;"
    cursor.execute(stTranx)
    statQuery = "SELECT * FROM `user_stats` WHERE `email` = " + "'" + session['email'] + "'" + ";"
    cursor.execute(statQuery)
    statQueryOut = cursor.fetchall()
    cnxn.commit()

    

    array = [session['name'], session['email'], statQueryOut[0][1], statQueryOut[0][2], statQueryOut[0][3]]

    return render_template("profile.html", user=current_user, Profile = array)

@auth.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
    cursor.execute(setIso)
    stTranx = "START TRANSACTION;"
    cursor.execute(stTranx)
    statQuery = "SELECT * FROM `user_stats` WHERE `email` = " + "'" + session['email'] + "'" + ";"
    cursor.execute(statQuery)
    statQueryOut = cursor.fetchall()
    cnxn.commit()

    if request.method == 'POST':
        #print(request.form)
        select = request.form["WL"]
        #flash( select, category='success')

        workout_list = []

        #CheckQuery = "SELECT `workout_name` FROM `workouts` WHERE `email` = " + "'" + session['email'] + "'" + ";"
        email = session['email']

        setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
        cursor.execute(setIso)
        stTranx = "START TRANSACTION;"
        cursor.execute(stTranx)
        cursor.callproc('GetWorkoutName', [str(email), ])
        cnxn.commit()
                
        templist = []

        for result in cursor.stored_results():

            templist.append(result.fetchall())


        tp = list(set(templist[0]))

        newWorkoutList = []
        for i in tp:
            newWorkoutList.append(i[0])
        

        workout_list = newWorkoutList
        #flash( newWorkoutList, category='success')

        CheckQuery = "SELECT `exercise_id` FROM `workouts` WHERE `email` = " + "'" + session['email'] + "'" + " and `workout_name` = "+"'"+select+"';"

        setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
        cursor.execute(setIso)
        stTranx = "START TRANSACTION;"
        cursor.execute(stTranx)

        cursor.execute(CheckQuery)
        QueryOut = cursor.fetchall()
        exlist = []
        for row in QueryOut:
            exlist.append(row[0])
        #flash( exlist, category='success')

        exNameList = []

        for i in exlist:
            setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
            cursor.execute(setIso)
            stTranx = "START TRANSACTION;"
            cursor.execute(stTranx)      

            CheckQuery = "SELECT `name` FROM `all_exercises` WHERE `id` = " + "'" + str(i) + "'" + ";"
            cursor.execute(CheckQuery)
            QueryOut = cursor.fetchall()
            for row in QueryOut:
                exNameList.append(row[0])
        ##flash( exNameList, category='success')    



        session['workout_list'] = list(set(workout_list))
        array = [session['name'], session['email']]
        array = [session['name'], session['email'], statQueryOut[0][1], statQueryOut[0][2], statQueryOut[0][3]]



        setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
        cursor.execute(setIso)
        stTranx = "START TRANSACTION;"
        cursor.execute(stTranx)   

        CheckQuery = "select count(*) from `workouts` group by `email`, `workout_name` having email = "+"'"+ str(session['email'])+ "'" + "and `workout_name` = " + "'" +select +"';"
        cursor.execute(CheckQuery)
        QueryOut = cursor.fetchall()
        randomlist = []
        for row in QueryOut:
            randomlist.append(row[0])
        session['exeCount'] = randomlist[0]
        session['expTime'] = randomlist[0] * 15

        session['exNameList'] = exNameList

        return redirect(url_for('auth.dashboard')) #render_template("select_exercises.html", user=current_user, Profile = array)

    
    #array = [session['name'], session['email']]
    #return render_template("user_home.html", user=current_user, Profile = array)
    
    workout_list = []
    setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
    cursor.execute(setIso)
    stTranx = "START TRANSACTION;"
    cursor.execute(stTranx)

    CheckQuery = "SELECT `workout_name` FROM `workouts` WHERE `email` = " + "'" + session['email'] + "'" + ";"
    cursor.execute(CheckQuery)
    QueryOut = cursor.fetchall()
    for row in QueryOut:
        workout_list.append(row[0])



    session['workout_list'] = list(set(workout_list))
    array = [session['name'], session['email']]
    array = [session['name'], session['email'], statQueryOut[0][1], statQueryOut[0][2], statQueryOut[0][3]]

    return render_template("dashboard.html", user=current_user, Profile = array)

@auth.route('/logout')
@login_required
def logout():

    session['email'] = ""
    session.clear()
    logout_user()
    return render_template("login.html", user=current_user)

@auth.route('/select_exercises', methods=['GET', 'POST'])
def select_exercises():
    if request.method == 'POST':
        W_name = request.form.get('W_name')
        W_type = request.form["W_type"]
        W_in = request.form["W_in"]
        exes = request.form.getlist('exercises')

        #flash( W_name , category='success')
        #flash( W_type , category='success')
        #flash(W_in , category='success')
        #flash(exes , category='success') 
        array = [session['name'], session['email']] 
        session['temp1'] = W_name
        session['temp2'] = exes

        today = date.today()
        todayFormat = today.strftime("%Y/%m/%d")

        stTranx = "START TRANSACTION;"
        

        for i in exes:
            setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
            cursor.execute(setIso)
            stTranx = "START TRANSACTION;"
            cursor.execute(stTranx)

            exerciseIdQuery = "SELECT `id` from `all_exercises` where `name` =" + "'"+i +"'"
            cursor.execute(exerciseIdQuery)
            exerciseIdQueryOut = cursor.fetchall()[0][0]

            cursor.execute(stTranx)
            insertQuery = "INSERT INTO `workouts` (`workout_name` ,`email`, `date`, `exercise_id`, `intensity_id`,`workout_category`)  VALUES(" + "'" + W_name + "'," + "'" + session['email'] + "',"  + "'" + todayFormat + "',"  + str(exerciseIdQueryOut) + "," + str(2) + "," + "'" + str(1) + "'" + ");"
            cursor.execute(insertQuery)
            cnxn.commit()

        return render_template("profile.html", user=current_user, Profile = array)
        
    array = [session['name'], session['email']]
    return render_template("select_exercises.html", user=current_user, Profile = array)


@auth.route('/user_home', methods=['GET', 'POST'])
def user_home():
    if request.method == 'POST':
        selected_muscles = []
        selected_muscles.append(request.form.getlist('back')) 
        selected_muscles.append(request.form.getlist('glute'))
        selected_muscles.append( request.form.getlist('calves') )
        selected_muscles.append(request.form.getlist('quadriceps')) 
        selected_muscles.append( request.form.getlist('hamstrings')) 
        selected_muscles.append( request.form.getlist('lats') )
        selected_muscles.append(request.form.getlist('trapezius')) 
        selected_muscles.append(request.form.getlist('abdominal') )
        selected_muscles.append(request.form.getlist('pectoral') )
        selected_muscles.append(request.form.getlist('deltoid') )
        selected_muscles.append(request.form.getlist('triceps') )
        selected_muscles.append(request.form.getlist('biceps') )
        selected_muscles.append(request.form.getlist('forearm') )

        check_list = []
        for sublist in selected_muscles:
            for item in sublist:
                check_list.append(item)
        if len(check_list) == 0:
            flash('Please select an option.', category='error')   

        else:
            exercises_list = []
            for mus in selected_muscles:
                if len(mus) > 0:
                    setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
                    cursor.execute(setIso)
                    stTranx = "START TRANSACTION;"
                    cursor.execute(stTranx)

                    CheckQuery = "select exe from (select a.name as exe, b.name as bd from `effects` e join `all_exercises` a on e.ex_id = a.id join `body_parts` b on b.id = e.bd_part_id) x where bd = " + "'" + mus[0] +"';"
                    cursor.execute(CheckQuery)
                    QueryOut = cursor.fetchall()
                    for row in QueryOut:
                        exercises_list.append(row[0])
            session['exe'] = list(set(exercises_list))
            array = [session['name'], session['email']]
            return redirect(url_for('auth.select_exercises')) #render_template("select_exercises.html", user=current_user, Profile = array)

            
    
    array = [session['name'], session['email']]
    return render_template("user_home.html", user=current_user, Profile = array)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    session['temp1'] = "workout name"
    session['temp2'] = "no workout plan created"
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
        cursor.execute(setIso)
        stTranx = "START TRANSACTION;"
        cursor.execute(stTranx)

        userCheckQuery = "SELECT * FROM `user_info` WHERE `email` = " + "'" + email + "'" + ";"
        cursor.execute(userCheckQuery)
        userCheckQueryOut = cursor.fetchall()
        userList = []
        for row in userCheckQueryOut:
            userList.append(row)
        
        if len(userList) != 0:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            hashedPassword = generate_password_hash(password1, method='sha256')
            #new_user = User(email=email, first_name=first_name, password=hashedPassword)
            #insertQuery = "INSERT INTO `user_info` (`email` ,`password`, `first_name`)VALUES(" + "'" + email + "'"+ "," + "'"+ hashedPassword + "'"+ "," + "'"+ first_name+ "'"+ ");"
            #cursor.execute(insertQuery)
            setIso = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
            cursor.execute(setIso)
            stTranx = "START TRANSACTION;"
            cursor.execute(stTranx)
            
            cursor.callproc('InsertUserInfo', [str(email), str(hashedPassword), str(first_name)])
            cnxn.commit()

            #login_user(new_user, remember=True)
            session['email'] = email
            flash(session['email'])
            session['name'] = first_name

            flash('Account created!', category='success')
            return redirect(url_for('auth.stats'))

            '''new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
            '''

    return render_template("sign_up.html", user=current_user)
