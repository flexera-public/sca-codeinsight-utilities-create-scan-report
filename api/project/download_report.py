'''
Copyright 2023 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Thu Nov 09 2023
File : download_report.py
'''

import logging
import requests
import time

logger = logging.getLogger(__name__)

#--------------------------------------------------
def download_report(projectID,  reportID, taskID, codeInsightURL, authToken):

    apiEndPoint = codeInsightURL + "/codeinsight/api/projects"
    apiEndPoint += "/" + str(projectID)
    apiEndPoint += "/reports/" + str(reportID)
    apiEndPoint += "/download?taskId=" + str(taskID)
  
    logger.debug("    apiEndPoint: %s" %apiEndPoint)
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + authToken} 
    
    #  Make the request to get the required data   
    try:
        response = requests.get(apiEndPoint, headers=headers)
    except requests.exceptions.RequestException as error:  # Just catch all errors
        logger.error(error)
        return

    ###############################################################################
    # We at least received a response from Code Insight so check the status to see
    # what happened if there was an error or the expected data

    while response.status_code == 202:
        logger.info("Report generation in process")
        time.sleep(5)
        response = requests.get(apiEndPoint, headers=headers)     

    if response.status_code == 200:
        # The report has completed
        reportZipFile = response.content        
        return reportZipFile

    else:
        logger.error(response.text)
        return 
