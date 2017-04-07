*** Settings ***

Documentation     Resource file containing all the PYTHON API implementations.
Library           Setup.py
Library		  BGPSetup.py

*** Keywords ***


setupActions

	Building Network Topology with specified number of devices 
	Get IPaddress List that should be assigned to DUT interfaces for a given network
	Set Topology file with all device details
	Configure IPaddress on DUT 

Building Network Topology with specified number of devices 

	Log To Console    Building Network Topology	
	${interface_list}=    Run Keyword and Continue On Failure     buildNetworkTopology   
	Set Suite Variable    ${interface_list}   

Get IPaddress List that should be assigned to DUT interfaces for a given network

	Log To Console    Get IPaddress List that should be assigned to DUT interfaces for a given network   
	${IPaddList}=    Run Keyword and Continue On Failure     getIPaddressList    	
	Set Suite Variable    ${IPaddList}   

Set Topology file with all device details

	Log To Console    Set Topology file that should be accessed to set configure devices  
	Run Keyword and Continue On Failure     setTopologyFile    ${interface_list}    ${IPaddList}


Configure IPaddress on DUT 

	Log To Console    Configure IPaddress on DUT
	Run Keyword and Continue On Failure     configureIPaddress     

Set all the required parameters for BGP configuration

	Log To Console    Setting BGP parameters
	Run Keyword and Continue On Failure     setBGPParameters

Set all the peer details and load it into json file
	
	Log To Console    Set BGP peer details 
	Run Keyword and Continue On Failure     setPeerDetails

Create BGP Neighbor for DUT

	Log To Console    creating BGPV4 neighbors
        Run Keyword and Continue On Failure     createBGPNeighbor    all

Check if BGP neighbors are set

	Log To Console    Checking if BGPV4 neighbors are set
	Run Keyword and Continue On Failure     checkBGPNeighbors    all
         

						
