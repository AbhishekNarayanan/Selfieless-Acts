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
from threading import Lock, Thread, Event
import time
import docker
#from docker import Client
client = docker.from_env()
event = Event()
start_request_count=0
end_request_count=0
total_number_of_requests=0
result={}
from flask import Flask, render_template, request
app = Flask(__name__,template_folder='template')
#cli = Client(base_url='unix://var/run/docker.sock')
ip_of_acts_vm="107.20.84.57"
#"localhost"="ip_of_acts_vm"
#dummy ports for testing
active_ports=['8000']
total_number_of_requests=0 
start_timer=False
#below is the index of the cotainer port to which the next request has to be forwarded to
port_index=-1
lock = Lock()

def run_load_balancer():
    app.run(host='0.0.0.0',debug=True, port=80,use_reloader=False)

@app.route('/api/v1/<path:url>', methods=['POST','GET','DELETE'], endpoint='load_balancer')
def load_balancer(url):
  global total_number_of_requests
  total_number_of_requests+=1

  path_to_route=request.path
  global port_index
  global active_ports
  port_index=(port_index+1)%len(active_ports)

  response = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, "http://localhost"+":"+str(active_ports[port_index])+"/"),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        allow_redirects=False)
  #round robin scheduling
  return (response.text, response.status_code, response.headers.items())

def run_autoscaler():
	global total_number_of_requests
	global start_request_count
	global end_request_count
	event.wait() # Blocks until the flag becomes true.
	start=time.time()
	while(True):
		start_request_count=total_number_of_requests
		print(start_request_count)
		print(end_request_count)
		autoscale(start_request_count - end_request_count+1)
		time.sleep(int(result['T_monitor'])-(time.time()-start)%int(result['T_monitor']))
		end_request_count=start_request_count

def autoscale(number_of_requests):
	global result
	number_of_containers_needed=(number_of_requests//int(result['threshold_requests']))+1 if (number_of_requests//int(result['threshold_requests']))==0 else (number_of_requests//int(result['threshold_requests']))+int(result['scale_factor'])
	global active_ports
	global port_index
	start_port=8000
	needed_containers=[]
	for i in range(0,number_of_containers_needed):
		needed_containers.append(str(start_port))
		start_port+=1

	running=len(active_ports)
	print(running)
	print(number_of_containers_needed)
	if(running>number_of_containers_needed):
		print("Scale in")
		reverse_ports=active_ports[::-1]
		for i in reverse_ports:
			if(i not in needed_containers):
				container_list = client.containers.list()
				for j in container_list:
					if( j.attrs['Config']['Image']!='mysql' and j.attrs['HostConfig']['PortBindings']['80/tcp'][0]['HostPort']==i):
						container_id =j.attrs['Config']['Hostname']
						active_ports.remove(i)
						j.stop()
						print("Stopped container "+container_id)
						break
	if(running<number_of_containers_needed):
		print("Scale out")
		for i in needed_containers:
			if(i not in active_ports):
				new_container=client.containers.run(image='acts', detach=True,network="my-network",ports={"80/tcp":int(i)},volumes={'/home/ubuntu/':{'bind':'/home/app','mode':'rw'}})
				print("created container at port "+str(i))
				active_ports.append(str(i))

@app.route('/')
def display_form():
   return render_template('form.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
      global result
      result = request.form
      event.set()
      return render_template("result.html",result = result)


threads = []
for func in [run_load_balancer,run_autoscaler]:
   threads.append(Thread(target=func))
   threads[-1].start()

for thread in threads:
   thread.join()