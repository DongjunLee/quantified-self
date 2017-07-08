#--------------------------------------------------------------
# TogglPy is a non-cluttered, easily understood and implemented
# library for interacting with the Toggl API.
#--------------------------------------------------------------
import base64
from datetime import datetime
# for making requests
import urllib.request
import urllib.error
import urllib.parse

# parsing json data
import json
#
#---------------------------------------------
# Class containing the endpoint URLs for Toggl
#---------------------------------------------


class Endpoints():
    WORKSPACES = "https://www.toggl.com/api/v8/workspaces"
    CLIENTS = "https://www.toggl.com/api/v8/clients"
    PROJECTS = "https://www.toggl.com/api/v8/projects"
    REPORT_WEEKLY = "https://toggl.com/reports/api/v2/weekly"
    REPORT_DETAILED = "https://toggl.com/reports/api/v2/details"
    REPORT_SUMMARY = "https://toggl.com/reports/api/v2/summary"
    START_TIME = "https://www.toggl.com/api/v8/time_entries/start"
    TIME_ENTRIES = "https://www.toggl.com/api/v8/time_entries"

    @staticmethod
    def STOP_TIME(pid):
        return "https://www.toggl.com/api/v8/time_entries/" + \
            str(pid) + "/stop"
    CURRENT_RUNNING_TIME = "https://www.toggl.com/api/v8/time_entries/current"

#-------------------------------------------------------
# Class containing the necessities for Toggl interaction
#-------------------------------------------------------


class Toggl():
    # template of headers for our request
    headers = {
        "Authorization": "",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "python/urllib",
    }

    # default API user agent value
    user_agent = "TogglPy"

    #-------------------------------------------------------------
    # Auxiliary methods
    #-------------------------------------------------------------

    def decodeJSON(self, jsonString):
        jsonString = str(jsonString, 'utf-8')
        return json.JSONDecoder().decode(jsonString)

    #-------------------------------------------------------------
    # Methods that modify the headers to control our HTTP requests
    #-------------------------------------------------------------
    def setAPIKey(self, APIKey):
        '''set the API key in the request header'''
        # craft the Authorization
        authHeader = APIKey + ":" + "api_token"

        authHeader = base64.b64encode(authHeader.encode('ascii'))
        authHeader = "Basic " + authHeader.decode(encoding='utf-8')

        # add it into the header
        self.headers['Authorization'] = authHeader

    def setAuthCredentials(self, email, password):
        authHeader = '{0}:{1}'.format(email, password)

        authHeader = base64.b64encode(authHeader.encode('ascii'))
        authHeader = "Basic " + authHeader.decode(encoding='utf-8')

        # add it into the header
        self.headers['Authorization'] = authHeader

    def setUserAgent(self, agent):
        '''set the User-Agent setting, by default it's set to TogglPy'''
        self.user_agent = agent

    def setWorkspaceId(self, wid):
        '''set the workspaces id in class'''
        self.wid = wid

    #------------------------------------------------------
    # Methods for directly requesting data from an endpoint
    #------------------------------------------------------

    def requestRaw(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters is None:
            return urllib.request.urlopen(
                urllib.request.Request(
                    endpoint, headers=self.headers)).read()
        else:
            if 'user_agent' not in parameters:
                # add our class-level user agent in there
                parameters.update({'user_agent': self.user_agent, })
            # encode all of our data for a get request & modify the URL
            endpoint = endpoint + "?" + urllib.parse.urlencode(parameters)
            return urllib.request.urlopen(
                urllib.request.Request(
                    endpoint,
                    headers=self.headers)).read()  # make request and read the response

    def request(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the page data as a parsed JSON dict'''
        return json.loads(str(self.requestRaw(endpoint, parameters), 'utf-8'))

    def postRequest(self, endpoint, parameters=None):
        '''make a POST request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters is None:
            return urllib.request.urlopen(
                urllib.request.Request(
                    endpoint, headers=self.headers)).read()
        else:
            data = json.JSONEncoder().encode(parameters)
            data = data.encode('ascii')
            return urllib.request.urlopen(
                urllib.request.Request(
                    endpoint,
                    data=data,
                    headers=self.headers)).read()  # make request and read the response

    #----------------------------------
    # Methods for managing Time Entries
    #----------------------------------

    def startTimeEntry(self, description, pid):
        '''starts a new Time Entry'''
        data = {
            "time_entry": {
                "description": description,
                "pid": pid,
                "created_with": self.user_agent
            }
        }
        response = self.postRequest(Endpoints.START_TIME, parameters=data)
        return self.decodeJSON(response)

    def currentRunningTimeEntry(self):
        '''Gets the Current Time Entry'''
        response = self.postRequest(Endpoints.CURRENT_RUNNING_TIME)
        return self.decodeJSON(response)

    def stopTimeEntry(self, entryid):
        '''Stop the time entry'''
        response = self.postRequest(Endpoints.STOP_TIME(entryid))
        return self.decodeJSON(response)

    def createTimeEntry(
            self,
            hourduration,
            projectid=None,
            projectname=None,
            clientname=None,
            year=None,
            month=None,
            day=None,
            hour=None):
        """
        Creating a custom time entry, minimum must is hour duration and project param
        :param hourduration:
        :param projectid: Not required if projectname given
        :param projectname: Not required if projectid was given
        :param clientname: Can speed up project query process
        :param year: Taken from now() if not provided
        :param month: Taken from now() if not provided
        :param day: Taken from now() if not provided
        :param hour: Taken from now() if not provided
        :return: response object from post call
        """
        data = {
            "time_entry": {}
        }

        if not projectid:
            if projectname and clientname:
                projectid = (
                    self.getClientProject(
                        clientname,
                        projectname))['data']['id']
            elif projectname:
                projectid = (self.searchClientProject(projectname))[
                    'data']['id']
            else:
                print('Too many missing parameters for query')
                exit(1)

        year = datetime.now().year if not year else year
        month = datetime.now().month if not month else month
        day = datetime.now().day if not day else day
        hour = datetime.now().hour if not hour else hour

        timestruct = datetime(year, month, day, hour - 2).isoformat() + '.000Z'
        data['time_entry']['start'] = timestruct
        data['time_entry']['duration'] = hourduration * 3600
        data['time_entry']['pid'] = projectid
        data['time_entry']['created_with'] = 'NAME'

        response = self.postRequest(Endpoints.TIME_ENTRIES, parameters=data)
        return self.decodeJSON(response)

    #-----------------------------------
    # Methods for getting workspace data
    #-----------------------------------
    def getWorkspaces(self):
        '''return all the workspaces for a user'''
        return self.request(Endpoints.WORKSPACES)

    def getWorkspace(self, name=None, workspace_id=None):
        '''return the first workspace that matches a given name or id'''
        workspaces = self.getWorkspaces()  # get all workspaces

        # if they give us nothing let them know we're not returning anything
        if name is None and id is None:
            print(
                "Error in getWorkspace(), please enter either a name or an id as a filter")
            return None

        if workspace_id is None:  # then we search by name
            for workspace in workspaces:  # search through them for one matching the name provided
                if workspace['name'] == name:
                    return workspace  # if we find it return it
            return None  # if we get to here and haven't found it return None
        else:  # otherwise search by id
            for workspace in workspaces:  # search through them for one matching the id provided
                if workspace['id'] == int(workspace_id):
                    return workspace  # if we find it return it
            return None  # if we get to here and haven't found it return None

    def getWorkspaceProjects(self):
        '''return all projects in the workspace'''
        return self.request(Endpoints.WORKSPACES + "/" +
                            str(self.wid) + "/projects")

    def getWorkspaceProject(self, name):
        """
        Provide only a projects name for query and search through entire available names
        :param name: WorkspaceId and Desired Project's name
        :return: Project object
        """
        for project in self.getWorkspaceProjects():
            if project['name'] == name:
                return project
        print('Could not find project by the name')
        return None

    #--------------------------------
    # Methods for getting client data
    #--------------------------------
    def getClients(self):
        '''return all clients that are visable to a user'''
        return self.request(Endpoints.CLIENTS)

    def getClient(self, name=None, client_id=None):
        '''return the first workspace that matches a given name or id'''
        clients = self.getClients()  # get all clients

        # if they give us nothing let them know we're not returning anything
        if name is None and id is None:
            print("Error in getClient(), please enter either a name or an id as a filter")
            return None

        if id is None:  # then we search by name
            for client in clients:  # search through them for one matching the name provided
                if client['name'] == name:
                    return client  # if we find it return it
            return None  # if we get to here and haven't found it return None
        else:  # otherwise search by id
            for client in clients:  # search through them for one matching the id provided
                if client['id'] == int(client_id):
                    return client  # if we find it return it
            return None  # if we get to here and haven't found it return None

    def getClientProjects(self, client_project_id):
        """
        :param id: Client ID by which to query
        :return: Projects object returned from endpoint
        """
        return self.request(Endpoints.CLIENTS + '/{0}/projects'.format(client_project_id))

    def searchClientProject(self, name):
        """
        Provide only a projects name for query and search through entire available names
        WARNING: Takes a long time!
                 If client name is known, 'getClientProject' would be advised
        :param name: Desired Project's name
        :return: Project object
        """
        for client in self.getClients():
            try:
                for project in self.getClientProjects(client['id']):
                    if project['name'] == name:
                        return project
            except BaseException:
                continue

        print('Could not find client by the name')
        return None

    def getClientProject(self, clientName, projectName):
        """
        Fast query given the Client's name and Project's name
        :param clientName:
        :param projectName:
        :return:
        """
        for client in self.getClients():
            if client['name'] == clientName:
                cid = client['id']

        if not cid:
            print('Could not find such client name')
            return None

        for projct in self.getClientProjects(cid):
            if projct['name'] == projectName:
                pid = projct['id']

        if not pid:
            print('Could not find such project name')
            return None

        return self.getProject(pid)

    # --------------------------------
    # Methods for getting PROJECTS data
    # --------------------------------
    def getProject(self, pid):
        '''return all projects that are visable to a user'''
        return self.request(Endpoints.PROJECTS + '/{0}'.format(pid))

    #---------------------------------
    # Methods for getting reports data
    #---------------------------------
    def getWeeklyReport(self, data):
        '''return a weekly report for a user'''

        if 'workspace_id' not in data:
            data['workspace_id'] = self.wid

        return self.request(Endpoints.REPORT_WEEKLY, parameters=data)

    def getWeeklyReportPDF(self, data, filename):
        '''save a weekly report as a PDF'''

        if 'workspace_id' not in data:
            data['workspace_id'] = self.wid

        # get the raw pdf file data
        filedata = self.requestRaw(
            Endpoints.REPORT_WEEKLY + ".pdf",
            parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getDetailedReport(self, data):
        '''return a detailed report for a user'''

        if 'workspace_id' not in data:
            data['workspace_id'] = self.wid

        return self.request(Endpoints.REPORT_DETAILED, parameters=data)

    def getDetailedReportPDF(self, data, filename):
        '''save a detailed report as a pdf'''

        if 'workspace_id' not in data:
            data['workspace_id'] = self.wid

        # get the raw pdf file data
        filedata = self.requestRaw(
            Endpoints.REPORT_DETAILED + ".pdf",
            parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getSummaryReport(self, data):
        '''return a summary report for a user'''

        if 'workspace_id' not in data:
            data['workspace_id'] = self.wid

        return self.request(Endpoints.REPORT_SUMMARY, parameters=data)

    def getSummaryReportPDF(self, data, filename):
        '''save a summary report as a pdf'''

        if 'workspace_id' not in data:
            data['workspace_id'] = self.wid

        # get the raw pdf file data
        filedata = self.requestRaw(
            Endpoints.REPORT_SUMMARY + ".pdf",
            parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)
