import pexpect
import time
import json
import re
from Buffer import flushBuffer
import basic_conf


#This method performs the following:
#	Pulls the latest flexswitch image from docker hub
#	Instantiate docker container as many required, on specified interfaces
	
def dockerStartup():

	with open('variable.json') as data_file:    
 			data = json.load(data_file)				#Get the json data from file "variable.json"
	Number_of_instances = data["number_of_instances"]
	child = pexpect.spawn("/bin/bash")					#Spawn the process ("/bin/bash")- Terminal
	print "*****   BUILDING THE NETWORK TOPOLOGY    *******"
	print "*****   PULL THE FLEXSWITCH BASE IMAGE   *******"
	child.expect(['/$',pexpect.EOF,pexpect.TIMEOUT],timeout=1)
	child.sendline('sudo docker pull snapos/flex:flex2')			#Pull the flexswitch image from docker hub
	child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=10)
	child.expect(['/$',pexpect.EOF,pexpect.TIMEOUT],timeout=5)
	child.sendline("mkdir -m 777 -p /var/run/netns")			#Create a directory
	child.expect(['netns',pexpect.EOF,pexpect.TIMEOUT],timeout=5)
	print child.before
	print "*****     SPAWN %s DOCKER INSTANCES          *******" %(Number_of_instances)
	RouterPid = [0]
	InterfaceList = [0]
	
	for i in range(1,(Number_of_instances+1)):				#Iterating, to create specified number of instances
			
		print "*****    CREATING INSTANCE Router%d          *******" %(i)
		Nid = createNodes(i,child)
		RouterPid.append(Nid)
		InterfaceList = addLinks(i,child,RouterPid,InterfaceList)
		bootUpDevices(i,child)
		print "*****    INSTANCE Router%d CREATED           *******" %(i) 

	return InterfaceList

def createNodes(iterator,child):

	i = iterator
	flushBuffer(1,child)
	child.sendcontrol('m')		
	child.expect(['/#',pexpect.EOF,pexpect.TIMEOUT],timeout=1)
	cmd = """sudo docker run -dt --privileged --log-driver=syslog --cap-add=ALL  --name Router%d -P snapos/flex:flex2""" %(i)	
	child.sendline(cmd)
	child.expect(['/d+',pexpect.EOF,pexpect.TIMEOUT],timeout=5)
	print child.before
	flushBuffer(1,child)
	child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=1)
	cmd1 = """sudo docker inspect -f '{{.State.Pid}}' Router%d""" %(i)
	child.sendline(cmd1)
	child.expect(['/d+',pexpect.EOF,pexpect.TIMEOUT],timeout=8)
	print child.before
	output = child.before
	pid = re.search('(\d\d[\d$]+)\s',output)
	count = 3		
	while count > 0:
		if pid:
			print "PID assigned(Container created for Router%d)" %(i)
			print "PID = %s" %(pid.group(1)) 
			return pid.group(1)
			break

		else:
			createNodes(iterator,child)
			count = count - 1 	
		raise RuntimeError("Some error : Unable to instantiate container:-Please manually check for errors")

def addLinks(iterator,child,RouterPid,InterfaceList):
	
	i = iterator
	flushBuffer(1,child)
	intfs = 'eth%d' %i

	InterfaceList.append(intfs)
	child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=1)
	cmd2 = """ln -s /proc/%s/ns/net /var/run/netns/%s""" %(RouterPid[i],RouterPid[i])
	child.sendline(cmd2)
	cmd3 = """sudo ip link add eth%d type veth peer eth%d
	sudo ip link set %s netns %s
	sudo ip netns exec %s ip link set %s up""" %(i,i+1,intfs,RouterPid[i],RouterPid[i],intfs)
	child.sendline(cmd3)
	child.expect(['w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=8)
	print child.before
	output = child.before
	status = re.search('Cannot find device',output)
	count = 3
		
	while count > 0:		
		if status:
			addLinks(i,child,RouterPid)
			count = count-1
		else:
			print "Links added"
			return InterfaceList
			break
		raise RuntimeError("Some error : Unable to add links")
	
	return InterfaceList

def bootUpDevices(iterator,child):
	
	i = iterator
	flushBuffer(1,child)
	child.sendcontrol('m')	
	print "STARTING FLEXSWITCH TO PICK UP THE INTERFACES"
	print "##############################"
	print "#######Router%d FS restart######" %(i)
	print "##############################"
	child.expect(['/#',pexpect.EOF,pexpect.TIMEOUT],timeout=8)
	cmd4 = """sudo docker exec Router%d sh -c "/etc/init.d/flexswitch restart" """ %(i)
	child.sendline(cmd4)
	time.sleep(10)
	child.expect(['IOError:',pexpect.EOF,pexpect.TIMEOUT],timeout=8)
	print child.before	
	return
			

#obj = dockerStartup()
