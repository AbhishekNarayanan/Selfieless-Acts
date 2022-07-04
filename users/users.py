from flask import Flask
import pymysql
import re
from flask import jsonify
from flask import flash, request
from werkzeug import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import binascii
import base64
from json import dumps
from flask import make_response
app = Flask(__name__)
total_number_of_requests=0
@app.route('/api/v1/users', methods=['POST'], endpoint='add_user')
def add_user():
	global total_number_of_requests
	total_number_of_requests+=1
	cursor=None
	conn=None
	try:
		_json = request.get_json(force=True)
		name = _json['username']
		password = _json['password']
		# validate the received values
		conn = pymysql.connect("localhost","root","","cc_selfielessacts")
		cursor = conn.cursor()
		pattern = re.compile(r'\b[0-9a-f]{40}\b')
		sh1 = re.match(pattern, password)
		cursor.execute("SELECT * FROM test WHERE username=%s", (name))
		conn.commit()
		cursor.fetchall()
		number_of_rows=cursor.rowcount
		if(number_of_rows>0):		
			return bad_request()
		if request.method == 'POST':
			if name and password and len(password)==40 and sh1:
				sql = "INSERT INTO test(username,password) VALUES(%s, %s)"
				data = (name,password)
				conn = pymysql.connect("localhost","root","","cc_selfielessacts")
				cursor = conn.cursor()
				cursor.execute(sql, data)
				conn.commit()
				message = {
            		'status': 201,
            		'message':'Created',
   				}
				resp = jsonify(message)
				resp.status_code = 201
				cursor.close() 
				conn.close()
				return resp
			else:
				return bad_request()
		else:
			return wrong_method()
	except Exception as e:
		return bad_request()


@app.route('/api/v1/users/<username>', methods=['DELETE'],endpoint='delete_user')
def delete_user(username):
	global total_number_of_requests
	total_number_of_requests+=1
	cursor=None
	conn=None
	if request.method == 'DELETE':
		try:
			conn =pymysql.connect("localhost","root","","cc_selfielessacts")
			
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM test WHERE username=%s", (username))
			conn.commit()
			cursor.fetchall()
			number_of_rows=cursor.rowcount
			if(number_of_rows==0):
				return bad_request()
			cursor.execute("DELETE FROM test WHERE username=%s", (username))
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


@app.route('/api/v1/users', methods=['GET'],endpoint='list_users')
def list_users():
	global total_number_of_requests
	total_number_of_requests+=1
	if request.method == 'GET':
			conn = pymysql.connect("localhost","root","","cc_selfielessacts")
			cursor = conn.cursor()
			cursor.execute("SELECT DISTINCT username FROM test")
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
			lusers=[]
			
			cursor.execute("SELECT DISTINCT username FROM test")
			conn.commit()
			rows = cursor.fetchall()			
			for row in rows:
				lusers.append(row[0])
			resp=jsonify(lusers)
			resp.status_code=200
			return resp
	else:
		return wrong_method()

@app.route('/api/v1/_count', methods=['GET'],endpoint='count_requests')
def count_requests():
	global total_number_of_requests
	response_count=[]
	response_count.append(total_number_of_requests)
	if(request.method=='GET'):
		return make_response(dumps(response_count)),200

	else:
		return wrong_method()

@app.route('/api/v1/_count', methods=['DELETE'],endpoint='reset_count_requests')
def reset_count_requests():
	global total_number_of_requests
	if(request.method=='DELETE'):
		total_number_of_requests=0
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


