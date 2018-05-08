from flask import Flask, render_template, request, make_response
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from azure.storage.blob import PublicAccess
from pymongo import MongoClient
import pyodbc
import MySQLdb
import time
import pymongo
import base64
import os

app = Flask(__name__)

accountname = 'rg1diag351'
accountkey = 'd90gqj0G+rC8y7CFbFcbEbn6UyYQblGF/pbsrQaEW8jHzlm/JPkubqBkEGi5+blC+TtJo4z3QdrI0e1T8fQjcw=='
containername = 'container1'
blobservice = BlockBlobService(account_name=accountname,account_key=accountkey)
if blobservice:
	print 'success'
blobservice.create_container(containername,public_access=PublicAccess.Container)

host = 'hemaserver1.mysql.database.azure.com'
user = 'server@hemaserver1'
password = 'Cloudcomputing6331!'
dbname = 'mydb'
db = MySQLdb.connect(host=host,user=user,passwd=password,db=dbname)
cur = db.cursor()

client = MongoClient('mongodb://hema:9tlRdmzDR3BinQIVRTHOvsTpyi4mhh6J4LDG7szKoC9PktZAXfALPzivmiB7oB6dler77iREp7IvZe6uo7gvkA==@hema.documents.azure.com:10255/?ssl=true&replicaSet=globaldb')
db = client['mongodb-1']
data1 = db.data

@app.route('/')
def hello_world():
	return render_template('index.html')
		
@app.route('/uploadcsv', methods=['GET','POST'])
def uploadcsv():
	cur.execute('drop table mytable1;')
	cur.execute('drop table mytable;')
	cur.execute('create table mytable(foodname varchar(35),foodtype varchar(15),col1 integer,col2 integer,col3 integer,qcount integer, primary key (foodname));')
	cur.execute('commit;')
	cur.execute('create table mytable1(ingredient varchar(15),qcount integer,foodname varchar(35),foreign key(foodname) references mytable(foodname));')
	cur.execute('commit;')
	path = '/home/hema/flaskapp/csvfiles/'
	for file in os.listdir(path):
		filename = path + file
		print filename
		fp = open(filename,'r')
		contents = fp.readlines()
		fp.close()
		foodtype = contents[2].split(',')
		first = contents[0].split(',')
		print 'insert into mytable values("' + file.split('.')[0] + '","' + foodtype[0] + '",' + first[0] + ',' + first[1] + ',' + first[2].split('\r')[0] + ',0);'
		cur.execute('insert into mytable values("' + file.split('.')[0] + '","' + foodtype[0] + '",' + first[0] + ',' + first[1] + ',' + first[2].split('\r')[0] + ',0);')
		cur.execute('commit;')		
		data = contents[1].split(',')
		print 'insert into mytable1 values("' + data[0] + ',0,"' + file.split('.')[0] + '");'
		for i in range(len(data)):
			cur.execute('insert into mytable1 values("' + data[i].split('\r')[0] + '",0,"' + file.split('.')[0] + '");')
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
	
@app.route('/query2',methods=['GET','POST'])
def query2():
	parameter1 = request.form['parameter1']
	#print 'select count(*),' + parameter1 + ',foodname from mytable1 group by ' + parameter1 + ' order by count(*) desc;'
	#cur.execute('select count(*),' + parameter1 + ',foodname from mytable1 group by ' + parameter1 + ' order by count(*) desc;')
	print 'select count(*),ingredient,foodname from mytable1 where ingredient="' + parameter1 +'";'
	cur.execute('select foodname from mytable1 where ingredient="' + parameter1 +'";')
	result = cur.fetchall()
	count = []
	field = []
	food = []
	for i in range(cur.rowcount):
		document = data1.find_one({"name": result[i][0]+'.jpg'})
		print result[i][0]+'.jpg'
		if document:
			food.append(document["content"])
		else:
			print 'inside else'
			food.append("None")
	row=cur.rowcount
	cur.execute('select * from mytable where foodname="'+ parameter1 +'" or foodtype="' + parameter1 +'";')
	r1 = cur.fetchall()
	if cur.rowcount > 0:
		print 'update mytable set qcount=qcount+1 where foodname="' + parameter1 + '" or foodtype="' + parameter1 + '";'
		cur.execute('update mytable set qcount=qcount+1 where foodname="' + parameter1 + '" or foodtype="' + parameter1 + '";')
		cur.execute('commit;')
	cur.execute('select * from mytable1 where ingredient="'+ parameter1 + '";')
	r2 = cur.fetchall()
	if cur.rowcount > 0:		
		print 'update mytable1 set qcount=qcount+1 where ingredient="' + parameter1 + '";'
		cur.execute('update mytable1 set qcount=qcount+1 where ingredient="' + parameter1 + '";')
		cur.execute('commit;')	
	return render_template('index.html',msg2=row,imagecontent=food)
	
@app.route('/query3',methods=['GET','POST'])
def query3():
	parameter1 = request.form['parameter1']
	parameter2 = request.form['parameter2']
	print parameter1	
	cur.execute('select * from mytable where foodname="'+ parameter1 +'" or foodtype="' + parameter1 +'";')
	r1 = cur.fetchall()
	if cur.rowcount > 0:
		print 'update mytable set qcount=qcount+1 where foodname="' + parameter1 + '" or foodtype="' + parameter1 + '";'
		cur.execute('update mytable set qcount=qcount+1 where foodname="' + parameter1 + '" or foodtype="' + parameter1 + '";')
		cur.execute('commit;')
	cur.execute('select * from mytable1 where ingredient="'+ parameter1 + '";')
	r2 = cur.fetchall()
	if cur.rowcount > 0:		
		print 'update mytable1 set qcount=qcount+1 where ingredient="' + parameter1 + '";'
		cur.execute('update mytable1 set qcount=qcount+1 where ingredient="' + parameter1 + '";')
		cur.execute('commit;')
	return render_template('index.html')

@app.route('/query4',methods=['GET','POST'])
def query4():
	path = '/home/hema/flaskapp/images/'
	files = os.listdir(path)
	images = []
	for file in files:
		document = data1.find_one({"name": file})
		if document:
			images.append(document['content'])
	return render_template('index.html',display=images,row=len(images),files=files)
	
@app.route('/query5',methods=['GET','POST'])
def query5():
	parameter1 = request.form['parameter1']
	range = parameter1.split('-')
	print 'select foodname from mytable where col1>=' + range[0] + ' and col1<=' + range[1] + ';'
	cur.execute('select foodname from mytable where col1>=' + range[0] + ' and col1<=' + range[1] + ';')
	result = cur.fetchall()
	print result
	images = []
	names = []
	for file in result:		
		document = data1.find_one({"name": file[0]+'.jpg'})
		if document:
			images.append(document['content'])
			names.append(file[0])
	return render_template('index.html',image1=images,files=names,rows=cur.rowcount)
	
@app.route('/query6',methods=['GET','POST'])
def query6():
	print 'select distinct qcount,ingredient from mytable1 order by qcount desc;'
	cur.execute('select distinct qcount,ingredient from mytable1 order by qcount desc;')
	result = cur.fetchall()
	return render_template('index.html',res6=result,rows=5)
	
@app.route('/query7',methods=['GET','POST'])
def query7():
	parameter1 = request.form['parameter1']
	print 'select foodname from mytable where col2<' + parameter1 + ';'
	cur.execute('select foodname from mytable where col2<' + parameter1 + ';')
	result = cur.fetchall()
	return render_template('index.html',res7=result,rows=cur.rowcount)
	
if __name__ == '__main__':
  app.run()