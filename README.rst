PyTester: Run python unittests in the background
===========================================

Installation
------------
- GIT clone or download the repository.
- IMPORTANT: Navigate into the root directory of the repository, where setup.py exists. (ie; PyTester/)
- Run the application : python3 Tester.py (located at PyTester/tester/).
NOTE: 
- To run bash tests on Windows, we will need 'bash' to be installed on the system.

Structure of Test
------------
- Tests are 'python packages' containing the following:
	- <Module>.py file that contains the unittest.TestCase classes. (example: PyTester/tester/PythonTests/PythonArithmeticTestsPass.py)
	- __init__.py file that imports the modules containing the unittest.TestCase. (example: PyTester/tester/PythonTests/__init__.py)

Commands
------------
- init <Test Package> <Environment Count>
	- This command is used to initialize the Test Environments.
	- <Test Package> : Specifies which python package contains the Test Modules (ie; python files containing unittests.TestCases)
	- <Environment Count> : Specifies how many Test Environments must be used to run and queue the unittests. (Default Count : 2)
- load <Test Module>
	- This command is used to load the Test Modules. (that contain the unittest functions)
	- <Test Module> : Specifies the name of the Test Module that contains unittest.TestCase class.
- run
	- This command runs the tests within the Test Module that was loading using 'load' command.
- environments
	- This command diplays the status of all the Test Environments.
- test <Test Name>
	- This command displays the status of the Test in the current session.
	- <Test Name> : Specifies the name of Test.
	- These results can be queried even when the current Test is in progress.
- results <Test Name>
	- This command displays not just the results of the Test from the current session but the entire history of results of the Test.
	- <Test Name> : Specifies the name of Test.
	- These are results retrieved from the database. These results for the current test will be avaiable only after the current test completes. However, history of results if it exists, will be displayed.

Results
------------
PyTester records 3 kinds of results for every Test:

- Main Logs:
	- These are main logger messages that is outputted in the console.
	- These are generated at the current working directory from where Tester.py was run.
	- Main Log name : <Random Number>_log.log
- Test Logs:
	- These are Test specific logger messages.
	- These are generated within the following folder hierarchy : <Test Package>/<Test Module>/<Test Name>/<random number>.log
- Database Results:
	- This is the database of results of the Test.
	- These are generated within the following folder hierarchy : <Test Package>/<Test Package>_<Test Module>.db
	- Note that these results for the current test will be only available after the test completes. However, if the test has history of results, they will be displayed.

Creating and running your own Tests
------------
- NOTE: Currently PyTester only supports Test creation at the PyTest/tester directory (ie; the location where Tester.py resides)
- Create a folder <TEST_NAME> under PyTester/
- Create a python module <MODULE_NAME> containing your unittest.TestCase class and the test functions you require within it, under 'PyTester/<TEST_NAME>/' folder
- Create the __init__.py at PyTester/ and import the module created in the step above like so :


.. code:: python

	from <MODULE_NAME> import *
	
	
- We can have multiple modules but all of these modules must be imported into __init__.py.
- This completes the Test creation and now we can proceed with running the Test using Tester.py.
- Run Tester.py 
- Initialize your Test Environment for your Test using : init <PACKAGE_NAME>.
- Load the Test Module using : load <MODULE_NAME>.
- Run the Tests using : run
- Retrieve results using : test <TEST_NAME> and results <TEST_NAME>

Sample Console output
-----------
- <PACKAGE_NAME> : BashTests
- <MODULE_NAME> : BashArithmeticTestsFail
- <TEST_NAME> : test_subtraction

.. code:: bash

	C:\Users\AP\Documents\PyTester\tester>python Tester.py
	Logging into 88133_logs.log
	Welcome! Type ? to list commands
	Tester> init BashTests
	Test Module was loaded successfully with 2 Virtual Environments. Use 'load <Test Case Name>' command to load the tests in the Module
	Tester> load BashArithmeticTestsFail
	The Tests were loaded successfully! Please enter 'run' command to run the tests
	Tester> run
	Starting tests in the background...
	Tests were started in the background... Use 'results <test name>' and 'test <test name>' to retrieve results!
	Tester> test test_subtraction
	id       | environment     | test            | createdAt       | startedAt       | finishedAt      | status          | results
	206140   | Virtual Environment 1 | 2018-12-11 14:54:08 | 2018-12-11 14:54:13 | None            | IN PROGRESS     | BashTests/BashArithmeticTestsFail/test_subtraction/206140.txt
	Tester> environments
	Name            | Free            | Current Test
	Virtual Environment 2 | False           | test_subtraction
	Virtual Environment 1 | True            | None

Algorithm
-----------

- Initialize objects to store Test, Environment and Result data.
- Connect to database table or create new if it does not exist.
- Read 'Test Package' string input from the user.
- Read 'Environment Count' integer input from the user, or default to 2.
- Create a Thread pool with processes equal to the number of environments provided. 
- Import the package if present, else display 'Test Module not Found' message.
- Read 'Test Module' string input from user.
- Load the module from the package if present using getattr. If failed, display error message.
- On successful load of module, load all test functions within it using TestLoader().
- Tests will be run using unittest.TextTestRunner().run(), which takes a unittest test function as input.
- unittest.TextTestRunner().run() will be invoked from the test container function.
- Upon running the tests, the test container function will be mapped to every test function using an 'async map'.
- The 'asyn map' will maintain a queue of size of 'Environment Count'.
- Update the test object when tests are running to allow retriveal of querying test results.
- Update the database when the test is complete and mark test object accordingly.

