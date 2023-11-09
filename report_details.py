'''
Copyright 2023 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Wed Nov 08 2023
File : report_details.py
'''
import api.reports.get_reports

#-----------------------------
def manage_reports(baseURL, authToken):
    reports = {}
    
    # reports["SBOM Report - HTML and Excel"] = {}
    # reports["SBOM Report - HTML and Excel"]["reportOptions"] = '''{"options": {"includeChildProjects": "true", "includeVulnerabilities": "true", "cvssVersion": "3.0"}}'''

    # reports["SBOM Report - SPDX"] = {}
    # reports["SBOM Report - SPDX"]["reportOptions"] = '''{"options":{"includeChildProjects": "true", "includeFileDetails": "True", "includeUnassociatedFiles": "false"}}'''
    
    reports["SBOM Report - CycloneDX"] = {}
    reports["SBOM Report - CycloneDX"]["reportOptions"] = '''{"options": {"includeChildProjects": "true", "includeVDRReport": "true", "includeVEXReport": "true"}}'''
    
    # reports["Third Party Notices Report"] = {}
    # reports["Third Party Notices Report"]["reportOptions"] = '''{"options": {"includeChildProjects": "true", "includeComponentVersions": "true"}}'''
    
    # reports["Project Inventory Report"] = {}
    # reports["Project Inventory Report"]["reportOptions"] = '''{"options": { "includeChildProjects": "true","includeComplianceInformation": "true", "maxVersionsBack": "10","cvssVersion": "3.0"}}'''
    
    # reports["Project Vulnerability Report"] = {}
    # reports["Project Vulnerability Report"]["reportOptions"] = '''{"options": {"includeChildProjects":"t", "cvssVersion":"3.0", "includeAssociatedFiles":"f"}}'''
    
    # reports["Third Party Evidence Report"] = {}
    # reports["Third Party Evidence Report"]["reportOptions"] = '''{}'''

    # reports["Project Task Report"] = {}
    # reports["Project Task Report"]["reportOptions"] = '''{"options": {"includeChildProjects":"t"}}'''

    # Get the report ID for each report and add to the report details
    for reportName in reports:

        reportInformation = api.reports.get_reports.get_all_currently_registered_reports_by_name(baseURL, authToken, reportName)
        reportID = str((reportInformation[0]["id"]))
        reports[reportName]["reportID"] = reportID

    return reports


 