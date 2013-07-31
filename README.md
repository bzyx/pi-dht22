pi-dht2
=======

DHT22 + raspberry pi + googe docs + flask + flask restful + sqlite + guiconrn + supervisor + nginx = lots of fun :)

How to run logger
------

  * Make a virtualenv and activate it
  * pip install -r requirements.txt
  * In py/daemon is the read & push to spreadsheet part

How to run web service
------
  * In py / flask_rest_dht is Flask site  
  HOWTO WILL BE LATER :)


How to configure
-----------------


In py/daemon/dht_logger.py set these values  
GOOGLE_LOGIN = ''  
GOOGLE_PASSWORD = ''  
and create a new spreadsheet with name DHT22 and you are ready to go!

The console C app is configured to DHT22 connected to GPIO 4.

How it look like
-----------------
The google docs part:
https://docs.google.com/spreadsheet/ccc?key=0AgfFjbJ5DOL0dGNQQ0l5WFZFaUxLdFduRk1Bb2RBcXc#gid=1


The "REST" API from Flask:
http://bzyx.no-ip.org/h/api/dht/last
