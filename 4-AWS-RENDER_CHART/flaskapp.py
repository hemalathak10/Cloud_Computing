from flask import Flask, render_template, request
import MySQLdb
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import boto
import boto.s3
import sys
from boto.s3.key import Key
import json
import pygal
import time

app = Flask(__name__)

accesskey = 'AKIAJYNS62DCQMXMXOTQ'
secretaccesskey = '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'
bucket_name = 'mybuckethema'
host = 'mydb.chptgni3gne2.us-east-2.rds.amazonaws.com'
user = 'hema'
password = 'Cloud6331!'
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
	cur.execute('create index index1 on mytable(Surname) using btree;')
	cur.execute('create index index2 on mytable(Centimeters) using btree;')
	cur.execute('create index index3 on mytable(State) using btree;')
	cur.execute('create index index4 on mytable(Age) using btree;')
	cur.execute('load data local infile \'/home/ubuntu/flaskapp/data.csv\' into table mytable fields terminated by \',\' optionally enclosed by \'"\' lines terminated by \'\n\' ignore 1 lines;')
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
	parameter3 = request.form['parameter3']
	charttype = request.form['chart']
	print charttype
	cur.execute('select ' + parameter1 + ',' + parameter2 + ' from mytable limit 1000;')
	result = cur.fetchall()
	final = []
	for data in result:
		final.append([data[0],data[1]])
	X = np.array(final)
	starttime = time.time()
	clt = KMeans(n_clusters=int(parameter3),random_state=0).fit(X)
	centroids = clt.cluster_centers_
	labels = clt.labels_
	u,c = np.unique(labels,return_counts=True)
	d = dict(zip(u,c))
	if charttype == 'RENDER PIE CHART' or charttype == 'RENDER BAR CHART':
		content = 'xaxis,yaxis\n'
		for k,v in d.iteritems():
			content = content + str(k)+','+str(v)+'\n'
		key = bucket.new_key('piechart.csv')
		key.key = 'piechart.csv'
		key.set_contents_from_string(content)
		bucket.set_acl('public-read',key)
		if charttype == 'RENDER PIE CHART':
			endtime = time.time()
			executiontime = endtime - starttime
			return render_template('piechart.html',t=executiontime)
		else:
			endtime = time.time()
			executiontime = endtime - starttime
			return render_template('barchart.html',t=executiontime)
	elif charttype == 'RENDER SCATTER CHART':
		xy_chart = pygal.XY(stroke=False)
		xy_chart.title = 'SCATTER PLOT'
		datalist = {}
		for i in range(len(result)):
			if labels[i] in datalist.keys():
				datalist[labels[i]].append((result[i][0],result[i][1]))
			else:
				datalist[labels[i]] = [(result[i][0],result[i][1])]
		for i in range(int(parameter3)):
			datapoints = len(datalist[i])
			xy_chart.add('cluster '+str(i+1)+' ('+str(datapoints)+')', datalist[i])
		for i in range(int(parameter3)):			
			xy_chart.add('centroid '+str(i+1), [(centroids[i][0],centroids[i][1])])
		chart = xy_chart.render(is_unicode=True)
		endtime = time.time()
		executiontime = endtime - starttime
		return render_template('scatterchart.html',chart=chart,t=executiontime)
	
if __name__ == '__main__':
  app.run()