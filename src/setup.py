import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='t9ek80',  
     version='0.3',
     scripts=['__init__.py','t9ek80.py'] ,
     author="Terje Nilsen",
     author_email="terje.nilsen@km.kongsberg.com",
     description="Simrad EK80 Echosounder interface module.",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/The1only/ek80",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
