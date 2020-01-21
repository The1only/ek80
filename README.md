# ek80
Simrad EK80 echosounder python interface module.

The t9ek80.py should normally not be modified, it contains the generic interface.
The biomass and singletargetchirp are example user files.
The xml files ar config files.

Usage:

 pip install --index-url https://test.pypi.org/simple/ --no-deps t9ek80
 
 # We are only on the test.pip yet... later it will be: pip install t9ek80

git clone https://github.com/The1only/ek80.git

cd ./ek80/examples

python biomass.py config2.xml


PS: All testing has been done using python3 and pip3 

The Simrad EK80 user manual can be found at: https://www.simrad.online/ek80/ref_en/default.htm


