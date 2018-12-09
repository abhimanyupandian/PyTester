import os
import time
import random
import sqlite3
import logging
import datetime
import unittest
import threading

from cmd import Cmd

from threading import Thread
from unittest import TestLoader
from multiprocessing.pool import ThreadPool
from multiprocessing.dummy import DummyProcess

logging.basicConfig(level="INFO")

class Test(object):
    """A skeleton class for a Test.

    :param test: A string, name of the test.
    """

    def __init__(self, test):
        self.createdAt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.startedAt = None
        self.finishedAt = None
        self.test = test
        self.results = None
        self._ref = None
        self._status = "NEW"
        self.environment = None
        self.id = random.randint(0, 999999)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if str(status).upper() in ['QUEUED', 'IN PROGRESS', 'PASSED', 'FAILED']:
            self._status = str(status).upper()

class TestEnvironment(object):
    """A skeleton class for a Test Environment/Container.

    :param name: A string, name of the Test Environment/Container.
    :param name: An object, reference to a thread that will run a test.
    """

    def __init__(self, name, thread):
        self.name = name
        self._free = True
        self._thread = thread
        self._currentTest = None

    @property
    def free(self):
        return self._free

    @free.setter
    def free(self, free):
        self._free = free

    @property
    def currentTest(self):
        return self._currentTest

    @currentTest.setter
    def currentTest(self, currentTest):
        self.free = True if currentTest == None else False
        self._currentTest = currentTest

class _tester(object):
    """The main class that implements the concept of Test Environment/Container.

    :param testModuleName: A string, name of the Module containing the unittest.TestCase.
    :param testEnvironmentCount: An integer, The number of Test Environments/Containers to create.
    """
    def __init__(self, testModuleName, testEnvironmentCount = 2):
        self._testDetails = {}
        self._environmentsPool = {}

        self._testModuleName = testModuleName
        self._testModule = __import__(testModuleName)
        self._createTestEnvironments(testEnvironmentCount)

    def _createTestEnvironments(self, environmentCount):
        """Creates a Pool to run the tests.

        :param environmentCount: An integer, specifying the number of Test Environments/Containers to create.
        """
        self.pool = ThreadPool(processes=environmentCount)
        self._updateEnvironmentDetails()

    @property
    def environments(self):
        if not self._environmentsPool:
            logging.error("No Test Enviroments Avaiable! Please create one using TestEnvironment()")
        else:
            return self._environmentsPool

    def _loadDatabase(self):
        """Connects to SQLITE3 database.
        """
        self._con = sqlite3.connect("{}_{}.db".format(self._testModuleName, self._testCaseName))
        self.db = self._con.cursor()

    def _closeDatabase(self):
        """Disconnects from SQLITE3 database.
        """
        self._saveDatabase()
        self.db.close()

    def _saveDatabase(self):
        """Saves the changes to the database.
        """
        self._con.commit()

    def _buildTestObjectBeforeRun(self, test):
        """Modifies/Builds the Test Object of the Test before starting.

        :param test: A string, name of the test.
        """
        _environment = threading.current_thread().getName()
        self.environments[_environment].currentTest = test
        self._testDetails[test].environment = _environment
        self._testDetails[test].startedAt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self._setTestStatuses(test)

    def _setTestStatuses(self, test):
        """Sets the progress of the tests before/while running accordingly.

        :param test: A string, name of the test.
        """
        self._testDetails[test].status = "IN PROGRESS"
        for name, test in self._testDetails.items():
            if test.status == "NEW":
                test.status = "QUEUED"

    def _setStatusBasedOnResult(self, test, status):
        """Sets the status of the tests after running accordingly.

        :param test: A string, name of the test.
        """
        if (len(status.failures) != 0) or (len(status.errors) != 0):
            status = "FAILED"
        else:
            status = "PASSED"
        self._testDetails[test].status = status

    def _detatchTestFromTestEnvironment(self, test, status):
        """Modifies the Test Environment object after it completes a test run.

        :param test: A string, name of the test.
        :param status: The TestTextResult object of the test.
        """
        self._setStatusBasedOnResult(test, status)
        logging.debug("DETATCHING {} ".format(test))
        self._testDetails[test].finishedAt = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.environments[threading.current_thread().getName()].currentTest = None

    def _testContainer(self, test):
        """The main container method that runs the test.

        :param test: A string, name of the test.
        """
        self._buildTestObjectBeforeRun(test)
        _logsDirectory = '{}/{}/{}'.format(self._testModuleName, self._testCaseName, test)
        if not os.path.exists(_logsDirectory):
            os.makedirs(_logsDirectory)
        logFileName = '{}/{}.txt'.format(_logsDirectory, self._testDetails[test].id)
        self._testDetails[test].results = logFileName
        with open(logFileName, "w+") as logFile:
            logging.debug("RUNNING -> {} -> {}".format(test, self._testDetails[test].environment))
            runner = unittest.TextTestRunner(logFile, verbosity=3)
            status = runner.run(self._testCase(methodName=test))
            self._detatchTestFromTestEnvironment(test, status)
            return status

    def _updateEnvironmentDetails(self):
        """Modifies the Test Environment object and updates the Test Environment pool.
        """
        for _thread in threading.enumerate():
            if DummyProcess == type(_thread):
                _environmentName = _thread.getName().replace("Thread-", "Virtual Environment ")
                _thread.setName(_environmentName)
                self._environmentsPool.update({
                    _environmentName: TestEnvironment(_environmentName, _thread)
                })

    def loadTests(self, testCase):
        """Loads the test from the unittest.TestCase class.

        :param testCase: A string, name of the unittest.TestCase class within the TestCaseModule.
        """
        self._testCaseName = testCase
        _testCase = getattr(self._testModule, testCase)
        self.tests = TestLoader().getTestCaseNames(_testCase)
        self._testCase = _testCase
        for eachTest in self.tests:
            self._testDetails.update(
                {
                    eachTest: Test(eachTest)
                })
        return True

    def runTests(self, results = False, resultInterval = 1):
        """Maps and Runs the tests in the Test Environment pool.

        :param results: A boolean, specifying whether results must be retrieved.
        :param resultInterval: An integer, specifying the interview to retrieve the results.
        """
        self._loadDatabase()
        for each_test in self.tests:
            self._testDetails[each_test]._ref = self.pool.map_async(self._testContainer, (each_test,))
        if results:
            self.getAllResults(resultInterval)
        self._closeDatabase()

    def checkTestDone(self, test):
        """Checks if the test run in the background is complete.

        :param test: A string, name of the test.
        """
        try:
            return True if self._testDetails[test]._ref.ready() else False
        except KeyError:
            logging.debug("Test {}'s results are not found! Were the tests run? ".format(test))
        except Exception as e:
            logging.error("Unable to retrieve test {}'s results. Error log : {}\n".format(test, e))
        return False

    def _insertIntoTable(self, test):
        """Records the Test object data into the results database.

        :param test: A string, name of the test.
        """
        self._loadDatabase()
        testRef = self._testDetails[test]
        if not self.db.execute('''SELECT * from {} WHERE startedAt="{}" AND test="{}" and id = "{}"'''
                           .format(test, testRef.startedAt, testRef.test, testRef.id)).fetchall():
            self.db.execute('''INSERT INTO {} (id, environment, test, createdAt, startedAt, finishedAt,
                            status, results) VALUES ("{}","{}","{}","{}","{}","{}","{}","{}")'''
                            .format(test, testRef.id, testRef.environment, testRef.test, testRef.createdAt,
                                    testRef.startedAt, testRef.finishedAt, testRef.status, testRef.results))
        self._closeDatabase()

    def _populateResultsIntoDatabase(self, test):
        """Creates a table and records the Test object data into the results database.

        :param test: A string, name of the test.
        """
        self._loadDatabase()
        try:
            self.db.execute('''CREATE TABLE {}(id any, environment any, test any, createdAt any, startedAt any, 
                                    finishedAt any, status any, results any)'''.format(test))
        except:
            pass
        finally:
            self._insertIntoTable(test)
        self._closeDatabase()

    def getResultsFromDatabase(self, test):
        """Retrieves results of a test from the database.

        :param test: A string, name of the test.
        """
        self._loadDatabase()
        testStructure = ("id","environment","test","createdAt","startedAt","finishedAt","status","results")
        try:
            return [dict(zip(testStructure, eachResult)) for eachResult in
                    self.db.execute("SELECT * FROM {}".format(test)).fetchall()]
        except sqlite3.OperationalError:
            logging.debug("No results found for test {}".format(test))
        self._closeDatabase()

    def getTest(self, test):
        """Retrieves the Test object.

        :param test: A string, name of the test.
        """
        return self._testDetails[test] if self._testDetails[test] else None

    def getTestResult(self, test):
        """Retrieves the results from the completed test.

        :param test: A string, name of the test.
        """
        self._loadDatabase()
        if self.checkTestDone(test):
            results = self._testDetails[test]._ref.get()[0]
            self._populateResultsIntoDatabase(test)
            return results
        self._closeDatabase()

    def currentTestRunningOnEnvironment(self, environment = 1):
        """Retrieves the test currenlty running on the Test Environment.

        :param environment: An integer, signifying the id of the Test Environment.
        """
        try:
            return self.environments['Virtual Environment ' + str(environment)].currentTest
        except Exception:
            logging.error("Virtual Environment {} not found!".format(environment))
            return None

    def getAllResults(self, interval=1):
        """Retrieves results of all the tests running on the Test Environment.

        :param interval: An integer, signifying the interval at which the test results must be retrieved.
        """
        allResults = []
        while (True):
            time.sleep(interval)
            for test in self._testDetails.keys():
                result = self.getTestResult(test)
                if result:
                    allResults.append(test)
            for environment, thread in self.environments.items():
                logging.debug("ENVIRONMENT {} | FREE STATUS -> {} | IS RUNNING -> {}".format(environment, thread.free,
                                                                                     thread.currentTest))
            for name, test in self._testDetails.items():
                logging.debug("TEST {} | STATUS -> {} | ENVIRONMENT -> {}".format(name, test.status, test.environment))
            if set(allResults) == set(self.tests):
                return allResults

class Tester(Cmd):

    prompt = 'Tester> '
    intro = "Welcome! Type ? to list commands"
    undoc_header = "Tester Commands"
    _tester = None
    _loaded = None

    def do_exit(self, exit):
        '''exit the application.'''
        logging.info("Bye!")
        return True

    def do_init(self, testModuleName, testEnvironment = 2):
        '''Initialize the Test Environments within the module specified and the number of Test Environments required.

        :param testModuleName: A string, name of the Module containing the unittest.TestCase.
        :param testEnvironmentCount: An integer, The number of Test Environments/Containers to create.

        :syntax
            init Tests 4 '''

        try:
            self._testModule = testModuleName
            self._tester = _tester(testModuleName, testEnvironmentCount=int(testEnvironment))
            if self._tester:
                logging.info("Test Module was loaded successfully. Use 'load' command to load the tests in the Module")
        except Exception as e:
            logging.info("There was a problem loading the Module - {}".format(e))
        self.lastcmd = ''

    def do_load(self, testCaseName):
        '''Loads the tests from the Module.

        :param testCaseName: A string, name of the unittest.TestCase.

        :syntax
            load FunctionalTests '''
        try:
            if self._tester == None:
                logging.info("Run 'init' command first to initialize the Test Module.")
            else:
                self._loaded = self._tester.loadTests(testCaseName)
                if self._loaded:
                    logging.info("The Tests were loaded successfully! Please enter 'run' command to run the tests")
        except AttributeError:
            logging.info("The Test Module {} does not contain an Test Case named {}".format(self._testModule, testCaseName))
        except Exception as e:
            logging.info("There was problem loading the Test Case from the Module - {}".format(e))
        self.lastcmd = ''

    def do_run(self, params):
        """Runs the tests.

        :param retrieveResults: A boolean, specifying whether results must be retrieved.
        :param resultInterval: An integer, specifying the interview to retrieve the results.

        :syntax
            run -r True -i 2"""
        results = False
        resultInterval = 1
        params = params.split()
        try:
            for index, arg in enumerate(params):
                if arg == '-r':
                    results = bool(params[index + 1])
                if arg == '-i':
                    try:
                        resultInterval = int(params[index + 1])
                    except:
                        pass
        except Exception as e:
            logging.info("'run' command failed - {}".format(e))

        if results:
            logging.basicConfig(level="DEBUG")
        elif self._loaded is None:
            logging.info("Run 'load' command first to load the Test Cases.")
        elif self._tester is None:
            logging.info("Run 'init' command first to initialize the Test Module.")
        else:
            print("Starting tests in the background...")
            t = Thread(target=self._tester.runTests, args= (results, resultInterval, ))
            t.daemon = True
            t.start()
            print("Tests were started in the background... Use 'get_result' and 'get_test' to retrieve results!")
        self.lastcmd = ''

    def do_get_results(self, test):
        """Retrieves results of a test from the database.
        """
        if self._loaded is None:
            logging.info("Run 'load' command first to load the Test Cases.")
        elif self._tester is None:
            logging.info("Run 'init' command first to initialize the Test Module.")
        else:
            results = self._tester.getResultsFromDatabase(str(test))
            if results is None:
                logging.info("Results for test {} was not found!".format(test))
            else:
                self._printResultTable(results)
        self.lastcmd = ''

    def do_get_test(self, test):
        """Retrieves Test details.
        """
        if self._loaded is None:
            logging.info("Run 'load' command first to load the Test Cases.")
        elif self._tester is None:
            logging.info("Run 'init' command first to initialize the Test Module.")
        else:
            _test = self._tester.getTest(str(test))
            if _test is None:
                logging.info("Test {} was not found!".format(test))
            else:
                self._printTest(_test)
        self.lastcmd = ''


    def _printTest(self, test):
        print("{:<8} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15}".format("id", "environment", "test" , "createdAt",
                                                                              "startedAt", "finishedAt","status", "results" ))

        print("{:<8} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15}".format(test.id,
                                                                              test.environment,
                                                                              test.createdAt,
                                                                              test.startedAt,
                                                                              test.finishedAt,
                                                                              test.status,
                                                                              test.results))

    def _printResultTable(self, results):
        print("{:<8} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15}".format("id", "environment", "test" , "createdAt",
                                                                              "startedAt", "finishedAt","status", "results" ))
        for eachResult in results:
            print("{:<8} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15} | {:<15}".format(eachResult["id"],
                                                                                  eachResult["environment"],
                                                                                  eachResult["test"],
                                                                                  eachResult["createdAt"],
                                                                                  eachResult["startedAt"],
                                                                                  eachResult["finishedAt"],
                                                                                  eachResult["status"],
                                                                                  eachResult["results"]))
Tester().cmdloop()

# if __name__ == "__main__":
#     tester = _tester("Tests", testEnvironmentCount = 2)
#     tester.loadTests("FunctionalTests")
#     tester.runTests(results = True, resultInterval = 1)
#     # tester.runTests()
#     print(tester.getResultsFromDatabase("test_uppersss"))
