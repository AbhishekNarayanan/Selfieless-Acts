from flask import Flask
import pymysql
import re
import datetime
from flask import jsonify
from flask import flash, request
from werkzeug import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import binascii
import base64
import requests
from json import dumps
from flask import make_response
import os
import sys
import traceback
import glob
import uuid 
import json
images=glob.glob("selfielessacts/*")
encoded=[]
for img in images:
	with open(img, "rb") as image_file:
		print("encoding")
		encoded_string = base64.b64encode(image_file.read())
		encoded.append(encoded_string)
usernames=['Narayanan','Prasad','Abijna','Shivani']
username_index=0
categories=["Helping_the_Poor","Helping_Needy_Children","Care_for_Nature","Care_for_Elderly","Care_for_Animals"]
categories_index=0
i=0
response = requests.request(
        method='post',
        url='http://3.95.148.42/api/v1/users',
        data="{'username':'Narayanan','password':'ffffffffffffffffffffffffffffffffffffffff'}",
        allow_redirects=False)
print(response.status_code)

response = requests.request(
        method='post',
        url='http://3.95.148.42/api/v1/users',
        data="{'username':'Prasad','password':'ffffffffffffffffffffffffffffffffffffffff'}",
        allow_redirects=False)
print(response.status_code)

response = requests.request(
        method='post',
        url='http://3.95.148.42/api/v1/users',
        data="{'username':'Abijna','password':'ffffffffffffffffffffffffffffffffffffffff'}",
        allow_redirects=False)
print(response.status_code)

response = requests.request(
        method='post',
        url='http://3.95.148.42/api/v1/users',
        data="{'username':'Shivani','password':'ffffffffffffffffffffffffffffffffffffffff'}",
        allow_redirects=False)
print(response.status_code)
response = requests.request(
        method='post',
        url='http://107.20.84.57/api/v1/categories',
        data='["Helping_the_Poor"]',
        allow_redirects=False)
print(response.status_code)

response = requests.request(
        method='post',
        url='http://107.20.84.57/api/v1/categories',
        data='["Helping_Needy_Children"]',
        allow_redirects=False)
print(response.status_code)


print(response.status_code)

response = requests.request(
        method='post',
        url='http://107.20.84.57/api/v1/categories',
        data='["Care_for_Elderly"]',
        allow_redirects=False)
print(response.status_code)

response = requests.request(
        method='post',
        url='http://107.20.84.57/api/v1/categories',
        data='["Care_for_Animals"]',
        allow_redirects=False)
print(response.status_code)

response = requests.request(
        method='post',
        url='http://107.20.84.57/api/v1/categories',
        data='["Care_for_Nature"]',
        allow_redirects=False)
print(response.status_code)
c=1
caption_index=1
for img in encoded:
	d={}
	now = datetime.datetime.now()
	d['username']=usernames[username_index]
	d['timestamp']=now.strftime('%d-%m-%Y:%S-%M-%H') 
	print(d['timestamp'])
	d['caption']=categories[categories_index]+str(caption_index)
	d['categoryName']=categories[categories_index]
	categories_index=(categories_index+1)%5
	caption_index=caption_index+1
	username_index=(username_index+1)%4
	d['imgB64']=img.decode('utf-8')
	d['actId']= str(uuid.uuid4())
	response = requests.request(
	   method='post',
	   url='http://Load-Balancer-1712257144.us-east-1.elb.amazonaws.com/api/v1/acts',
	   data=json.dumps(d),allow_redirects=False)
	print(re.match("(0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-[0-9]{4}:[0-5][0-9]-[0-5][0-9]-(2[0-3]|[01][0-9])",d['timestamp']))
	print(c)
	c+=1


