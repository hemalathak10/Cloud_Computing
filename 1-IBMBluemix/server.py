#################################################################################
#																				#
#	Filename	:	server.py													#
#																				#
#	Author		:	Hemalatha Krishnan											#
#																				#
#	Description	:	The scripts connects to the IBM Bluemix for upload and		#
#					download actions with encryption and decryption				#
#																				#
#	Course No	:	6331														#
#																				#
#	Lab No		:	1															#	
#																				#
#################################################################################

#importing the required modules from the python library
import swiftclient
import keystoneclient
import os
from cryptography.fernet import Fernet
import mimetypes

#key for encryption and decryption
key = 'mPugypH1sWC82zJQ3_He9DmCbheSd29zLDMoUhAQPZo='
encryptKey = Fernet(key)

#defining the variables required for the connection to the IBM Bluemix
password='password'
auth_url='https://identity.open.softlayer.com/v3/'
auth_version=3
projId='projid'
userId='userid'
region='region'
container_name='ContainerForFiles'

#Connecting to the IBM Bluemix server
print 'Connecting to the IBM Bluemix server......'
conn_obj = swiftclient.Connection(key=password, authurl=auth_url, auth_version='3', os_options={"project_id": projId, "user_id": userId, "region_name": region})
if not conn_obj:
	print 'Connection to the IBM Bluemix failed!!'
print 'Connection to IBM Bluemix......'

#creating a container on the IBM Bluemix server to store files
conn_obj.put_container(container_name)
print 'Container created on the cloud'

#################################################################################
#																				#
#	Functionname	:	upload													#
#																				#
#	Author			:	Hemalatha Krishnan										#
#																				#
#	Description		:	The function uploads a folder to the cloud after		# 
#						encryption 												#
#																				#
#################################################################################
	
def upload(path):
	#rootDir = 'F:\Python\Flask_Examples\IBMBluemix-Assignment1\upload_folder'
	for dirName, subdirList, fileList in os.walk(path):
		for fname in fileList:
			file_location = (dirName+ "\\" + fname)
			with open(file_location, 'rb') as example_file:				
				conn_obj.put_object(container_name,fname,contents=encryptKey.encrypt(example_file.read()),content_type='jpg')
				#conn_obj.put_object(container_name,fname,contents=example_file.read(),content_type='jpg')
				print fname + ' file uploaded successfully!!'
				example_file.close()
	print '\n';

#################################################################################
#				hema																#
#																				#
#	Functionname	:	upload_file												#
#																				#
#	Author			:	Hemalatha Krishnan										#
#																				#
#	Description		:	The function uploads a file to the cloud after			# 
#						encryption 												#
#																				#
#################################################################################
				
def upload_file(path,fname):
	#rootDir = 'F:\Python\Flask_Examples\IBMBluemix-Assignment1\upload_folder'
	for dirName, subdirList, fileList in os.walk(path):
		file_location = (dirName+ "\\" + fname)
		if os.path.isfile(file_location):
			with open(file_location, 'rb') as example_file:				
				conn_obj.put_object(container_name,fname,contents=encryptKey.encrypt(example_file.read()),content_type='text')
				#conn_obj.put_object(container_name,fname,contents=example_file.read(),content_type='jpg')
				print fname + ' file uploaded successfully!!'
				example_file.close()
		else:
			print name + ' not present in the path ' + path + '\n'
			
#################################################################################
#																				#
#	Functionname	:	download												#
#																				#
#	Author			:	Hemalatha Krishnan										#
#																				#
#	Description		:	The function downloads a file to the cloud				#
#																				#
#################################################################################

def download(filename):
	file_list = [];
	for container in conn_obj.get_account()[1]:
		for data in conn_obj.get_container(container['name'])[1]:
			file_list.append(data['name'])
	print file_list;
	if filename in file_list:		
		file_obj = conn_obj.get_object(container_name, filename)
		new_file_name = 'C:\Users\H.E.M.A\Downloads' + "\\" + filename
		with open(new_file_name,'wb') as my_copy_file:
			my_copy_file.write(encryptKey.decrypt(file_obj[1]))
			#my_copy_file.write(file_obj[1])
			print filename + ' file downloaded successfully!!\n'
	else:
		print filename + ' not present on the cloud\n'
		
#################################################################################
#																				#
#	Functionname	:	main													#
#																				#
#	Author			:	Hemalatha Krishnan										#
#																				#
#	Description		:	The function takes input from the user					#
#																				#
#################################################################################
		
def main():
	while(1):
		print 'Select among the below options:'
		print '1: Upload'
		print '2: Upload file'
		print '3: Download'
		print '4: Sync'
		print '5: Exit'
		option = input('Enter your choice: ')
		if option == 1:
			path = raw_input('Enter the file path: ')
			upload(path);
		elif option == 2:
			path = raw_input('Enter the file path: ')
			name = raw_input('Enter the file name: ')
			upload_file(path,name)
		elif option == 3:
			filename = raw_input('Enter the file name: ')
			download(filename)
		elif option == 4:
			path = raw_input('Enter the file path: ')
			upload(path);
		elif option == 5:
			return
		
if __name__ == '__main__':
	main()