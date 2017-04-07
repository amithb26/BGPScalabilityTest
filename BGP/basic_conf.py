import pexpect
import time
from Buffer import flushBuffer
from GetData import getData
from Execute import Execute
import re
import ipaddress
from PutData import putData


def getIPaddList(Network):
		IPaddList = [0]
		Hosts_IP = ipaddress.ip_network(Network,strict = False)
		data = getData('variable.json')
		Number_of_instances = data["number_of_instances"]
		for i in Hosts_IP.hosts():
			if Number_of_instances > 0:
				#print i
				IPaddList.append(str(i))
				Number_of_instances = Number_of_instances -1
			else:
				break
		return IPaddList


def switchToRouter(child,RouterInst):
		
		flushBuffer(1,child)
		child.sendcontrol('m')
		child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=3)
		cmd = """sudo docker exec -it %s bash""" %(RouterInst)
		child.sendline(cmd)
		child.expect(['\d+',pexpect.EOF,pexpect.TIMEOUT],timeout=5)
		print child.before
		return child

	
def preliminaryInstalls(child):

		flushBuffer(1,child)
		child.sendcontrol('m')
		child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=3)
		child.sendline("sudo apt-get update")
		time.sleep(15)
		child.sendline("sudo apt-get install curl -y")
		time.sleep(40)
		child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=5)
		print child.before
		return child		
				


def configureIP(RouterInst,Interface,IP_address):
	#This method will configure IP address
		flushBuffer(1,RouterInst)
		RouterInst.sendcontrol('m')
		RouterInst.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=3)
		config = """curl -H "Content-Type: application/json" -d '{"IpAddr": "%s", "IntfRef": "%s"}' http://localhost:8080/public/v1/config/IPv4Intf""" % (IP_address,Interface)
		Exe = Execute()
		Exe.executeCmd(RouterInst,config)
		return RouterInst
	
		
def getRouterIDList(RouterIDNetwork):
		RouterIDList = [0]
		IDs = ipaddress.ip_network(Network,strict=False)
		data = getData('variable.json')
		Number_of_instances = data["number_of_instances"]
		for i in IDs.hosts():
			if Number_of_instances > 0:
				RouterIDList.append(i)
				data = getData('variable.json')
				Number_of_instances = data["number_of_instances"]
				Number_of_instances = Number_of_instances -1
			else:
				break
		return RouterIDList



def getASNumList(AS_Start):
		ASNumList = [0]
		data = getData('variable.json')
		Number_of_instances = data["number_of_instances"]
		#count = Number_of_instances // 2 
		for i in range(1,(Number_of_instances+1)):
		#	if i <= count:
				ASNumList.append(AS_Start)
		#	else : 
		#		ASNumList.append(AS_Start + 1)
		return ASNumList		
		
def getPeerDetails(Router):
		data = getData('variable.json')
		Number_of_instances = data["number_of_instances"]
		PeerAS = []
		start = 'DUT1'
		end = 'DUT%d' %(Number_of_instances)
		data = getData('ProtocolSpecific.json')
		topodata = getData('topo.json')
		
		PeerDetails = {}
		data['BGP_Parameters'][0]['DUT1'].update({"PeerDetails" : []})
		

		if DUT == start:
			DUT = 'DUT2'
			PeerASNum = data["BGP_Parameters"][0][DUT]["ASNum"]
			PeerAddress = topodata["Device_details"][0][DUT]["IP_address"]
			PeerInterface = topodata["Device_details"][0][DUT]["Interface"]
			PeerDetails = {"Peer1":{"ASNum" : PeerASNum, "IP_Address" : PeerAddress, "Interface" : PeerInterface}} 
			data['BGP_Parameters'][0][DUT]['PeerDetails'].append(PeerDetails)
			putData(data,'ProtocolSpecific.json')

		elif DUT == end:
			DUT = 'DUT%d' % (Number_of_instances-1)
			PeerASNum = data["BGP_Parameters"][0][DUT]["ASNum"]
			PeerAddress = topodata["Device_details"][0][DUT]["IP_address"]
			PeerInterface = topodata["Device_details"][0][DUT]["Interface"]
			PeerDetails = {"Peer1":{"ASNum" : PeerASNum, "IP_Address" : PeerAddress, "Interface" : PeerInterface}} 
			data['BGP_Parameters'][0][DUT]['PeerDetails'].append(PeerDetails)
			putData(data,'ProtocolSpecific.json')
		else:

			devno = DUT[3:]
			Peers = ['DUT%d','DUT%d'] %(devno-1,devno+1)
			count = 1
			dictionary = {}
		
			for i in Peers:
				
				PeerASNum = data["BGP_Parameters"][0][i]["ASNum"]
				PeerAddress = topodata["Device_details"][0][i]["IP_address"]	
				PeerInterface = topodata["Device_details"][0][i]["Interface"]
				dictionary = {"Peer"+str(count) : {"ASNum" : PeerASNum, "IP_Address" : PeerAddress, "Interface" : PeerInterface}} 
				count = count+1 
				PeerDetails.update(dictionary)

			data['BGP_Parameters'][0][DUT]['PeerDetails'].append(PeerDetails)
			putData(data,'ProtocolSpecific.json')
		return	


def checkInterface(RouterInst,Interface):
		flushBuffer(1,RouterInst)
		RouterInst.sendcontrol('m')
		#RouterInst.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=3)
		RouterInst.sendline("ifconfig")
		RouterInst.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=3)
		print child.before
		output = child.before
		status = re.search(Interface,output)
		if status = True:
			print "Interface %s of %s is up" %(Interface,RouterInst)
			return
		else:
			raise RuntimeError("Some error : Interface is not UP")
		
		
