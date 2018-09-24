This folder contains following items:
/lazer_serial_controllers/
----LazerSerialControllerSingleLD.py
----__init__.py
LazerSerialControllerSingleLD_test.py
readme.txt

/lazer_serial_controllers/ folder contains files that are responsible 
for communicating with lazer by serial port
It can be imported as python package into your project by
'from lazer_serial_controllers.LazerSerialControllerSingleLD import LazerSerialControllerSingleLD'

There is a python class that handles connection establishment,
command sending and data receiving.

To check out package functionality, run LazerSerialControllerSingleLD_test.py file.

Protocols supported:
Technoscan single LD

Daniel Lotkov, 2018
For any information contact me at entrolab@gmail.com