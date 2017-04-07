import pexpect
import time
import BGP
from Buffer import flushBuffer
from GetData import getData
from Execute import Execute
from PutData import putData

class BGPSetup:

	def __init__(self):
		self.child = pexpect.spawn("/bin/bash")
		self.data = getData('variable.json')
		self.Number_of_instances = self.data["number_of_instances"]
		self.RouterIDNetwork = self.data["RouterIDNetwork"]
		self.AS_Start = self.data["AS_Start"]


	def setBGPParameters(self):
		
		DATA = {}
		DATA.update({'BGP_Parameters' : {}})
		GlobalAS = self.data["globalAS"]
		for i in range(1,(self.Number_of_instances+1)):
			Router = 'Router%d' %(i)
			RouterIDList = BGP.getRouterIDList(self.RouterIDNetwork)
			ASNumList = BGP.getASNumList(self.AS_Start)
			DATA['BGP_Parameters'].update({Router :{'GlobalAS' : GlobalAS,'RouterID' : RouterIDList[i],'ASNum' : ASNumList[i]}})
		putData(DATA,'ProtocolSpecific.json')
		return

	
	def setPeerDetails(self):

		for i in range(1,(self.Number_of_instances+1)):
			Router = 'Router%d' %(i)
			BGP.getPeerDetails(Router)
		return


	def enableBGPGlobal(self,Device):

		data = getData('ProtocolSpecific.json')
		GlobalAS = self.data["globalAS"]
		RouterID = data['BGP_Parameters'][Device]['RouterID']
		RouterInst = BGP.switchToRouter(self.child,Device)
		RouterInst = BGP.BGPglobal(RouterInst,GlobalAS,RouterID)
		return RouterInst


	def createBGPNeighbor(self,Router):

		data = getData('ProtocolSpecific.json')
		
		if (isinstance(Router,list)):

			for i in Router:
				print "Configuring BGP in %s" %(i)
				RouterInst = self.enableBGPGlobal(i)
				Peers = data["BGP_Parameters"][i]['PeerDetails']
				for peer in Peers.keys():
					PeerAS = data["BGP_Parameters"][i]['PeerDetails'][peer]['ASNum']
					PeerAddress = data["BGP_Parameters"][i]['PeerDetails'][peer]['IP_Address']
					RouterInst = BGP.createBGPV4Neighbor(RouterInst,PeerAS,PeerAddress)
					RouterInst.sendline('exit')
			print "BGP neighbors done in %s" %(i) 


		elif Router == 'all':

			for i in data['BGP_Parameters'].keys():
				print "Configuring BGP in %s" %(i)
				RouterInst = self.enableBGPGlobal(i)
				Peers = data["BGP_Parameters"][i]['PeerDetails']
				#print Peers.keys()
				for peer in Peers.keys():
					#print 
					PeerAS = str(data["BGP_Parameters"][i]['PeerDetails'][str(peer)]['ASNum'])
					PeerAddress = str(data["BGP_Parameters"][i]['PeerDetails'][str(peer)]['IP_Address'])
					NeighborAddress = PeerAddress.split('/')
					RouterInst = BGP.createBGPV4Neighbor(RouterInst,PeerAS,NeighborAddress[0])
				RouterInst.sendline('exit')
			print "BGP neighbor set in %s" %(i)
		return


	def checkBGPNeighbors(self,Router):

		if (isinstance(Router,list)):
			for i in Router:
				print "Checking if BGP neighbors are set in %s" %(i)
				RouterInst = self.enableBGPGlobal(i)
				RouterInst = BGP.checkAllBGPNeighbors(RouterInst)
				RouterInst.sendline('exit')
			print "Verification-BGPNeighbors----PASS in %s" %(i) 

		elif DUT == 'all':

			for i in data['BGP_Parameters'].keys():
				print "Checking if BGP neighbors are set in %s" %(i)
				RouterInst = self.enableBGPGlobal(i)
				RouterInst = BGP.checkAllBGPNeighbors(RouterInst)
				RouterInst.sendline('exit')
			print "Verification-BGPNeighbors----PASS in %s" %(i)
		return 

	 	
		


#obj = BGPSetup()
#obj = BGPSetup()
#obj.setBGPParameters()
#obj.setPeerDetails()
#obj.createBGPNeighbor('all')			

			


