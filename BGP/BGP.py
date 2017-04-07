import pexpect
import time
from Buffer import flushBuffer
from GetData import getData
from Execute import Execute
from PutData import putData
import ipaddress



def getRouterIDList(RouterIDNetwork):

	
	RouterIDList = [0]
	IDs = ipaddress.ip_network(RouterIDNetwork,strict=False)
	data = getData('variable.json')
	Number_of_instances = data["number_of_instances"]
	for i in IDs.hosts():
		if Number_of_instances > 0:
			RouterIDList.append(str(i))
			Number_of_instances = Number_of_instances -1
		else:
			break
	return RouterIDList

	
def getASNumList(AS_Start):

	ASNumList = [0]
	data = getData('variable.json')
	Number_of_instances = data["number_of_instances"]
	count = Number_of_instances // 2 
	for i in range(1,(Number_of_instances+1)):
	#	if i <= count:
			ASNumList.append(AS_Start)
	#	else : 
	#		ASNumList.append(AS_Start + 1)
	return ASNumList
		
		
def getPeerDetails(Router):

	vardata = getData('variable.json')
	Number_of_instances = vardata["number_of_instances"]
	
	start = 'Router1'
	end = 'Router%d' %(Number_of_instances)
	data = getData('ProtocolSpecific.json')
	topodata = getData('Topology.json')
	data["BGP_Parameters"][Router].update({"PeerDetails" : {}})
	
	if Router == start:
		
		NDUT = 'Router2'
		PeerASNum = data["BGP_Parameters"][NDUT]["ASNum"]
		PeerAddress = topodata["Device_details"][NDUT]["IP_address"]
		PeerInterface = topodata["Device_details"][NDUT]["Interface"]
		data["BGP_Parameters"][Router]['PeerDetails'].update({"Peer1":{"ASNum" : PeerASNum, "IP_Address" : PeerAddress, "Interface" : PeerInterface}})
		putData(data,'ProtocolSpecific.json')

	elif Router == end:
		
		NDUT = 'Router%d' % (Number_of_instances-1)
		PeerASNum = data["BGP_Parameters"][NDUT]["ASNum"]
		PeerAddress = topodata["Device_details"][NDUT]["IP_address"]
		PeerInterface = topodata["Device_details"][NDUT]["Interface"]
		data["BGP_Parameters"][Router]['PeerDetails'].update({"Peer1":{"ASNum" : PeerASNum, "IP_Address" : PeerAddress, "Interface" : PeerInterface}})
		putData(data,'ProtocolSpecific.json')

	else:

		devno = int(Router[6:])
		Peers = ['Router'+str(devno-1),'Router'+str(devno+1)] 
		count = 1
		dictionary = {}

		for i in Peers:
			NDUT = i
			PeerASNum = data["BGP_Parameters"][NDUT]["ASNum"]
			PeerAddress = topodata["Device_details"][NDUT]["IP_address"]	
			PeerInterface = topodata["Device_details"][NDUT]["Interface"]
			data["BGP_Parameters"][Router]['PeerDetails'].update({"Peer"+str(count) : {"ASNum" : PeerASNum, "IP_Address" : PeerAddress, "Interface" : PeerInterface}})
			count = count+1 
		putData(data,'ProtocolSpecific.json')
		return	

	
def switchToDUT(child,RouterInst):
		
		flushBuffer(1,child)
		child.sendcontrol('m')
		child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=3)
		cmd = """sudo docker exec -it %s bash""" %(RouterInst)
		child.sendline(cmd)
		child.expect(['\d+',pexpect.EOF,pexpect.TIMEOUT],timeout=5)
		print child.before
		return child

#BGP requires a local AS Number and a Router ID to enable globally. Once these two items are assigned, BGP will be globally enabled on FlexSwitch				
	#Perform Global BGP configuration
	#ASNum - This will take unique Autonomous System Number.
	#RouterId - Router id key.
	#Example:AS_Num = 500, RouterId = 10.1.1.1
	
def BGPglobal(child,AS_Num,RouterId):

	exe = Execute()
	config = """curl -X PATCH "Content-Type: application/json" -d '{"ASNum":"%s","RouterId":"%s"}' http://localhost:8080/public/v1/config/BGPGlobal""" % (AS_Num, RouterId)
	exe.executeCmd(child,config)
	print "Global BGP Configuration Done"
	return child

#BGP requires established peering relationships to exchange routing information. This method will assist in setting up a BGP peer with another device.
#Setup BGP neighbors

def createBGPV4Neighbor(child,IntfRef,NeighborAddress,BfdEnable=False,PeerGroup='',MultiHopTTL=0,LocalAS='',KeepaliveTime=0,AddPathsRx=False,UpdateSource='',RouteReflectorClient=False,MaxPrefixesRestartTimer=0,Description='',MultiHopEnable=False,AuthPassword='',RouteReflectorClusterId=0,AdjRIBOutFilter='',MaxPrefixesDisconnect=False,PeerAS='',AddPathsMaxTx=0,AdjRIBInFilter='',MaxPrefixes=0,MaxPrefixesThresholdPct=80,BfdSessionParam='default',NextHopSelf=False,Disabled=False,HoldTime=0,ConnectRetryTime=0):
	exe = Execute()
	config = """curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{"PeerAS":"%s", "NeighborAddress":"%s", "IfIndex":0,"RouteReflectorClusterId":0, "MultiHopTTL":0,"ConnectRetryTime":60,"HoldTime":180,"KeepaliveTime":60,"AddPathsMaxTx":0}' 'http://localhost:8080/public/v1/config/BGPv4Neighbor'""" %(PeerAS,NeighborAddress)
	print 'command sent'
	exe.executeCmd(child,config)
	return child

#Check all bgp neighbors for the given router.

def checkAllBGPNeighbors(child):
	exe = Execute()
	config = """curl -H "Accept: application/json" "http://localhost:8080/public/v1/state/BGPv4Neighbors" | python -m json.tool"""
	exe.executeCmd(child,config)
	print "BGP neighbor set "
	return child

def checkIPV4Route(child):
	exe = Execute()
	config = """curl  -H "Accept: application/json" "http://localhost:8080/public/v1/state/IPv4Routes" | python -m json.tool"""
	Execute.executeCmd(child,config)
	print "Route Set in IPv4 table"
	return

def checkBGPRoute(child):
	exe = Execute()
	config = """curl -i -H "Content-Type: application/json" "http://localhost:8080/public/v1/state/BGPv4Routes"""
	exe.executeCmd(child,config)
	print " BGP Route Set in routing table"
	return











	
 
