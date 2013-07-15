pi-dht2
=======

DHT22 + raspberry pi + googe docs + flask = fun :)

How to run 
------


  * Make a virtualenv and activate it
  * pip install -r requirements.txt
  * In py/daemon is the read & push to spreadsheet part
  * In py/dht22_www is Flask part (still don't works :( )  

How to configure
-----------------


In py/daemon/dht_logger.py set these values  
GOOGLE_LOGIN = ''  
GOOGLE_PASSWORD = ''  
and create a new spreadsheet with name DHT22 and you are ready to go!

The console C app is configured to DHT22 connected to GPIO 4.

How it look like
-----------------
https://docs.google.com/spreadsheet/ccc?key=0AgfFjbJ5DOL0dDRYZlNEQkJybERtRllSVzQxOHptRUE&usp=sharing