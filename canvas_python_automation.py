#!usr/bin/python

#Google OAuth imports
#from __future__ import print_function
#from apiclient.discovery import build
#from httplib2 import Http
#from oauth2client import file, client, tools
#End of Google OAuth imports

import sys
import argparse
import requests
import json

students = list()

#Command Line Argument Handing
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help='subparsers')

#Create subparsers for different options.
assessment_parser = subparsers.add_parser('a', help='Retrieves assessment')
student_parser = subparsers.add_parser('s', help='Retrieves student')
assessment_parser.add_argument('-s', '--section',
                        type=int,
                        help='Returns all students within the given section')
#Assessment argument with rubric as child.
#parser.add_argument('-r', '--rubric')
parser.add_argument('-o', '--output', help='Output file', default="stdout")
parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Displays verbose output(default is stdout)')
args = parser.parse_args()

def main():
    if(args.section):
        get_students_in_section(args.section)
    #Reset list
    #get_rubric_marks(sydney_section_id, assessment_id)

def get_students_in_section(section_id):
    '''
    This is a docstring

    Arguments
    ---------
    section_id(int):
        section_id is used to filter the students by section
    
    Returns
    -------
    students(list):
        A list of student dictionarie that include studentID, name, etc.
    '''
    global students

    pagination_level = 200
    domain = 'https://coderacademy.instructure.com'
    API_request = '/api/v1/courses/109/sections'
    payload = {'per_page':pagination_level, 
               'include[]': 'students'
              }
    headers = {'Authorization' : 'Bearer {Enter bearer here}'}
    print("Requesting {0} endpoint".format(domain + API_request))
    response = requests.get(
                            domain + API_request,
                            params=payload,
                            headers=headers
                           )
    #Converts the request into text format
    response = response.text
    #Converts the response text into JSON
    response = json.loads(response)
    #section is an dictionary that contains information about the section.
    #Contains a field for students
    for section in response:
        #filters the sections by name
        if section['id'] == section_id:
            #student is a dictionary of student data.
            for enrolled_student in section['students']:
                print(enrolled_student['name'])
                students.append(student(enrolled_student['id']))
    print("Found {0} students in section: {1}".format(len(students),
                                                      section_id))
    return students

def get_rubric_marks(section_id, assessment_id):
    assert(section_id.__class__ == str)
    assert(assessment_id.__class__ == str)

    pagination_level = 200
    domain = 'https://coderacademy.instructure.com'
    API_request ='/api/v1/sections/{0}/assignments/{1}/submissions'.format(section_id, assessment_id)
    payload = {'per_page':pagination_level, 
               'include[]': 'rubric_assessment'
              }
    headers = {}
    response = requests.get(
                            domain + API_request,
                            params=payload,
                            headers=headers
                           )
    #Converts the request into text format
    response = response.text
    #Converts the response text into JSON
    response = json.loads(response)
    #each_submission is a student assessment submission
    #For each level of JSON data you transverse you need to use the
    print("Displaying marks for assessment: {0}".format(assessment_id))
    global students
    for each_submission in response:
        current_student = None
        #Iterates over students and see if any match.
        if 'user_id' in each_submission:
            for each_student in students:
                #If the student_id of the student matches this submission
                if each_student.student_id == each_submission['user_id']:
                    current_student = each_student
        if 'rubric_assessment' in each_submission:
            for outcome in each_submission['rubric_assessment']:
                '''
                Attaches a learning outcome to a student Object and sets the
                value to 'None' if an existing value is not present. 
                '''
                current_student.add_learning_outcome(outcome)
                current_student.set_grades(outcome,
                                           each_submission['rubric_assessment'][outcome]['points'])



    for i in students:
        print(i.student_id)
        print(i.grades)
    '''
    values = ""
    body = {
        'values': values
    }
    
    #value_range_body =json.loads(value_range_body)
    service = get_credentials()
    # Call the Sheets API
    SPREADSHEET_ID = ""
    RANGE_NAME = 'Sydney_Marks'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    
    request = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID,
                                     range=RANGE_NAME,
                                     valueInputOption="RAW", 
                                     body=body)
    response = request.execute()
    '''

def get_credentials():
    '''
    Returns the credentials for use with a google spreadsheet API.
    Returns
    -------
        service:
            The service to be used with the API
    '''
    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service

'''

Arguments
    ---------
        spreadsheet_id:
            The spreadsheet that will be used for the service.
        sheet_range:
            The specified cell ranges for use with the service.
'''

class student:
    def __init__(self, student_id):
        self.student_id = student_id
        self.grades = dict()
    def add_learning_outcome(self, learning_outcome_id):
        if self.grades.has_key(learning_outcome_id) == False:
            self.grades[learning_outcome_id] = ""
        else:
            print("""Learning outcome already exists in this student instance. The
                  existing value will remain. You will need to manually set the
                  grade for this student to 'None'""")
    def set_grades(self, learning_outcome_id, grade):
        self.grades[learning_outcome_id] = grade

if __name__ == "__main__":
    main()
else:
    print("This class is imported")
