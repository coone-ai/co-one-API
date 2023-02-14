#################################################################
######### User-friendly file uploader script for Co-One #########
#################################################################

# Librarys

import os
import sys
import time
import json
import getpass
import requests
from math import fabs
from traceback import print_tb
from alive_progress import alive_bar

# Global variables
global loginSuccessful
loginSuccessful = False

global customerProjects
customerProjects = []

global customerProjectNames
customerProjectNames = []

global projectSelected
projectSelected = False

global selectedProjectID
selectedProjectID = ""

global selectedProjectName
selectedProjectName = ""

global loginEmail
loginEmail = ""
global loginPassword
loginPassword = ""
global authToken
authToken = ""

# ----------------------------- LOGIN ----------------------------

def login():
    global authToken
    global loginSuccessful
    global loginEmail
    global loginPassword
    global selectedProjectID
    global selectedProjectName
    global customerProjects
    global customerProjectNames

    if loginSuccessful:
      print("\n***** You are already logged in! ***** ")
      time.sleep(1)
      os.system("printf '\033c'")
      return False

    authToken = ""
    os.system("printf '\033c'")
    print("******** Login ******** ")
    loginEmail = input("Please enter your email for logining in to co-one: ")
    loginPassword = getpass.getpass('Please enter your password: ')
    print("\n--> Logging in to " + loginEmail, end="\r", flush=True)

    loginUrl = "https://us-central1-co-one-app-1252e.cloudfunctions.net/api/v1/auth/login"
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }

    loginEmail = loginEmail.lower()
    payload = "email=" + loginEmail + "&password=" + loginPassword

    r = requests.request("POST", loginUrl, headers=headers, data=payload)

    if r.status_code == 200:
      print("--> Login successful! Loading projects...")

      jsonFile= r
      jsonFile = json.loads(jsonFile.text)
      customerProjects = jsonFile['data']['projects']
      customerProjectNames = jsonFile['data']['projectNames']
      authToken = jsonFile['data']['token']

      loginSuccessful = True
      time.sleep(2)
      return True

    elif r.status_code == 404:
      print("--> Login failed, user not found: " + loginEmail)
      loginSuccessful = False
      input("Press Enter to try again...")
      login()

    elif r.status_code == 403:

      print("--> Login failed, free users cannot use API to upload files sorry!")
      loginSuccessful = False
      input("Press Enter to exit...")
      sys.exit()

    elif r.status_code == 206:

      print("--> Login failed, You have no projects, please create one before you upload!")
      loginSuccessful = False
      input("Press Enter to exit...")
      sys.exit()

    else:
      print("--> Login failed. Have you checked your email and password?")
      loginSuccessful = False
      input("Press Enter to continue...")
      return False

def renewLogin():
  global authToken
  global loginSuccessful
  global loginEmail
  global loginPassword

  loginUrl = "https://us-central1-co-one-app-1252e.cloudfunctions.net/api/v1/auth/login"
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }

  loginEmail = loginEmail.lower()
  payload = "email=" + loginEmail + "&password=" + loginPassword

  r = requests.request("POST", loginUrl, headers=headers, data=payload)

  if r.status_code == 200:

      jsonFile= r
      jsonFile = json.loads(jsonFile.text)
      authToken = jsonFile['data']['token']

      loginSuccessful = True
      time.sleep(2)
      return True
  else:
    loginSuccessful = False
    return False

# ----------------------------- SELECT PROJECT ----------------------------

def selectProject(auth):
    global selectedProjectID
    global selectedProjectName
    global projectSelected
    global customerProjects
    global customerProjectNames

    if customerProjects == []:
      print("***** You have no projects, please create one before you upload! *****\n")
      input("Press Enter to continue...")
      projectSelected = False
      return False

    print("****** List of your projects ******\n")

    for i in range(len(customerProjectNames)):
      print(str(i+1) + ') ' + customerProjectNames[i])
    print("\n")
    selectedProjectNo = input("Please select a project: ")
    try:
      selectedProjectID = customerProjects[int(selectedProjectNo)-1]
      selectedProjectName = customerProjectNames[int(selectedProjectNo)-1]
      print("\n--> You have selected project: " + selectedProjectName)
      projectSelected = True
      time.sleep(1)
      return selectedProjectID
    except:
      print("\n***** Invalid project number, try again *****\n")
      time.sleep(1)
      projectSelected = False
      return selectProject(auth)

# --------------------------- UPLOAD FILE ---------------------------------

def uploadFile(auth):

    if not projectSelected:
      os.system("printf '\033c'")
      print("\n***** You have not selected a project, please select a project first ! *****\n")
      projectID = selectProject(auth)
    else:
      projectID = selectedProjectID
      print("Selected project: " + selectedProjectName)

    uploadUrl = "https://us-central1-co-one-app-1252e.cloudfunctions.net/api/v1/upload/" + projectID

    print("\nEnter the path of your file to upload: ")
    filePath = input()
    if not os.path.exists(filePath):
      print("\n***** File does not exist, try again *****\n")
      time.sleep(1)
      return uploadFile(auth)
    fileName = os.path.basename(filePath)

    print('Uploading file: ' + fileName)

    payload={}
    files=[
      ('file',(fileName, open(filePath,'rb'),'image/'))
    ]
    headers = {
      'Authorization': auth
    }

    r = requests.request("POST", uploadUrl, headers=headers, data=payload, files=files)
    response = r.text.split(':')[1].split('"')[1]
    if response == 'success':
      print("\n********** Upload Complete **********")
      input("Press Enter to continue")
      os.system("printf '\033c'")
      return True
    else:
      renewLogin()
      headers = {
        'Authorization': auth
      }
      r2 = requests.request("POST", uploadUrl, headers=headers, data=payload, files=files)
      response2 = r2.text.split(':')[1].split('"')[1]
      if response2 == 'success':
        print("\n********** Upload Complete **********")
        input("Press Enter to continue")
        os.system("printf '\033c'")
        return True
      else: 
        print("\n**********\ File upload failed **********")
        print('reason: ' + response2)
        input("Press Enter to continue...")
        os.system("printf '\033c'")
        return False

# -------------------------- UPLOAD FOLDER ----------------------------

def uploadFolder(auth):
  
    if not projectSelected:
      os.system("printf '\033c'")
      print("\n***** You have not selected a project, please select a project first ! *****")
      print("--> Getting projects...")
      projectID = selectProject(auth)
    else:
      projectID = selectedProjectID

    uploadUrl = "https://us-central1-co-one-app-1252e.cloudfunctions.net/api/v1/upload/" + projectID
    print("\nEnter the path of your folder to upload: ")
    folderPath = input()

    if not os.path.exists(folderPath):
      print("\n***** Folder does not exist, try again *****\n")
      time.sleep(1)
      return uploadFolder(auth)
    
    folderName = os.path.basename(folderPath)
    print('\n--> Uploading folder: ' + folderName)

    filesInFolder = os.listdir(folderPath)
    imagesInFolder = []

    for file in filesInFolder:
      if file.endswith(".jpg") or file.endswith(".png"):
        imagesInFolder.append(file)

    fileCount = len(imagesInFolder)
    
    print("--> There are " + str(fileCount) + " images in this folder")
    print("\n********** Image List **********")

    for i in range(fileCount):
      if i <= 9:
        print(str(i+1) + ') ' + imagesInFolder[i])
      elif i == 10:
        print('\n--> There are ' + str(fileCount - i) + ' more images in this folder...')

    print("\n")
    if askYesNo("Are you sure you want to upload these images? (y/n): "):
      print("\n")

      with alive_bar(len(imagesInFolder), dual_line=True) as bar:
        for i in range(len(imagesInFolder)):
          bar.text = f'-> Uploading file: {imagesInFolder[i]}, please wait...'

          filePath = folderPath + '/' + imagesInFolder[i]
          fileName = imagesInFolder[i]
          payload={}
          files=[
            ('file',(fileName, open(filePath,'rb'),'image/'))
          ]
          headers = {
            'Authorization': auth
          }

          r = requests.request("POST", uploadUrl, headers=headers, data=payload, files=files)
          response = r.text.split(':')[1].split('"')[1]

          if response != 'success':
            renewLogin()
            headers = {
            'Authorization': auth
            }
            r2 = requests.request("POST", uploadUrl, headers=headers, data=payload, files=files)
            response2 = r2.text.split(':')[1].split('"')[1]
            if response2 != 'success':
              print('Upload failed: ' + fileName + ' - reason: ' + response)
          
          bar()
        

      print("\n********** Upload Complete **********\n")
      input("Press Enter to continue")
      return True

    else:
      os.system("printf '\033c'")
      print("\n***** Aborting upload *****\n")
      input("Press Enter to continue...")
      return False


#  ----------------------------- MENU ---------------------------------

menu_options = {
    1: 'Login',
    2: 'Select project',
    3: 'Upload a File',
    4: 'Upload a Folder',
    0: 'Exit',
}

def askYesNo(question):
    while True:
        answer = input(question).lower()
        if answer in ('y', 'yes'):
            return True
        elif answer in ('n', 'no'):
            return False
        else:
            print("\n--> Please respond with 'yes' or 'no'")

def print_init():
    os.system("printf '\033c'")
    print("********** Welcome to Co-One ********** ")
    print('********* File uploader script *********\n')

    if loginSuccessful:
      logTxt = "You are logged in as " + loginEmail
    else:
      logTxt = "You are not logged in"

    if projectSelected:
      projTxt = "You have selected project: " + selectedProjectName
    else:
      projTxt = "You have not selected a project"

    print('--> ' + logTxt)
    print('--> ' + projTxt)

    print('\n--> Please select an option:')
    print('')

def print_menu():
    for key in menu_options.keys():
        print(key, ')', menu_options[key])

#  ----------------------------- MAIN ---------------------------------
if __name__ == '__main__':
    while(True):
        print_init()
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except:
            print('\nWrong input. Please enter a number ...')
            time.sleep(1)
        if isinstance(option, int):
          if option > int(menu_options.keys().__len__()-1) or option < 0:
              print('\nWrong input. Please enter a number between 0 and ' + str(menu_options.keys().__len__()-1))
              time.sleep(1)
############################# OPT 1 #############################
        if option == 1:
            login()

############################# OPT 2 #############################
        elif option == 2:

          if not loginSuccessful:
            os.system("printf '\033c'")
            print("***** You need to login first! ***** ")
            input("Press Enter to login...")
            login()
          else:
            os.system("printf '\033c'")
            selectProject(authToken)

############################# OPT 3 #############################
        elif option == 3:
          if not loginSuccessful:
            os.system("printf '\033c'")
            print("***** You need to login first! ***** ")
            input("Press Enter to login...")
            login()
          else:
            uploadFile(authToken)

############################# OPT 4 #############################
        elif option == 4:
          if not loginSuccessful:
            os.system("printf '\033c'")
            print("***** You need to login first! ***** ")
            input("Press Enter to login...")
            login()
          else:
            uploadFolder(authToken)
        
############################# OPT 5 #############################
        elif option == 0:
            os.system("printf '\033c'")
            print('Credits:\nOnur Gumus\nonur.gumus@co-one.co')
            print('\nMade with love <3\n')
            exit()

############################# ELSE #############################
        else:
          print("else")
