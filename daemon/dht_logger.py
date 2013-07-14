import envoy
import gspread
import urllib2
import re
import time
import threading
import logging
from datetime import datetime


GOOGLE_LOGIN = '...'
GOOGLE_PASSWORD = '...'
SPREADSHEET_NAME = 'DHT22'
COMMAND_TO_RUN = "sudo ./dht_reader"


logging.basicConfig(level=logging.DEBUG, filename='/tmp/dht_logging_app.log')


class SpreadsheetHandler:
    SHEET_TITLES = ('VALUES', 'ERRORS')
    SHEETS_COLUM_TITLES = (('TIMESTAMP', 'TEMP', 'HUM'),
                           ('TIMESTAMP', 'ERROR_CODE', 'ERROR_DESC'))

    def __init__(self):
        gsconnect = gspread.login(GOOGLE_LOGIN, GOOGLE_PASSWORD)
        self.spreadsheet = gsconnect.open(SPREADSHEET_NAME)

    def prepare_speradsheet(self):
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
        values = self.spreadsheet.worksheet(SpreadsheetHandler.SHEET_TITLES[0])
        values_to_add = [datetime.now(), temperature, humidity]
        logging.info('Trying to add a value')
        values.append_row(values_to_add)
        logging.info('Trying to add a value - SUCCESS')

    def add_error(self, error_code, error_desc,):
        values = self.spreadsheet.worksheet(SpreadsheetHandler.SHEET_TITLES[1])
        values_to_add = [datetime.now(), error_code, error_desc]
        logging.info('Trying to add an error')
        values.append_row(values_to_add)


class DHTReader:

    def __init__(self):
        self.spreadsheet_handler = SpreadsheetHandler()

    def form_result(self, response_dht):
        results = [elem.replace('= ', '') for elem in re.findall("= [0-9.]+",
                                                                 response_dht)]
        assert len(results) == 2
        return results

    def try_read(self):
        logging.info('Trying to read')
        response = envoy.run(COMMAND_TO_RUN, timeout=2)

        if response.status_code == 0:
            try:
                self.spreadsheet_handler.add_measurement(
                                        *self.form_result(response.std_out))
            except AssertionError, e:
                logging.exception(e)
                self.spreadsheet_handler.add_error(response.status_code,
                                                   response.std_out)
        else:
            self.spreadsheet_handler.add_error(response.status_code,
                                               response.std_err)

    def run(self):
        i = 1
        while True:
            logging_TXT = "Measure # %d"
            logging.info(logging_TXT % i)
            self.try_read()
            time.sleep(15)

if __name__ == '__main__':
    logging.info('DHT_LOGGER_APP STARTS NOW!')
    s = SpreadsheetHandler()
    s.prepare_speradsheet()
    d = DHTReader()
    threading.Thread(target=d.run).start()
