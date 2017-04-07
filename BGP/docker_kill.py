import pexpect
import time
import json
import os
from Buffer import flushBuffer
import re

def docker_kill():
	
	with open('variable.json') as data_file:    
 		data = json.load(data_file)
		
   	Number_of_instances = data["number_of_instances"]
	child = pexpect.spawn("/bin/bash")
	
	for i in range(1,(Number_of_instances+1)):
		flushBuffer(1,child)
		cmd = """sudo docker rm -f Router%d""" %(i)		
		child.sendline(cmd)
		child.expect(['/w+',pexpect.EOF,pexpect.TIMEOUT],timeout=1)
		print child.before


docker_kill()	

