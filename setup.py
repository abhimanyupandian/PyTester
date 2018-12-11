
from setuptools import find_packages, setup

setup(name="Tester",
      version="1.0",
      packages=find_packages(),
      data_files = [('tester/BashTests/src',['tester/BashTests/src/Arithmetic.sh'])]
)