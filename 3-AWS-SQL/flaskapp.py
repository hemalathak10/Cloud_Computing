from flask import Flask, render_template, request, jsonify, make_response
import boto
import boto.s3.connection
import boto.rds
from boto.s3.key import Key
import datetime
import hashlib
import base64
import mimetypes
import MySQLdb
import csv
import memcache
import random
import time

app = Flask(__name__)

accesskey = 'accesskey'
secretaccesskey = 'secretccesskey'
bucket_name = 'mybucket'

host = 'hostname'
user = 'user'
password = 'password'
dbname = 'mydb'
farerange = []

s3 = boto.connect_s3(accesskey,secretaccesskey)
bucket = s3.create_bucket(bucket_name, location=boto.s3.connection.Location.DEFAULT)

db = MySQLdb.connect(host=host,user=user,passwd=password,db=dbname)
cur = db.cursor()

memhost = 'mymemcache.uacsj9.cfg.use2.cache.amazonaws.com:11211'

mc = memcache.Client([memhost], debug=0)

@app.route('/')
def login():
	return render_template('index.html')

@app.route('/uploadcsv', methods=['GET','POST'])
def uploadcsv():
	cur.execute('drop table mytable;')
	cur.execute('create table mytable(mytime timestamp,latitude double,longitude double,depth double,mag double,magType varchar(4),nst integer,gap double,dmin double,rms double,net varchar(3),id varchar(11),updated timestamp,place varchar(50),typess varchar(20),horizontalError double,depthError double,magError double,magNst double,statuss varchar(20),locationSource varchar(3),magSource varchar(3));')
	#cur.execute('create table mytable(pclass integer,survived integer,name varchar(30),sex varchar(10),age double,ticket	varchar(15),fare double,cabin varchar(15),home varchar(30));')
	cur.execute('create index index1 on mytable(longitude) using btree;')
	cur.execute('load data local infile \'/home/ubuntu/flaskapp/all_month.csv\' into table mytable fields terminated by \',\' optionally enclosed by \'"\' lines terminated by \'\n\' ignore 1 lines;')
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
	parameter1 = request.form['parameter1']
	parameter2 = request.form['parameter2']
	cur.execute('select count(*) from mytable where age = %s and sex = %s;',(parameter1,parameter2))
	count = cur.fetchall()
	cur.execute('select name from mytable where age = %s and sex = %s;',(parameter1,parameter2))
	result = cur.fetchall()
	rows = cur.rowcount
	one = result[0]
	cols = len(one)
	print one
	print 'rowcount: ',rows
	print 'colcount: ',cols
	query = 'select name from mytable where age = ' + parameter1 + ' and sex = ' + parameter2 + ';'
	query = query.replace(' ',':')
	mc.set(query,result)
	print 'memcache: ',mc.get(query)
	return render_template('index.html',res2=result,row=rows,col=cols,header='name',c=count)

@app.route('/query3', methods=['GET','POST'])
def query3():
	parameter = request.form['parameter']
	starttime = time.time()
	for i in range(0,500):
		rn = random.uniform(-62.5965,84.659)
		mykey = parameter + ':' + str(rn)
		datafrommc = mc.get(mykey)
		if not datafrommc:
			query = 'select * from mytable where ' + parameter + ' = ' + str(rn) + ';'
			cur.execute(query)
			if cur.rowcount > 0:
				print 'inside if'
				mc.set(mykey,cur.fetchall())
	endtime = time.time()
	executiontime = endtime - starttime
	print 'time: ',executiontime
	return render_template('index.html',time=executiontime)	

@app.route('/query4', methods=['GET','POST'])
def query4():
	parameter = request.form['parameter']
	starttime = time.time()
	for i in range(0,500):
		rn = random.uniform(-62.5965,84.659)
		query = 'select * from mytable where ' + parameter + ' = ' + str(rn) + ';'
		cur.execute(query)
	endtime = time.time()
	executiontime = endtime - starttime
	print 'time: ',executiontime
	return render_template('index.html',time1=executiontime)	

@app.route('/query5', methods=['GET','POST'])
def query5():
	parameter1 = request.form['parameter1']
	parameter2 = request.form['parameter2']
	starttime = time.time()
	for i in range(0,500):
		mykey = parameter1 + ':' + parameter2
		datafrommc = mc.get(mykey)
		if not datafrommc:
			query = 'select * from mytable where ' + parameter1 + ' = ' + parameter2 + ';'
			cur.execute(query)
			if cur.rowcount > 0:
				print 'inside if'
				mc.set(mykey,cur.fetchall())
	endtime = time.time()
	executiontime = endtime - starttime
	print 'time: ',executiontime
	return render_template('index.html',time2=executiontime)	

@app.route('/query6', methods=['GET','POST'])
def query6():
	parameter1 = request.form['parameter1']
	parameter2 = request.form['parameter2']
	starttime = time.time()
	for i in range(0,500):
		query = 'select * from mytable where ' + parameter1 + ' = ' + parameter2 + ';'
		cur.execute(query)
	endtime = time.time()
	executiontime = endtime - starttime
	print 'time: ',executiontime
	return render_template('index.html',time3=executiontime)

@app.route('/query7', methods=['GET','POST'])
def query7():
	fname = 'all_month.csv'
	fp = open(fname,'r')
	key = bucket.new_key(fname)
	key.key = fname
	key.set_contents_from_string(fp.read())
	fp.close()
	for mylist in bucket.list():
		if fname == mylist.key:
			print 'file uploaded successfully'
			return render_template('index.html',msg1='success')
		else:
			print 'file upload failed'
			return render_template('index.html',msg1='failure')
	return render_template('index.html')

if __name__ == '__main__':
	app.run()
