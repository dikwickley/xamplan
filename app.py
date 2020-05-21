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


def allTopicList(exam):
	
	all_topics = {}
	data =  mongo.db.syllabus.find_one({'exam': exam})
	for key in data[exam]:
		topics = data[exam][key]
		for topic in topics:
			all_topics[topic[0]] = topic[1:5]
	return all_topics




app = Flask(__name__)



app.config['JSON_SORT_KEYS'] = False


#database configuration
app.config["MONGO_URI"] = "mongodb://aniket:Aniketsprx077@cluster0-shard-00-00-uugt8.mongodb.net:27017,cluster0-shard-00-01-uugt8.mongodb.net:27017,cluster0-shard-00-02-uugt8.mongodb.net:27017/main?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
mongo = PyMongo(app)

app.secret_key = 'aniket'									
app.permanent_session_lifetime = timedelta(days = 28)


@app.route('/')
def survey():
	return render_template('survey.html')

@app.route('/handle_survey', methods=['GET', 'POST'])
def handle_survey():

	if request.method == 'POST':

		data = request.form
		print(data)

		return "DATA"
	else:
		return redirect(url_for('/'))


@app.route('/get_topics', methods=['POST','GET'])
def get_topics():

	exam = dict(request.form)
	syllabus = allTopicList(exam['exam'])
	return json.dumps({'data' : syllabus})

if __name__ == "__main__":
    app.run(debug=True)