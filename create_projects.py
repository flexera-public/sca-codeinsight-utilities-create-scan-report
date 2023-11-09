'''
Copyright 2023 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Mon Oct 30 2023
File : create_projects.py
'''
import os, logging, sys, json, time, io, zipfile
import api.folder.create_folder
import api.project.create_project
import api.project.get_project_id
import api.project.upload_project_codebase
import api.scm.git
import api.project.add_child_projects
import api.scan.project_scan
import api.jobs.status
import api.jobs.update_notices
import api.project.generate_report
import project_details
import report_details
import api.project.download_report


###################################################################################
# Test the version of python to make sure it's at least the version the script
# was tested on, otherwise there could be unexpected results
if sys.version_info < (3, 6):
    raise Exception("The current version of Python is less than 3.6 which is unsupported.\n Script created/tested against python version 3.6.8. ")
else:
    pass

logfileName = os.path.dirname(os.path.realpath(__file__)) + "/_create__projects.log"
propertiesFile = "server_properties.json"  # Created by installer or manually
propertiesFile =  os.path.dirname(os.path.realpath(__file__)) + "/" +  propertiesFile


###################################################################################
#  Set up logging handler to allow for different levels of logging to be capture
logging.basicConfig(format='%(asctime)s,%(msecs)-3d  %(levelname)-8s [%(filename)-30s:%(lineno)-4d]  %(message)s', datefmt='%Y-%m-%d:%H:%M:%S', filename=logfileName, filemode='w',level=logging.DEBUG)
logger = logging.getLogger(__name__)

logging.getLogger("urllib3").setLevel(logging.WARNING)  # Disable logging for requests module

#####################################################################################################
#  Code Insight System Information
#  Pull the base URL from the same file that the installer is creating
if os.path.exists(propertiesFile):
    try:
        file_ptr = open(propertiesFile, "r")
        configData = json.load(file_ptr)
        baseURL = configData["core.server.url"]
        authToken = configData["core.server.token"]
        file_ptr.close()
        logger.info("Using baseURL from properties file: %s" %propertiesFile)
    except:
        logger.error("Unable to open properties file: %s" %propertiesFile)
else:
    baseURL = "UPDATEME"   # Required if the core.server.properties file is not used
    authToken = "UPDATEME" # Required if the core.server.properties file is not used
    logger.info("Using baseURL and authToken from create_report.py")


scanProjects = True
updateNotices = True
generateReports = True
downloadReports = True

#----------------------------------------------------------------------#
def main():

    projects = project_details.populate_project_details()
    
    # Create projects and upload code
    for projectName in projects:
        parentFolderID = "1" # Just create in the base area for now
        print("\nManaging project %s" %projectName)
        # Create the project folder if required
        folderName = projects[projectName]["folder"]

        # See if there are potentially subfolders
        folders = folderName.split("/")
        if len(folders) > 1:
            for folder in folders:
                folderID = api.folder.create_folder.create_project_folder(baseURL, authToken, folder, parentFolderID)
                parentFolderID = str(folderID)
        else:
            folderID = api.folder.create_folder.create_project_folder(baseURL, authToken, folderName, parentFolderID)

        projectOptions = projects[projectName]["projectOptions"]
        projectOptions["folderId"] = str(folderID)     

        projectID = api.project.create_project.create_project(baseURL, authToken, projectName, projectOptions)

        # Was it an ID returned or an error message?
        if str(projectID).endswith("already exists."):
            projectID = api.project.get_project_id.get_projectID(baseURL, authToken, projectName)
            logger.debug("            Existing projectID %s:" %projectID)
            print("    Existing project found with an ID of %s" %(projectID))
            projects[projectName]['projectID'] = projectID
        else:
            print("    Project created with an ID of %s" %(projectID))
            projects[projectName]['projectID'] = projectID

            # Since the projct aleady exists we'll assume we don't need to manage the source
            if "upload" in projects[projectName]:
                archiveFile = projects[projectName]["upload"] 
                
                print("    Uploading %s" %archiveFile)
            
                # Upload a zip file to the server
                fileptr = open(archiveFile,"rb")
                zipFileContents = fileptr.read()
                fileptr.close()
                
                api.project.upload_project_codebase.upload_archive(projectID, zipFileContents, baseURL, authToken)
                logger.debug("Project zip file has been uploaded")
                print("    Project zip file has been uploaded")

            elif "repo" in projects[projectName]:
                repoDetails = projects[projectName]["repo"]

                print("    Configuring SCM details for repo %s" %repoDetails["url"])

                response = api.scm.git.create_git_instance(projectID, repoDetails, baseURL, authToken)

    #######################################################################################################
    # Now that all of the projects have been created configure the project hierarchy if needed

    print("\nManaging project hierarchy configuration for projects")
    for projectName in projects:
        
        if "parentProject" in projects[projectName]:
            childProjectID = projects[projectName]["projectID"]
            parentProjectName = projects[projectName]["parentProject"]
            parentProjectID = projects[parentProjectName]["projectID"]
            
            if api.project.add_child_projects.add_child_project(baseURL, authToken, parentProjectID, childProjectID):
                print("    Added %s as a child project to %s" %(projectName, parentProjectName))
            else:
                print("    Unable to add %s as a child project to %s" %(projectName, parentProjectName))


    if scanProjects:
        #######################################################################################################
        # Scan each project in order

        print("\nStarting project scans")
        
        for projectName in projects:
            print("    Starting scan for project %s" %projectName)
            projectID = projects[projectName]["projectID"]

            # Just start the scan and grab the corresponding ID to query prior to generating any reports
            # This allows other scans to start if the report generation could take time
            response = api.scan.project_scan.scan_project(projectID, baseURL, authToken)
            if type(response) != int:
                if "error" in response:
                    if "Error: " in response["error"]:
                        responseString = response["error"]
                        jobID = responseString.split("task ID: ")[1][:-2]
                        print("        Project %s is queued for scanning." %projectName, end = "", flush=True)
                    else:
                        print("Unknown issue")
                        sys.exit()
            else:
                jobID = response
                print("    Scanning project %s  " %projectName, end = "", flush=True)
            wait_for_job_to_complete(jobID, baseURL, authToken)
            print("\n        Project scan completed")

    #************************************************
    if updateNotices:

        #######################################################################################################
        # Now that all of the scans have completed generate the reports
        print("\nUpdating Project Notices Reports")
        for projectName in projects:
            projectID = projects[projectName]["projectID"]
            print("    Updating notices for project %s  " %projectName, end = "", flush=True)
            response = api.jobs.update_notices.update_project_notices(baseURL, authToken, projectID)
            jobID = response["message"].split(":")[1].strip()
            wait_for_job_to_complete(jobID, baseURL, authToken)
            print("\n        Notice update completed")

    #************************************************
    if generateReports:

        reports = report_details.manage_reports(baseURL, authToken)

        #######################################################################################################
        # Now that all of the scans have completed generate the reports
        print("\nGenerating Reports")
        for projectName in projects:
            projectID = projects[projectName]["projectID"]

            print("    Generating reports for project %s" %projectName)
            
            for report in reports:
                print("        %s" %report)
                reportID = reports[report]["reportID"]
                reportOptions = reports[report]["reportOptions"]
                
                print("            Report generation in process  ", end = "", flush=True)
                
                jobID = api.project.generate_report.generate_report(projectID, reportID, reportOptions, baseURL, authToken)
                
                while jobID == None:
                    jobID = api.project.generate_report.generate_report(projectID, reportID, reportOptions, baseURL, authToken)

                wait_for_job_to_complete(jobID, baseURL, authToken)
                print("\n                Report generation completed")

                if downloadReports:

                    # Download newly created report
                    reportZipFilename = "%s-%s.zip" %(projectName, report)
                    reportZipFilename = reportZipFilename.replace(" ", "-")
                    reportZipFileData = api.project.download_report.download_report(projectID, reportID, jobID, baseURL, authToken)  

                    # Write the report download zip file to memory
                    print("            Writing %s to drive" %reportZipFilename)
                    with open(reportZipFilename, "wb") as fp:
    
                        # Write bytes to file
                        fp.write(reportZipFileData)


#---------------------------------------
def wait_for_job_to_complete(jobID, baseURL, authToken):

    response = api.jobs.status.get_job_status(jobID, baseURL, authToken)

    while response["status"] != "Completed":
        for cursor in '\\|/-':
          time.sleep(1)
          # Use '\r' to move cursor back to line beginning
          # Or use '\b' to erase the last character
          sys.stdout.write('\b{}'.format(cursor))
          # Force Python to write data into terminal.
          sys.stdout.flush()
        response = api.jobs.status.get_job_status(jobID, baseURL, authToken)

    return response

#----------------------------------------------------------------------#    
if __name__ == "__main__":
    main()  