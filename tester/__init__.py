import os
import subprocess

from Tester import *

class BashScript(object):
    def __init__(self, script):
        self.script = script

    def __getattr__(self, name):
        def call_fun(*args):
            script_path = "'{}'".format(os.path.dirname(os.path.realpath(self.script)))
            return subprocess.check_output(['bash', '-c', 'source {} && {} {}'.format(script_path, name,
                                            " ".join([str(each) for each in args]))], universal_newlines=True)

        return call_fun
