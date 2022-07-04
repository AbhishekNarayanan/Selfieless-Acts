from flask import Flask
import pymysql
import re
from flask import jsonify
from flask import flash, request
from werkzeug import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import binascii
import base64
import requests
from json import dumps
from flask import make_response
app = Flask(__name__)
import os
import sys
import traceback
from threading import RLock
total_number_of_requests=0
crashed = False
lock_request=RLock()
lock_crash=RLock()
@app.route('/api/v1/categories', methods=['POST'], endpoint='addnew_category')
def addnew_category():
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	cursor=None
	conn=None
	try:
		#print("hello")
		json = request.data.decode("UTF-8")
		#print(json)
		categoryName = json[json.find('"')+1:json.rfind('"')]
		#print(categoryName)
		# validate the received values
		if request.method == 'POST':
			if categoryName:
				# save edits
				conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
				cursor = conn.cursor()
				cursor.execute("SELECT * FROM categories WHERE categoryName=%s", (categoryName))
				conn.commit()
				cursor.fetchall()
				number_of_rows=cursor.rowcount
				if number_of_rows>0:
					return bad_request()
				sql = "INSERT INTO categories(categoryName) VALUES(%s)"
				data = (categoryName)
				
				cursor.execute(sql, data)
				conn.commit()
				cursor.close() 
				conn.close()
				message = {
            		'status': 201,
            		'message':'Created',
   				}
				resp = jsonify(message)
				resp.status_code = 201
				return resp
			else:
				return bad_request()
		else:
			return wrong_method()
	except Exception as e:
		return bad_request()

		

@app.route('/api/v1/categories/<categoryName>', methods=['DELETE'], endpoint='delete_a_category')
def delete_a_category(categoryName):
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	if request.method == 'DELETE':
		try:
			conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM categories WHERE categoryName=%s", (categoryName))
			conn.commit()
			cursor.fetchall()
			number_of_rows=cursor.rowcount
			if(number_of_rows==0):
				return bad_request()
			cursor.execute("DELETE FROM categories WHERE categoryName=%s", (categoryName))
			conn.commit()
			cursor.close()
			conn.close()
			message = {
            	'status': 200,
            	'message':'OK',
   			}
			resp = jsonify(message)
			resp.status_code = 200
			return resp
		except Exception as e:
			return bad_request()			
	else:
		return wrong_method()

@app.route('/api/v1/categories', methods=['GET'], endpoint='view_category')
def view_category():
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	if request.method == 'GET':
			conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
			cursor = conn.cursor()
			cursor.execute("SELECT DISTINCT categoryName FROM categories")
			conn.commit()
			rows_n = cursor.fetchall()
			if len(rows_n)==0:
				message = {
            		'status': 204,
            		'message':'No Content',
   				}
				resp = jsonify(message)
				resp.status_code = 204
				return resp
			dic={}
			for row in rows_n:
				dic[row[0]]=0
			
			cursor.execute("SELECT DISTINCT category, count(category) FROM acts GROUP BY category")
			conn.commit()
			rows = cursor.fetchall()			
			for row in rows:
				dic[row[0]]=row[1]
			resp=jsonify(dic)
			resp.status_code=200
			return resp
	else:
		return wrong_method()

@app.route('/api/v1/categories/<categoryName>/acts/size', methods=['GET'], endpoint='listno_acts')
def listno_acts(categoryName):
    lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
    if request.method == 'GET':
        try:
            conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE categoryName=%s", (categoryName))
            conn.commit()
            cursor.fetchall()
            number_of_rows=cursor.rowcount
            if number_of_rows==0:
            	message = {
            		'status': 204,
            		'message':'No Content'
            		}
            	resp=jsonify(message)
            	resp.status_code=204
            	return resp
            cursor.execute("SELECT DISTINCT actId,count(actId)  FROM acts WHERE category=%s GROUP BY actId", (categoryName))
            conn.commit()
            cursor.fetchall()
            number_of_rows=cursor.rowcount
            #number_of_rows=10
            list1=[]
            list1.append(number_of_rows)
            resp=jsonify(list1)
            resp.status_code=200
            return resp
        except Exception as e:
            return bad_request()         
    else:
        wrong_method()


def list_one_act(categoryName):
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	try:
		conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM categories WHERE categoryName=%s", (categoryName))
		conn.commit()
		cursor.fetchall()
		number_of_rows=cursor.rowcount
		if number_of_rows==0:
			message = {
            		'status': 204,
            		'message':'No Content',
   				}
			resp=jsonify(message)
			resp.status_code=204
			return resp

		cursor.execute("SELECT COUNT(*) FROM acts WHERE category=%s", (categoryName))
		conn.commit()
		cursor.fetchall()
		number_of_rows=cursor.rowcount
		if number_of_rows>100:
			message = {
            		'status': 413,
            		'message':'Payload Too Large',
   				}
			resp=jsonify(message)
			resp.status_code=413
			return resp
		cursor.execute("SELECT actId,username,caption,timestamp,upvotes,image FROM acts WHERE category=%s", (categoryName))
		conn.commit()
		row_headers=[x[0] for x in cursor.description]
		rv = cursor.fetchall()
		json_data=[]
		for result in rv:
			json_data.append(dict(zip(row_headers,result)))
		if(json_data==[]):
			message = {
            		'status': 204,
            		'message':'No Content',
   				}
			resp=jsonify(message)
			resp.status_code=204
			return resp
		for i in json_data:
			f=open("/home/app/"+i['actId']+".txt","r")
			i['imgB64']=f.read()
			i.pop('image',None)
			f.close()

		resp=jsonify(json_data)
		resp.status_code=200
		return resp
	except Exception as e:
		return bad_request()
    

@app.route('/api/v1/categories/<categoryName>/acts', methods=['GET'], endpoint='listno_acts_range')
def listno_acts_range(categoryName):
    lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
    if request.method == 'GET':
        try:
            conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
            cursor = conn.cursor()
            start = request.args.get('start')
            end = request.args.get('end')
            cursor.execute("SELECT * FROM categories WHERE categoryName=%s", (categoryName))
            conn.commit()
            cursor.fetchall()
            number_of_rows=cursor.rowcount
		
            if number_of_rows==0:
            	message = {
            		'status': 204,
            		'message':'No Content'
            	}
            	resp=jsonify(message)
            	resp.status_code=204
            	return resp


            if(start and end):
            	if (start>end):
            		message={
            		"status" : 204,
            		"message" : "No Content"
            		}
            		resp=jsonify(message)
            		resp.status_code=204
            		return resp
            	cursor.execute("SELECT * FROM acts WHERE category=%s ORDER BY timestamp ", (categoryName))
            	conn.commit()
            	rv=cursor.fetchall()
            	number_of_rows=cursor.rowcount
            	if((int(end)-int(start)+1)>100):
            		message = {
            		'status': 413,
            		'message':'Payload Too Large'
            		}
            		resp=jsonify(message)
            		resp.status_code=413
            		return resp
            	row_headers=[x[0] for x in cursor.description]
            	json_data=[]
            	for result in rv:
            		json_data.append(dict(zip(row_headers,result)))
            	if(json_data==[]):
            		message = {
            		'status': 204,
            		'message':'No Content'
            		}
            		resp=jsonify(message)
            		resp.status_code=204
            		return resp
            	for i in range(int(start)-1,int(end)):
            		f=open("/home/app/"+json_data[i]['actId']+".txt","r")
            		json_data[i]['imgB64']=f.read()
            		json_data[i].pop('image',None)
            		f.close()
            	resp=jsonify(json_data[int(start)-1:int(end)])
            	resp.status_code=200
            	return resp
            else:
            	return list_one_act(categoryName)           
        except Exception as e:
            return bad_request()         
    else:
        wrong_method()

@app.route('/api/v1/acts', methods=['POST'], endpoint='upload_act')		
def upload_act():
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	try:
		lusers=requests.get('http://3.95.148.42/api/v1/users').text		
		json = request.get_json(force=True)
		name = json['username']
		actId = json["actId"]
		caption = json["caption"]
		category = json["categoryName"]
		time = json["timestamp"]
		image = json["imgB64"]
		print("1")
		try:
			upvotes=json["upvotes"]
			return bad_request()
		except Exception as e:
				
			if request.method == 'POST':
				conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
				cursor = conn.cursor()
				# to check if username exists
				if(lusers.find(name)==-1):
					return bad_request()
				print("2")
				# to check if timestamp is in the right format (DD-MM-YYYY:SS-MM-HH)
				if re.match("(0[1-9]|[1-2][0-9]|3[0-1])-(0[1-9]|1[0-2])-[0-9]{4}:[0-5][0-9]-[0-5][0-9]-(2[0-3]|[01][0-9])",time)==False:
					return bad_request()
				print("3")
				# to check if image is in base64 format
				if (isBase64(image) == False):
					return bad_request()
				print("4")
				# to check if category exists
				cursor.execute("SELECT * FROM categories WHERE categoryName=%s", (category))
				conn.commit()
				cursor.fetchall()
				number_of_rows=cursor.rowcount
				print("5")
				if number_of_rows==0:
					return bad_request()
					
				# to check if actId is not present already
				cursor.execute("SELECT * FROM acts WHERE actId=%s", (actId))
				conn.commit()
				cursor.fetchall()
				number_of_rows=cursor.rowcount
				print("6")
				if number_of_rows>0:
					return bad_request()
				# add act into database
				filename="/home/app/"+actId+".txt"
				f=open(filename,"w")
				f.write(image)
				f.close()
				print("7")
				cursor.execute("INSERT INTO acts(actId,username,category,caption,timestamp,upvotes,image) VALUES (%s,%s,%s,%s,%s,%s,%s)",(actId,name,category,caption,time,0,filename))
				conn.commit()
				cursor.close()
				conn.close()
				print("8")
				resp = jsonify('Created')
				resp.status_code = 201
				return resp
			else:
				return wrong_method()
	except Exception as e:
		return bad_request()

@app.route('/api/v1/acts/<actId>', methods=['DELETE'], endpoint='delete_act')
def delete_act(actId):
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	if request.method == 'DELETE':
		try:
			conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM acts WHERE actId=%s", (actId))
			conn.commit()
			cursor.fetchall()
			number_of_rows=cursor.rowcount
			if(number_of_rows==0):
				return bad_request()
			cursor.execute("DELETE FROM acts WHERE actId=%s", (actId))
			conn.commit()
			cursor.close()
			conn.close()
			message = {
            	'status': 200,
            	'message':'OK',
   			}
			resp = jsonify(message)
			resp.status_code = 200
			return resp
		except Exception as e:
			return bad_request()
	else:
		wrong_method()
@app.route('/api/v1/user/get_password/<username>', methods=['POST'], endpoint='get_password')
def get_password(username):
	if request.method == 'POST':
			conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
			cursor = conn.cursor()
			
			dic={}
			
			
			cursor.execute("SELECT username,password FROM test WHERE username=%s", (username))
			conn.commit()
			cursor.fetchall()
			number_of_rows=cursor.rowcount
			if(number_of_rows==0):
				resp=jsonify('wrong_password')
				resp.status_code=200
				return resp
			cursor.execute("SELECT username,password FROM test WHERE username=%s", (username))
			conn.commit()
			rows = cursor.fetchall()			
			for row in rows:
				dic[row[0]]=row[1]
			#print(dic)
			resp=jsonify(dic[username])
			resp.status_code=200
			return resp
	else:
		return wrong_method()


		
@app.route('/api/v1/acts/upvote',methods=['POST'], endpoint='upvote')
def upvote():
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	cursor=None
	conn=None
	if request.method == 'POST':	
		try:
			json = request.data.decode("UTF-8")
			#print(json)
			act = json[json.find('[')+1:json.rfind(']')]
			#print(act)
			conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM acts WHERE actId=%s", (act))
			conn.commit()
			cursor.fetchall()
			number_of_rows=cursor.rowcount
			if(number_of_rows==0):
				return bad_request()
			cursor.execute("UPDATE acts SET upvotes=upvotes+1 WHERE actId=%s", (act))
			conn.commit()
			message = {
            	'status': 200,
            	'message':'OK',
   			}
			resp = jsonify(message)
			resp.status_code = 200
			cursor.close() 
			conn.close()
			return resp
		except Exception as e:
			return bad_request()
	else:
		wrong_method()

def isBase64(sb):
	try:
		if type(sb) == str:
			# If there's any unicode here, an exception will be thrown and the function will return false
			sb_bytes = bytes(sb, 'ascii')
		elif type(sb) == bytes:
			sb_bytes = sb
		else:
			raise ValueError("Argument must be string or bytes")
		return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
	except Exception:
		return False

@app.route('/api/v1/acts/count', methods=['GET'],endpoint='count_acts')
def count_acts():
	lock_request.acquire()
	global total_number_of_requests
	total_number_of_requests+=1
	lock_request.release()
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	if request.method == 'GET':
			conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM acts")
			conn.commit()
			cursor.fetchall()
			number_of_rows=cursor.rowcount
			response_list=[]
			response_list.append(number_of_rows)
			resp=jsonify(response_list)
			resp.status_code=200
			return resp
	else:
		return wrong_method()	


@app.route('/api/v1/_count', methods=['GET'],endpoint='count_requests')
def count_requests():
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	lock_request.acquire()
	global total_number_of_requests
	response_count=[]
	response_count.append(total_number_of_requests)
	if(request.method=='GET'):
		return make_response(dumps(response_count)),200
	lock_request.release()
	else:
		return wrong_method()

@app.route('/api/v1/_count', methods=['DELETE'],endpoint='reset_count_requests')
def reset_count_requests():
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	lock_request.acquire()
	global total_number_of_requests
	if(request.method=='DELETE'):
		total_number_of_requests=0
		resp=jsonify("")
		resp.status_code=200
		return resp
	lock_request.release()
	else:
		return wrong_method()

@app.route('/api/v1/_health', methods=['GET'], endpoint='health_checkup')
def health_checkup():
	lock_crash.acquire()
	global crashed
	if(crashed==True):
		resp=jsonify("")
		resp.status_code=500
		return resp
	lock_crash.release()
	try:

		conn =pymysql.connect("mysql-server","root","secret","cc_selfielessacts")
		cursor = conn.cursor()
		print("3")
		cursor.execute("INSERT INTO acts(actId,username,category,caption,timestamp,upvotes,image) VALUES (%s,%s,%s,%s,%s,%s,%s)",("health_checkup","health_checkup","health_checkup","health_checkup","health_checkup",0,"health_checkup"))
		conn.commit()
		print("4")
		cursor.execute("SELECT * FROM categories WHERE categoryName=%s", ("health_checkup"))
		conn.commit()
		print("5")
		cursor.execute("DELETE FROM acts WHERE actId='health_checkup'")
		conn.commit()
		print("3")
		cursor.close()
		conn.close()
		resp=jsonify("")
		resp.status_code=200
		return resp

	except:
		resp=jsonify("")
		resp.status_code=500
		return resp



@app.route('/api/v1/_crash', methods=['POST'], endpoint='crash_apis')
def crash_apis():
	if(request.method=='POST'):
		lock_crash.acquire()
		global crashed
		crashed = True
		lock_crash.release()
		resp=jsonify("")
		resp.status_code=200
		return resp
	else:
		return wrong_method()

		

@app.errorhandler(405)
def wrong_method(error=None):
    message = {
            'status': 405,
            'message': 'Method Not Allowed',
    }
    resp = jsonify(message)
    resp.status_code = 405
    return resp

@app.errorhandler(400)
def bad_request(error=None):
    message = {
            'status': 400,
            'message': 'Bad Request',
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp
			
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=80)
