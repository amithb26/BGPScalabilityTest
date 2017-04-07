*** Settings ***

Documentation     A test suite with tests to configure BGP.

Resource          Resource.robot

Suite Setup       setupActions 
            

*** Test Cases ***

BGP Setup
	
	Set all the required parameters for BGP configuration
	Set all the peer details and load it into json file
	Create BGP Neighbor for DUT


BGP Validation
        
	Check if BGP neighbors are set
	
