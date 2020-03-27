from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
     name='t9ek80',
     version='1.1.2',
#     scripts=['__init__.py','t9ek80.py'],
#     install_requires=[
#               'soket',
#               'time',
#               'datetime',
#               'binascii',
#               'threading',
#               'sys',
#               'requests',
#               'xmltodict',
#               'xml.etree.ElementTree',
#               'struct',
#               'collections',
#               'pprint',
#     ],
     author="Terje Nilsen",
     author_email="terje.nilsen@km.kongsberg.com",
     description="Simrad EK80 Echosounder interface module.",
     url="https://github.com/The1only/ek80/src",
     long_description=long_description,
     long_description_content_type="text/markdown",
     packages=find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
