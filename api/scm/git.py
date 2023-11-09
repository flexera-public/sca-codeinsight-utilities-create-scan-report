'''
Copyright 2023 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Mon Oct 30 2023
File : git.py
'''
import logging
import requests
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------------------#
def create_git_instance(projectID, repoDetails, baseURL, authToken):


    RESTAPI_BASEURL = baseURL + "/codeinsight/api/"
    ENDPOINT_URL = RESTAPI_BASEURL + "scmInstances/"
    RESTAPI_URL = ENDPOINT_URL + "Git?projectId=%s" %projectID
    logger.debug("    RESTAPI_URL: %s" %RESTAPI_URL)

    instanceDetails = str(repoDetails).replace("'", '"')
   
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + authToken}     
       
    ##########################################################################   
    # Make the REST API call with the project data           
    try:
        response = requests.post(RESTAPI_URL, headers=headers, data=instanceDetails)
    except requests.exceptions.RequestException as error:  # Just catch all errors
        logger.error(error)
        return {"error" : error}

    ###############################################################################
    # We at least received a response from so check the status to see
    # what happened if there was an error or the expected data
    if response.status_code == 201:
        logger.debug("Git Instance was successfully created.")
        return response.json()
    else: 
        logger.error("Response code %s - %s" %(response.status_code, response.text))
        return {"error" : response.text}
    


#----------------------------------------------------------------------#    
