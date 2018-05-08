from flask import Flask, render_template, request, jsonify, make_response
import boto
import boto.s3.connection
import boto.rds
from boto.s3.key import Key
import datetime
import hashlib
import base64

app = Flask(__name__)

access_key = 'accesskey'
secret_access_key = 'secretaccesskey'
bucket_name = 'my_bucket_list'

s3 = boto.connect_s3(access_key,secret_access_key)
bucket = s3.create_bucket(bucket_name, location=boto.s3.connection.Location.DEFAULT)

@app.route('/')
def login():
        filename = 'user.txt'
        key = bucket.new_key(filename)
        key.key = filename
        key.set_contents_from_string(base64.b64encode('vijay:vijay@123\nuser:user@123'))
        return render_template('login.html')

@app.route('/send', methods=['GET','POST'])
def send():
        if request.method == 'POST':
                username = request.form['username'];
                password = request.form['password'];
                for mylist in bucket.list():
                        if 'user.txt' == mylist.key :
                                mylist.get_contents_to_filename('/home/ubuntu/flaskapp/downloaded_file')
                                with open('/home/ubuntu/flaskapp/downloaded_file','r') as fp:
                                        downloaded_contents = base64.b64decode(fp.read())
                                        print 'filecontents: ',downloaded_contents
                                        fp.close()
                                        data1 = downloaded_contents.split('\n')
                                        print data1
                                        for data in data1:
                                                details = data.split(':')
                                                print details,username,password
                                                if username == details[0] and password == details[1]:
                                                        print 'login successful'
                                                        return render_template('index.html', user=username)
        return render_template('login.html', msg='failure')


@app.route('/home', methods=['GET','POST'])
def home():
        return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
        return render_template('upload.html')

@app.route('/uploadToCloud', methods=['GET','POST'])
def uploadToCloud():
        if request.method == 'POST':
                fname = request.files['file']
                contents = fname.read()
                encoded_contents = base64.b64encode(contents);
                key = bucket.new_key(fname.filename)
                key.key = fname.filename
                key.set_contents_from_string(encoded_contents)
                b_list = bucket.list()
                files = getfilelist()
                if fname.filename in files:
                        print 'file uploaded successfully'
                        return render_template('upload.html',msg='success')
                else:
                        print 'file upload failed'
                        return render_template('upload.html',msg='failed')
        return render_template('upload.html',msg='')

@app.route('/download', methods=['GET','POST'])
def download():
        filelist = getfilelist()
        return render_template('download.html',files=filelist)

@app.route('/downloadFromCloud', methods=['GET','POST'])
def downloadFromCloud():
        if request.method == 'POST':
                filename = request.form['filename']
                for mylist in bucket.list():
                        if filename == mylist.key:
                                print 'Name: ',mylist.key
                                mylist.get_contents_to_filename('/home/ubuntu/flaskapp/downloaded_file')
                                with open('/home/ubuntu/flaskapp/downloaded_file','r') as fp:
                                        downloaded_contents = base64.b64decode(fp.read())
                                        fp.close()
                                        response = make_response(downloaded_contents)
                                        response.headers['Content-disposition'] = "attachment; filename=%s"%filename
                                        return response
        return render_template('download.html',files=filelist, msg='')

@app.route('/remoteList', methods=['GET','POST'])
def remoteList():
        files = getfilelist()
        return render_template('remoteList.html',filelist=files)

@app.route('/delete', methods=['GET','POST'])
def delete():
        files = getfilelist()
        return render_template('delete.html',filelist=files)

@app.route('/deleteFromCloud', methods=['GET','POST'])
def deleteFromCloud():
        if request.method == 'POST':
                fname = request.form['filename']
                print fname
                for mylist in bucket.list():
                        if fname == mylist.key:
                                bucket.delete_key(mylist.key)
                                break
                flag = 0
                for mylist in bucket.list():
                        if fname == mylist.key:
                                flag = 1
                if flag == 0:
                                print 'File deleted successfully'
                else:
                                print 'File deletion failed'
                return render_template('delete.html',msg='success')

def getfilelist():
        files = []
        for mylist in bucket.list():
                if 'user.txt' != mylist.key:
                        files.append(mylist.key)
        print files
        return files

if __name__ == '__main__':
        app.run()