import envoy
import gspread
import urllib2
import re
import time
import threading
import logging

from datetime import datetime
from urllib2 import HTTPError


GOOGLE_LOGIN = ''
GOOGLE_PASSWORD = ''
SPREADSHEET_NAME = 'DHT22'
COMMAND_TO_RUN = "sudo ./dht_reader"
DB_LOCATION = "./database.db"


logging.basicConfig(level=logging.DEBUG, filename='/tmp/dht_logging_app.log')
"""Internal logger"""


class DatabaseHandler(object):
    """This class handles connection to spreadsheet and managing it's state.
    """
    DB_CREATE_COMMAND = """
    CREATE TABLE "error" ( "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "timestamp" TEXT NOT NULL, "description" TEXT );
    CREATE TABLE "measurement" ( "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "timestamp" TEXT NOT NULL, "year" TEXT, "month" TEXT, "day" TEXT, "hour" TEXT, "temp" REAL, "humid" REAL );
    CREATE TABLE "settings" ( "key" TEXT NOT NULL, "value" TEXT );
    """
    
    DB_INIT_COMMAND = """
    INSERT INTO settings VALUES( "last_measurement_id", 0);
    """
    DB_TEST_COMMAND = """
    SELECT value FROM settings WHERE key = "last_measurement_id";
    """
    
    INSERT_MEASUREMENT = "INSERT INTO measurement ('timestamp', 'year', 'month', 'day', 'hour', 'temp', 'humid') VALUES (?, ?, ?, ?, ?, ?, ?);"
    INSERT_ERROR = "INSERT INTO error ('timestamp', 'description') VALUES (?, ?);"


    def __init__(self):
        """A class that connects to google drive and prepares the spreadsheet.
        """
        self.connnection = sqlite3.connect(DB_LOCATION)
        self.prepare_database()
        


    def prepare_database(self):
        """This function prepares the structure of spreadsheet.
            1) Adds new spreadsheets and changes their size
            2) Tries to delete the original one

            Returns:
            None
        """
        data = None
        try:
            cursor = self.connnection.cursor()
            cursor.execute(DatabaseHandler.DB_TEST_COMMAND)
            data=cursor.fetchone()
        except sqlite3.OperationalError, e:
            logging.error('Db error')
            logging.exception(e)
            
        if data is None:
            logging.info('Creating a new database')
            cursor.executescript(DatabaseHandler.DB_CREATE_COMMAND)
            self.connnection.commit()
            cursor = self.connnection.cursor()
            cursor.execute(DatabaseHandler.DB_INIT_COMMAND)
            self.connnection.commit()


    def add_measurement(self, temperature, humidity):
        """This function adds a measurement to database with
            actual timestamp

            Args:
               temperature (str):  A temperature value.
               humidity (str):     A humidity value.

            Returns:
            None
        """
        with self.connnection:
            cursor = self.connnection.cursor()
            dt_now = datetime.now()
            cursor.execute(DatabaseHandler.INSERT_MEASUREMENT, (dt_now, dt_now.year,
                                                            dt_now.month, dt_now.day, dt_now.hour,
                                                            temperature, humidity))
            logging.info('Trying to add a value to DB')
            lastrowid = cursor.lastrowid
            logging.info('GOT ROW_ID '+ str(lastrowid))
            cursor.execute("UPDATE settings SET value=? WHERE key='last_measurement_id'", (lastrowid, ))
            
            self.connnection.commit()

    def add_error(self, error_code, error_desc):
        """This function adds an error description to database

            Args:
               error_code:          A numerical error code from reader
               error_desc (str):    An additional description of error

            Returns:
            None
        """
        with self.connnection:
            cursor = self.connnection.cursor()
            dt_now = datetime.now()
            cursor.execute(DatabaseHandler.INSERT_ERROR, ( datetime.now(),error_desc))
            logging.info('Trying to add an error to DB')
                        
            self.connnection.commit()

class SpreadsheetHandler(object):
    """This class handles connection to spreadsheet and managing it's state.
    """
    SHEET_TITLES = ('VALUES', 'ERRORS')
    SHEETS_COLUM_TITLES = (('TIMESTAMP', 'TEMP', 'HUM'),
                           ('TIMESTAMP', 'ERROR_CODE', 'ERROR_DESC'))

    def __init__(self):
        """A class that connects to google drive and prepares the spreadsheet.
        """
        gsconnect = gspread.login(GOOGLE_LOGIN, GOOGLE_PASSWORD)
        self.spreadsheet = gsconnect.open(SPREADSHEET_NAME)
        self.prepare_speradsheet()

    def prepare_speradsheet(self):
        """This function prepares the structure of spreadsheet.
            1) Adds new spreadsheets and changes their size
            2) Tries to delete the original one

            Returns:
            None
        """
        if len(set(self.spreadsheet.worksheets()) -
                set(SpreadsheetHandler.SHEET_TITLES)) == 1:
            logging.info('Creating a new spreadsheet')

            for sheet_title, colum_names in \
                            zip(SpreadsheetHandler.SHEET_TITLES,
                                SpreadsheetHandler.SHEETS_COLUM_TITLES):
                wrk_sheet = self.spreadsheet.add_worksheet(sheet_title,
                                                           rows=1, cols=3)
                wrk_sheet.update_cell(1, 1, colum_names[0])
                wrk_sheet.update_cell(1, 2, colum_names[1])
                wrk_sheet.update_cell(1, 3, colum_names[2])
            try:
                logging.info('Trying to delete a sheet')
                self.spreadsheet.del_worksheet(self.spreadsheet.sheet1)
            except urllib2.HTTPError, e:
                logging.exception(e)

    def add_measurement(self, temperature, humidity):
        """This function adds a measurement to spreadsheet with
            actual timestamp

            Args:
               temperature (str):  A temperature value.
               humidity (str):     A humidity value.

            Returns:
            None
        """
        values = self.spreadsheet.worksheet(SpreadsheetHandler.SHEET_TITLES[0])
        values_to_add = [datetime.now(), temperature, humidity]
        logging.info('Trying to add a value')
        values.append_row(values_to_add)

    def add_error(self, error_code, error_desc):
        """This function adds a measurement to spreadsheet with
            actual timestamp

            Args:
               error_code:          A numerical error code from reader
               error_desc (str):    An additional description of error

            Returns:
            None
        """
        values = self.spreadsheet.worksheet(SpreadsheetHandler.SHEET_TITLES[1])
        values_to_add = [datetime.now(), error_code, error_desc]
        logging.info('Trying to add an error')
        values.append_row(values_to_add)

    def get_last_num_values(self, number_of_values=40):
        """This function returns a part of last values from spreadsheet

            Args:
               number_of_values (int):    How many values (default 40 ~ 10min)

            Returns:
            tuple. Tuple of lists with the values

            Notes:
                This works very very slow :(
        """
        values = self.spreadsheet.worksheet(SpreadsheetHandler.SHEET_TITLES[0])
        timestamps = []
        temps = []
        humids = []

        starting_row = values.row_count - number_of_values
        for row in xrange(starting_row, values.row_count):
            row_value = values.row_values(row)      # TODO: Why this is so slow
            timestamps.append(row_value[0])
            temps.append(row_value[1])
            humids.append(row_value[2])
        return (timestamps, temps, humids)


class DHTReader(object):
    """This class handles reading data from DHT sensor."""

    def __init__(self):
        """Opens a spreadsheet and reads data from DHT22.
        Then saves the data to the spreadsheet"""

        self.spreadsheet_handler = SpreadsheetHandler()
        self.database_handler = DatabaseHandler()

    def _form_result(self, response_dht):
        """This function get response text from DHT and pulls the data out

        Args:
            response_dht(str):   A string from DHT reader app

        Raises:
            AssertionError

        Returns:
            list. A list of 2 values the temperature and humidity
        """
        results = [elem.replace('= ', '') for elem in re.findall("= [0-9.]+",
                                                                 response_dht)]
        assert len(results) == 2
        return results

    def try_read(self):
        """This function tries to execute the command and read the data

        Returns:
        None
        """
        logging.info('Trying to read')
        response = None
        try:
            response = envoy.run(COMMAND_TO_RUN, timeout=2)

            if response.status_code == 0:
                try:
                    self.spreadsheet_handler.add_measurement(
                                        *self._form_result(response.std_out))
                    self.database_handler.add_measurement(
                                        *self._form_result(response.std_out))
                except AssertionError, e:
                    logging.exception(e)
                    self.spreadsheet_handler.add_error(response.status_code,
                                                   response.std_out)

            else:
                self.spreadsheet_handler.add_error(response.status_code,
                                               response.std_err)
        except OSError, e:
        # From time to time "OSError: [Errno 1] Operation not permitted"
            logging.exception(e)

    def run(self):
        """This function runs the script in endless loop and reads data
        in interval of 15 sec.
        """
        i = 1
        while True:
            logging_TXT = "Measure # %d"
            logging.info(logging_TXT % i)
            try:
                self.try_read()
            except HTTPError, e:
                # HTTPError: HTTP Error 500: Internal Server Error when google have problems
                logging.exception(e)
            time.sleep(15)

if __name__ == '__main__':
    logging.info('DHT_LOGGER_APP STARTS NOW!')
    d = DHTReader()
    d.run()
    #threading.Thread(target=d.run).start()
