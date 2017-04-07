import pexpect
import time
import basic_conf
from Buffer import flushBuffer
from GetData import getData
from Execute import Execute
from PutData import putData
from docker_startup import dockerStartup

class Setup:

	def __init__(self):
		self.child = pexpect.spawn("/bin/bash")
		self.data = getData('variable.json')
		self.Number_of_instances = self.data["number_of_instances"]
		self.Network = self.data["Network"]
	
	def buildNetworkTopology(self):

		InterfaceList = dockerStartup()
		print InterfaceList
		return InterfaceList


	def getIPaddressList(self):

		IPaddressList = basic_conf.getIPaddList(self.Network)
		print IPaddressList
		return IPaddressList

	def setTopologyFile(self,InterfaceList,IPaddressList):

		subnet = str(self.Network[-3:])
		DATA = {}
		DATA.update({'Device_details' : {}})
		for i in range(1,(self.Number_of_instances+1)):
			Router = 'Router%d' %(i)
			DATA['Device_details'].update({Router : {"Interface" : InterfaceList[i], "IP_address" :IPaddressList[i]+subnet}})
		putData(DATA,'Topology.json')
		print DATA
		return		

	def configureIPaddress(self):
		
		data = getData('Topology.json')
		Devices = data['Device_details']
		for Device in Devices.keys():
			print "***  Device_Name = %s  ***" %(Device)
			print "***  Setting up initial configurations in docker instance -- %s  ***" %(Device)
			RouterInst = basic_conf.switchToRouter(self.child,Device)
 			RouterInst = basic_conf.preliminaryInstalls(RouterInst)
			RouterInst = basic_conf.configureIP(RouterInst,data['Device_details'][Device]['Interface'],data['Device_details'][Device]['IP_address'])
			RouterInst.sendline('exit')
			self.child.expect(['/w+@.*/#',pexpect.EOF,pexpect.TIMEOUT],timeout=10)
			print self.child.before
			print "*** IP address for %s interface of device %s is set ***" %(data['Device_details'][Device]['Interface'],Device)
		print "*****  Initial Setup to start with flexswitch is ready  *****"
		return 


