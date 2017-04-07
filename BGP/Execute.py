import pexpect
import time
from Buffer import flushBuffer

class Execute:

	# This method will execute the single or set of curl commands to perform necessary configuration or to grab any data.
	# At the same time it will also check the status of result.
	# If pass, it continues with next operation to be performed and if error, resolves the error and continues with the execution

	count = 5
	def executeCmd(self,child,cmds):
		flushBuffer(1,child)
		child.sendcontrol('m')
		child.sendline(cmds)
		flag = child.expect(['/w+@.*/#','\"Result\"\:\"Success\"','Failed to connect to localhost port 8080','system not ready','Internal error processing CreateBGPv4Neighbor\:', pexpect.EOF, pexpect.TIMEOUT],timeout=8)
		print child.before
		
		if flag == 0 or flag == 1 : 
			print "Result=Success"
			
		elif flag == 2:

			print "ERROR:Failed to connect to localhost port 8080"
			while count > 0:
				self.count = self.count -1
				self.restartSwitch(child)
				self.execCmd(child,cmds)
				
			raise RuntimeError('Unable to boot the flexswitch')
			

		elif flag == 3:
			print "ERROR:System not ready,Daemons still restarting"
			time.sleep(20)
			self.execCmd(child,cmds)

		elif flag == 4:
			print "Configurations not done properly"

		
		return




	def restartSwitch(self,child):
		
		child.sendline('service flexswitch restart')
		time.sleep(35)
		child.sendcontrol('m')
		child.sendcontrol('m')
		return


	







