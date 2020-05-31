from flask import Flask, render_template, url_for, flash,session
from flask import request, redirect
import os
from datetime import datetime, timedelta, date
import json
import csv
from flask_pymongo import PyMongo
import algo
from bson import Binary, Code
from bson.json_util import dumps
import random

#------------------------------------Algorithm Funcitons Begins

	#Increasing
def increasing_curve(number_of_weeks, number_of_topics):
	print(increasing_curve)
	increasing_distribution = algo.getDistribution(weeks=number_of_weeks, topics=number_of_topics)
	increasing_distribution.reverse()
	return increasing_distribution

#Increasing
def decreasing_curve(number_of_weeks, number_of_topics):
	print("decreasing_curve")
	decreasing_distribution = algo.getDistribution(weeks=number_of_weeks, topics=number_of_topics)
	return decreasing_distribution

def nonlinear_curve(number_of_weeks, number_of_topics):
	print("nonlinear_curve")
	time_half1 = int(number_of_weeks / 2)	#apply increasing
	topics_half1 = int(number_of_topics/2)
	time_half2 = number_of_weeks - time_half1		#apply decreasing
	topics_half2 =  number_of_topics - topics_half1
	distribution_half1 = increasing_curve(time_half1,topics_half1)
	distribution_half2 = decreasing_curve(time_half2,topics_half2)
	(distribution_half1).extend(distribution_half2)
	nonlinear_distribution = distribution_half1
	return nonlinear_distribution

def linear_curve(number_of_weeks, number_of_topics):
	topics_half1 = int(number_of_topics/2)
	topics_half2 =  number_of_topics - topics_half1

	a = increasing_curve(number_of_weeks, topics_half1)
	b = decreasing_curve(number_of_weeks, topics_half2)
	
	return [a[i]+b[i] for i in range(len(a))]

#------------------------------------Algorithm Funcitons Ends

#..................................Global Funcitons

month_list = ['january', 'febuary', 'march', 'april', 'may', 'june', 'july','august','september','october','novermber','december']

def pretty(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def getStreak(email):
	data = mongo.db.cred.find_one({'email' : email})
	print(data['streak'])
	currentStreak = data['streak'][0]
	start_date = date(int(data['streak'][0]['start_date'][0]), int(data['streak'][0]['start_date'][1]), int(data['streak'][0]['start_date'][2]))
	last_date = date(int(data['streak'][0]['last_date'][0]), int(data['streak'][0]['last_date'][1]), int(data['streak'][0]['last_date'][2]))
	today_date = date.today()
	print('Start Date: ', start_date)
	print('last_date: ', last_date)
	print('today: ', today_date)
	if (today_date - last_date).days > 1:
		currentStreak['start_date'] = [today_date.year,today_date.month,today_date.day]
		currentStreak['last_date'] = [today_date.year,today_date.month,today_date.day]
		print('Current Streak: ', currentStreak)
		mongo.db.cred.update_one({'email':email},{'$set':{'streak':[currentStreak]}})
		return 0
	else:
		currentStreak['last_date'] = [today_date.year,today_date.month,today_date.day]
		mongo.db.cred.update_one({'email':email},{'$set':{'streak':[currentStreak]}})
		return (today_date -  start_date).days
	


#algo.getDistribution(weeks=x,topics=y)
#this function is use to distriubte the topics accross a week
#returns the list of all the topics for a particular exam
def allTopicList(exam):
	
	all_topics = {}
	data =  mongo.db.syllabus.find_one({'exam': exam})
	for key in data[exam]:
		topics = data[exam][key]
		for topic in topics:
			all_topics[topic[0]] = topic[1:5]
	return all_topics


#returns the codes for all the topics for a particular exam
def allTopicCode(exam):
	all_topics = [] 
	data = mongo.db.syllabus.find_one({'exam': exam})
	for key in data[exam]:
		subject_topics = data[exam][key]
		for topic in subject_topics:
			all_topics.append(topic[0])
	return all_topics

#sort a given list of topic codes according to it's difficulty
def sortTopics(topics):
	hard = []
	med = []
	easy = []
	for topic_code in topics:
		if topic_code[-1] == 'h':
			hard.append([topic_code,'P'])
		elif topic_code[-1] == 'm':
			med.append([topic_code,'P'])
		else:
			easy.append([topic_code,'P'])
	return [hard,med,easy]

def getPlan(target_year,curve,topic_list,revision):
	today = date.today()
	target_year = int(target_year)
	current_year = today.year
	current_month = today.month
	current_week = 0
	month_left = 12*( target_year - current_year - 1) + (12 - current_month)
	print("Today's year:", today.year)
	print("today's month: ", today.month)
	print("year left(exculding current_year): ", target_year - current_year - 1)
	print("month left(exculding current_month): ", month_left)

	if today.day >= 1 and today.day <7 :
		current_week = 1
	elif today.day >= 7 and today.day <14:
		current_week = 2
	elif today.day >= 14 and today.day <21:
		current_week = 3
	else:
		current_week = 4

	#"gets the total time left or the number of weeks for it"
	total_weeks =  (4 - current_week + 1 ) + (month_left)*4

	print("total_weeks: ",total_weeks)
	sorted_topics = sortTopics(topic_list)
	#print(sorted_topics)

	#the list it self
	hard_topics_list = (revision+1)*sorted_topics[0]
	med_topics_list = (revision+1)*sorted_topics[1]
	easy_topics_list = (revision+1)*sorted_topics[2]
	
	#the distribution across week
	#the function has to be made dynamic

	if  curve == 'linear':
		hard_distribution = linear_curve(total_weeks, (revision+1)*len(sorted_topics[0]))
		medium_distribution = linear_curve(total_weeks, (revision+1)*len(sorted_topics[1]))
		easy_distribution = linear_curve(total_weeks, (revision+1)*len(sorted_topics[2]))
	elif curve == 'increasing':
		hard_distribution = increasing_curve(total_weeks, (revision+1)*len(sorted_topics[0]))
		medium_distribution = increasing_curve(total_weeks, (revision+1)*len(sorted_topics[1]))
		easy_distribution = increasing_curve(total_weeks, (revision+1)*len(sorted_topics[2]))
	elif curve == 'decreasing':
		hard_distribution = decreasing_curve(total_weeks, (revision+1)*len(sorted_topics[0]))
		medium_distribution = decreasing_curve(total_weeks, (revision+1)*len(sorted_topics[1]))
		easy_distribution = decreasing_curve(total_weeks, (revision+1)*len(sorted_topics[2]))
	else:
		hard_distribution = nonlinear_curve(total_weeks, (revision+1)*len(sorted_topics[0]))
		medium_distribution = nonlinear_curve(total_weeks, (revision+1)*len(sorted_topics[1]))
		easy_distribution = nonlinear_curve(total_weeks, (revision+1)*len(sorted_topics[2]))



	print('hard: ',hard_distribution)
	print('med: ',medium_distribution)
	print('easy: ',easy_distribution)


	week_count = 0		#in the end, week count has to match the total number of weeks
	slice_beg = [0,0,0]
	slice_end = [hard_distribution[0],medium_distribution[0],easy_distribution[0]]

	plan_current_month = (month_list[current_month - 1]+'_'+str(current_year))

	plan = { plan_current_month : {}}

	for x in range(current_week,5):
		plan[plan_current_month]['week'+str(x)] = []
		plan[plan_current_month]['week'+str(x)].append(hard_topics_list[slice_beg[0]:slice_end[0]])	#hard
		plan[plan_current_month]['week'+str(x)].append(med_topics_list[slice_beg[1]:slice_end[1]])	#med
		plan[plan_current_month]['week'+str(x)].append(easy_topics_list[slice_beg[2]:slice_end[2]])	#easy
		slice_beg[0] = slice_end[0]
		slice_beg[1] = slice_end[1]
		slice_beg[2] = slice_end[2]
		slice_end[0] += hard_distribution[week_count]
		slice_end[1] += medium_distribution[week_count]
		slice_end[2] += easy_distribution[week_count]
		week_count +=1
	#current month is already filled as it may not have all four weeks

	year = current_year
	times = 0
	for x in range(current_month+1,month_left + current_month + 1):
		if(x%13 == 0 ):
			year +=1
		if(x>12 and x<=24):
			plan_month = month_list[x - 12 -1]+'_'+str(year)
		elif (x>24 and x<=36):
			plan_month = month_list[x - 24 -1]+'_'+str(year)
		elif (x>48 and x<=60):
			plan_month = month_list[x - 48 -1]+'_'+str(year)
		else:
			plan_month = month_list[x -1]+'_'+str(year)
		print(plan_month)
		plan[plan_month] = {}
		for x in range(1,5):
			plan[plan_month]['week'+str(x)] = []
			plan[plan_month]['week'+str(x)].append(hard_topics_list[slice_beg[0]:slice_end[0]])	#hard
			plan[plan_month]['week'+str(x)].append(med_topics_list[slice_beg[1]:slice_end[1]])	#med
			plan[plan_month]['week'+str(x)].append(easy_topics_list[slice_beg[2]:slice_end[2]])	#easy
			slice_beg[0] = slice_end[0]
			slice_beg[1] = slice_end[1]
			slice_beg[2] = slice_end[2]
			slice_end[0] += hard_distribution[week_count]
			slice_end[1] += medium_distribution[week_count]
			slice_end[2] += easy_distribution[week_count]
			week_count += 1

	return plan


#....................................Global Funcitons Ends

app = Flask(__name__)


app.config['JSON_SORT_KEYS'] = False


#database configuration
app.config["MONGO_URI"] = "mongodb://aniket:Aniketsprx077@cluster0-shard-00-00-uugt8.mongodb.net:27017,cluster0-shard-00-01-uugt8.mongodb.net:27017,cluster0-shard-00-02-uugt8.mongodb.net:27017/main?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
mongo = PyMongo(app)


#for sessions
app.secret_key = 'aniket'									
app.permanent_session_lifetime = timedelta(days = 28)
#currently uses two session variables
#session['user'] this is the basic session variable for auto login. Used to set the values of session['login']
#session['login'] this was created for the purpose of seperating handle login and account route
# it basically saves the email in it and if this exist, email is taken, this session is poppped and user is sent to account page


@app.route('/test')
def test():
	print(linear_curve(100,210))
	return "this is test"


@app.route('/blogadmin')
def blogadmin():
	return render_template('blogadmin.html')

@app.route('/blog')
def blog():
	return render_template('blog.html')

@app.route('/prep')
def prep():
	return render_template('prep.html')


@app.route('/privacypolicy')
def privacypolicy():
	return render_template('privacypolicy.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/submit_feedback', methods=['POST','GET'])
def submit_feedback():
	if request.method == 'POST':
		data = dict(request.form)
		x = mongo.db.feedback.insert_one(data)
		print(x)
		return "Feedback Submitted. Thank You."

@app.route('/demo')
def demo():
	return render_template('demo.html')

@app.route('/get_demo', methods=['POST','GET'])
def get_demo():
	if request.method == 'POST':
		data = dict(request.form)
		
		year = data['year']
		curve = data['curve']
		allTopicList = allTopicCode(data['exam'])
		revision = data['revision']
		

		all_topics = {}
		topic_data =  mongo.db.syllabus.find_one({'exam': data['exam']})
		for key in topic_data[data['exam']]:
			topics = topic_data[data['exam']][key]
			for topic in topics:
				all_topics[topic[0]] = topic[1:5]
		res = {
		'plan' : getPlan(target_year=str(year),curve=curve,topic_list=allTopicList,revision=int(revision)),
		'topics' : all_topics
		}
		
		return json.dumps(res)
	else:
		return  "request not post"


@app.route('/survey')
def survey():
	return render_template('survey.html')

@app.route('/handle_survey', methods=['GET', 'POST'])
def handle_survey():
	if request.method == 'POST':
		data = dict(request.form)
		print(data)
		x = mongo.db.survey_data.insert_one(data)
		print(x)
		return 'success'


@app.route('/get_topics', methods=['POST','GET'])
def get_topics():
	data = dict(request.form)
	syllabus = allTopicList(data['exam'])
	x = mongo.db.survey_users.insert_one(data)
	print(x)
	return json.dumps({'data' : syllabus})


@app.route('/thanks')
def thanks():
	return "<h1>Thank You</h1>"

@app.route('/')
def main():
	ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	now = datetime.now()
	date = now.strftime("%Y-%m-%d/%H:%M:%S")
	mongo.db.ip.insert_one({'ip':ip,'date':date})
	if 'user' in session:
		return render_template('index.html', res=json.dumps({'login': session['user']}))	
	else:
		return render_template('index.html', res=json.dumps({'login': 'loggedout'}))	

	

@app.route('/create')
def create():
	return render_template('signup.html')

@app.route('/handle_create', methods=['POST','GET'])
def handle_create():

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password1']

		user = (mongo.db.cred.find({'email': email}))
		print("user: ", user)

		if mongo.db.cred.find_one({"email": email}) != None:
		 	return redirect(url_for('create', msg="email_exists", **request.args))
		else:
		 	print("no such email")
		 	now = date.today()
		 	user_data =  {	'email':email,
		 					'password': password,
		 					 'membership' : 'unpaid',
		 					 'streak' : [{'start_date' : [now.year, now.month, now.day],'last_date'	: [now.year, now.month, now.day]}]
		 				}

		 	print("USER DATA: ", user_data)

		 	mongo.db.cred.insert_one(user_data)
		 	session['user'] = email
		return redirect(url_for('login'))
	else:
		return redirect(url_for('create'))

@app.route('/user_config')
def user_config():
	if 'user' in session:
		email = session['user']
		return render_template('configure.html', res=json.dumps({'email' : email}))
	else:
		return redirect(url_for('login'))

@app.route('/send_syllabus', methods=['POST', 'GET'])
def get_syllabus():
	
	if (mongo.db.syllabus.find_one({'exam':request.form['exam']})) != None:
		data = dumps(mongo.db.syllabus.find_one({'exam':request.form['exam']}))
	else:
		data = {"error" : "Couldn't fetch data"}
	return data


@app.route('/handle_config', methods=['POST', 'GET'])
def handle_config():
	if request.method == 'POST':
		email = request.form['email']
		name = request.form['name']
		exam = request.form['exam']
		year = request.form['year']
		curve = request.form['curve']
		college = request.form['college']
		revision = request.form['revision']
		college_year = request.form['college_year']
		completed_topics = request.form.getlist('c_topic')

		#here is the problem the user topics is sorted
		# user_topics = (list(set(allTopicCode(exam)) - set(completed_topics)))		#removes the completed topics from all topics
		# print('user_topics', user_topics)
		
		allTopicList = allTopicCode(exam)
		user_topics_unsorted = []
		for code in allTopicList:
			if code not in completed_topics:
				user_topics_unsorted.append(code)

		pretty(getPlan(target_year=str(year),curve=curve,topic_list=user_topics_unsorted,revision=int(revision)))

		document = {
		'email' : email,
		'name' : name,
		'exam' : exam,
		'year' : year,
		'curve' : curve,
		'college' : college,
		'college_year' : college_year,
		'plan' : [getPlan(target_year=str(year),curve=curve,topic_list=user_topics_unsorted,revision=int(revision))]
		}

		
		msg = mongo.db.user.insert_one(document)
		print(msg)

	return redirect(url_for('login'))

@app.route('/login')
def login():
	if 'user' in session:
		session['login'] = session['user']
		if mongo.db.user.find_one({"email": session['user']}) != None:	
			return redirect(url_for('account'))
		else:
			return redirect(url_for('user_config'))
	else:
		return render_template('login.html')

@app.route('/handle_login', methods=['POST','GET'])
def handle_login():

	if request.method == 'POST':
		session.pop('login', None)
		email = request.form['email']
		password = request.form['password']
		if mongo.db.cred.find_one({"email": email}) != None:
			if password == mongo.db.cred.find_one({"email": email})['password']:
				session['login'] = email
				session['user'] = email
				if mongo.db.user.find_one({"email": session['user']}) != None:
					return redirect(url_for('account'))
				else:
					return redirect(url_for('user_config'))
			else:
				return redirect(url_for('login',msg="password_error", **request.args))
		else:
			return redirect(url_for('login',msg="email_error", **request.args))
	else:
		return redirect(url_for('login'))


@app.route('/send_checked_topics', methods=['POST','GET'])
def send_checked_topics():
	if request.method == 'POST':
		data = request.form
		data = dict(data)
		thePlan = mongo.db.user.find_one({'email': data['email']})['plan'][0]
		print(thePlan)

		theWeek = thePlan[data['topicMonth']][data['topicWeek']]
		print("before: ", theWeek)
		print(data['topicCode'])
		for x in range(len(theWeek)):
			for y in range(len(theWeek[x])):
				print(theWeek[x][y])
				if (data['topicCode'] == theWeek[x][y][0]):
					if data['topicState'] == 'true':
						theWeek[x][y][1] = 'C'
					else:
						theWeek[x][y][1] = 'P'

		thePlan[data['topicMonth']][data['topicWeek']] =  theWeek

		mongo.db.user.update_one({'email' : data['email']},{'$set':{'plan' : [thePlan]}})
		print("after: ", theWeek)
		return "success"
	else:
		return redirect(url_for('main'))

@app.route('/send_motivation', methods=['GET','POST'])
def send_motivation():
	if request.method == 'POST':
		mno = random.randint(0,400)
		quote = mongo.db.motivation.find_one({'mno': mno})
		print(quote)
		del quote['_id']

		return quote
	else:
		return redirect(url_for('main'))


@app.route('/account')
def account():
	if 'login' in session:
		email = session['login']
		session.pop('login', None)
		data = (mongo.db.user.find_one({"email": email}))
		if data != None:
			del data['_id']		#can't be sent in the json object, and it was not required anyway
		else:
			return redirect(url_for('main'))
		
		#sending current month
		today = date.today()
		year = str(today.year)
		month = month_list[today.month - 1 ] +'_'+ year
		streak  = getStreak(data['email'])
		data['plan'] = data['plan'][0]


		mno = random.randint(0,400)
		quote = mongo.db.motivation.find_one({'mno': mno})
		print(quote)
		del quote['_id']

		return render_template('new_account.html',data=json.dumps(data, sort_keys=False),date=json.dumps({'month':month, 'streak': streak}),topics=json.dumps({'topics':allTopicList(exam=data['exam'])}), motivation=json.dumps(quote))
	else:
		return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session.pop('login', None)
	session.pop('user', None)
	return redirect(url_for('main'))

@app.route('/delete_account', methods=['POST','GET'])
def delete_account():
	if request.method == 'POST':
		data = dict(request.form)

		user_cred =  mongo.db.cred.find_one({'email' : data['email']})
		
		if user_cred['password'] == data['password']:
			print("Account deleted")
			database_response = mongo.db.user.remove({'email': data['email']})
			print(database_response)
			return "success"
		else:
			print('password error')
			return "Incorrect Password"


#ERROR HANDLING

@app.errorhandler(404)
def page_not_found(e):
    return render_template('Error.html'), 404

@app.errorhandler(403)
def page_forbidden(e):
    return render_template('Error.html'), 403

@app.errorhandler(410)
def page_gone(e):
    return render_template('Error.html'), 410

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('Error.html'), 500




if __name__ == "__main__":
    app.run(debug=True)
