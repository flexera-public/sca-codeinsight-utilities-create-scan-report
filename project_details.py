'''
Copyright 2023 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Nov 08 2023
File : project_details.py
'''
import os
#------------------------------------------------------
def populate_project_details():

    projects = {}  # To store details about created projects
    
    #----------------
    projectName = "Example Project"
    projects[projectName] = {}
    projects[projectName]["folder"] = "Folder1/Folder2"
    #projects[projectName]["upload"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "archives", "ExampleCodeBase.zip")
    projects[projectName]["upload"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".", "ExampleCodeBase.zip")
    projects[projectName]["projectOptions"] = {}
    projects[projectName]["projectOptions"]["scanProfileName"] = "Basic Scan Profile (Without CL)"
    projects[projectName]["projectOptions"]["policyProfileName"] = "Default License Policy Profile"


    # #----An Example SCM Integration------------
    # projectName = "LMAX-Exchange"
    # projects[projectName] = {}
    # projects[projectName]["folder"] = "Java Example"
    # projects[projectName]["repo"] = {}
    # projects[projectName]["repo"]["url"] = "https://github.com/LMAX-Exchange/disruptor.git"
    # projects[projectName]["repo"]["tag"] = "4.0.0"
    # projects[projectName]["projectOptions"] = {}
    # projects[projectName]["projectOptions"]["scanProfileName"] = "Comprehensive Scan Profile"


    return projects
