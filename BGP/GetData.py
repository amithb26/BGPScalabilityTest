import json
import yaml

def getData(filename):

	
   	with open(filename) as data_file:    
 		data = json.load(data_file)
   	return data



  


