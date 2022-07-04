#import required packages
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

#This function runs in a separate thread and loops through all active port numbers and polls containers running at these ports for health status
#if any container is found unhealthy, we crash the container and recreate a new one at the same port
def loop_health_check():
	global active_ports
	global port_index
	start=time.time()
	while(True):
		for port in active_ports:
			check_health(port)
		time.sleep(1)
		

#this function is a helper utility to perform the above mentioned task of health monitoring and fault tolerance
def check_health(port_no):
  response=requests.get('http://localhost:'+str(port_no)+"/api/v1/_health")
  print(response.status_code)
  if response.status_code == 500:
    # get list of containers
    check=0;
    container_list = client.containers.list()
    for i in container_list: 
        if(i.attrs['Config']['Image']!='mysql'):
            print(i.attrs['HostConfig']['PortBindings']['80/tcp'][0]['HostPort'])
        if( i.attrs['Config']['Image']!='mysql' and i.attrs['HostConfig']['PortBindings']['80/tcp'][0]['HostPort']==port_no):
          container_id =i.attrs['Config']['Hostname']
          print("Stopped container "+container_id)
          i.stop()
          new_container=client.containers.run(image='acts', detach=True,network="my-network",ports={"80/tcp":int(port_no)},volumes={'/home/ubuntu/':{'bind':'/home/app','mode':'rw'}})
          print("created container at "+str(port_no))
          break
  print("All Healthy!")      

#This function runs in a separate thread and faciliates interception of incoming requests and load balancing of requests to different containers in round robin way
def run_load_balancer():
    app.run(host='0.0.0.0',debug=True, port=80,use_reloader=False)

#this is the actual function utility for round robin load balancing
@app.route('/api/v1/<path:url>', methods=['POST','GET','DELETE'], endpoint='load_balancer')
def load_balancer(url):
  global total_number_of_requests
  total_number_of_requests+=1
  if(total_number_of_requests==1):
    print("Starting Autoscaling Timer")
    event.set()

  path_to_route=request.path
  global port_index
  global active_ports
  port_index=(port_index+1)%len(active_ports)
  #forward incoming request to next port to that on which previous request was routed
  response = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, "http://localhost"+":"+str(active_ports[port_index])+"/"),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        allow_redirects=False)
  #round robin scheduling
  return (response.text, response.status_code, response.headers.items())

#this function runs as a separate thread and faciitates autoscaling feature, which gets triggered when the load balancer receives the first request
def run_autoscaler():
	global total_number_of_requests
	global start_request_count
	global end_request_count
	event.wait() # Blocks until the flag becomes true.
	start=time.time()
	#monitor request count for threshold time
	while(True):
		start_request_count=total_number_of_requests
		print(start_request_count)
		print(end_request_count)
		autoscale(start_request_count - end_request_count+1)
		time.sleep(120.0-(time.time()-start)%120)
		end_request_count=start_request_count

#scale in or scale out based on number of requests in two minute intervals
def autoscale(number_of_requests):
	number_of_containers_needed=(number_of_requests//20)+1
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
		#if unnecessary containers are running
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
	#if less than required containers are running
	if(running<number_of_containers_needed):
		print("Scale out")
		for i in needed_containers:
			if(i not in active_ports):
				new_container=client.containers.run(image='acts', detach=True,network="my-network",ports={"80/tcp":int(i)},volumes={'/home/ubuntu/':{'bind':'/home/app','mode':'rw'}})
				print("created container at port "+str(i))
				active_ports.append(str(i))
			


#create and join all threads
threads = []
for func in [loop_health_check,run_load_balancer,run_autoscaler]:
   threads.append(Thread(target=func))
   threads[-1].start()

for thread in threads:
   thread.join()




