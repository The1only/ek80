from setuptools import setup, find_packages
from importlib import import_module

PKG_NAME = "t9ek80"

module = import_module("{}".format(PKG_NAME))


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name=PKG_NAME,
     version=module.__version__,
     scripts=['__init__.py','t9ek80.py'] ,
     author="Terje Nilsen",
     author_email="terje.nilsen@km.kongsberg.com",
     description="Simrad EK80 Echosounder interface module.",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/The1only/ek80",
     packages=find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
