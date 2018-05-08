from flask import Flask, render_template, request
import MySQLdb
import numpy as np
import boto
import boto.s3
import sys
from boto.s3.key import Key
import time
from subprocess import call
import commands

app = Flask(__name__)

accesskey = 'accesskey'
secretaccesskey = 'secretaccesskey'
bucket_name = 'mybucket'
host = 'hostname'
user = 'user'
password = 'password'
dbname = 'mydb'

db = MySQLdb.connect(host=host,user=user,passwd=password,db=dbname)
cur = db.cursor()
s3 = boto.connect_s3(accesskey,secretaccesskey)
bucket = s3.create_bucket(bucket_name, location=boto.s3.connection.Location.DEFAULT)

@app.route('/', methods=['GET','POST'])
def mainpage():
	return render_template('index.html')

@app.route('/uploadcsv', methods=['GET','POST'])
def uploadcsv():
	cur.execute('drop table mytable;')
	cur.execute('create table mytable(Gender	varchar(10),GivenName varchar(20),Surname varchar(20),StreetAddress varchar(20),City varchar(15),State varchar(20),EmailAddress varchar(30),Username varchar(15),TelephoneNumber varchar(15),Age double,BloodType varchar(5),Centimeters integer,Latitude double,Longitude double);')
	cur.execute('load data local infile \'/tmp/gutenberg/data.csv\' into table mytable fields terminated by \',\' optionally enclosed by \'"\' lines terminated by \'\n\' ignore 1 lines;')
	cur.execute('commit;')
	return render_template('index.html',msg='success')

@app.route('/query1', methods=['GET','POST'])
def query1():
	cur.execute('select count(*) from mytable;')
	result = cur.fetchall()
	rows = cur.rowcount
	one = result[0]
	cols = len(one)
	print one
	print 'rowcount: ',rows
	print 'colcount: ',cols
	return render_template('index.html',res1=result,row=rows,col=cols,header='COUNT')

@app.route('/query2', methods=['GET','POST'])
def query2():
	print 'executing!!'
	print commands.getoutput('sudo -S -u hduser rm /tmp/user/part-00000')
	print commands.getoutput('sudo -S -u hduser /usr/local/hadoop/bin/hadoop dfs -rmr /user/hduser/*')
	print commands.getoutput('sudo -S -u hduser /usr/local/hadoop/bin/hadoop dfs -copyFromLocal /tmp/user /user/hduser/user')
	command_output = commands.getoutput('sudo -S -u hduser /usr/local/hadoop/bin/hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.6.1.jar -file /home/hduser/flaskapp/mapper.py -mapper "python /home/hduser/flaskapp/mapper.py" -file /home/hduser/flaskapp/reduce.py -reducer "python /home/hduser/flaskapp/reduce.py" -input /user/hduser/user/* -output /user/hduser/user/user-output')
	print command_output
	if 'streaming.StreamJob: Output directory: /user/hduser/user/user-output' in command_output:
		print 'Success !!!'
		print commands.getoutput('sudo -S -u hduser /usr/local/hadoop/bin/hadoop dfs -copyToLocal /user/hduser/user/user-output/part-00000 /tmp/user')
		fp = open('/tmp/user/part-00000','r')
		contents = fp.readlines()
		fp.close()
		return render_template('index.html',msg2='success',content=contents)
	else:
		return render_template('index.html',msg2='failure')
	
if __name__ == '__main__':
  app.run()
