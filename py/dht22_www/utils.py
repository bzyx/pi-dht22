import time
import threading
from daemon import SpreadsheetHandler


class DataKeeper(object):
    """This class works like a dummy "cache"
    cause google drive api for read is very slow.
    Unfortunately this don't works like i want :-)
    """

    TIME_TO_UPDATE = 300  # 5 min

    def __init__(self, data_amout=40):
        """ This class should work in 
        background process and update it's data
        in cycle of 5 minutes, switching the data after complete
        """
        self.s = SpreadsheetHandler()
        self.data_amount = data_amout
        self.currentData = ()
        self.futureData = None
        #threading.Thread(target=self.run).start()
        t = threading.Thread(target=self.run())
        t.setDaemon(True)
        t.start()

    def _updateData(self):
        """Call gspread API to download new data"""
        self.futureData = self.s.get_last_num_values(self.data_amount)

    def getData(self):
        """Get the current data"""
        if len(self.futureData) == self.data_amount:
            self.currentData = self.futureData
            self.futureData = None

        return self.currentData

    def run(self):
        """Run in thread and wait"""
        while True:
            self._updateData()
            time.sleep(DataKeeper.TIME_TO_UPDATE)
