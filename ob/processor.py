import csv
import os


class DataProcessor(object):

    def __init__(self, data_dir, dates, format="raw"):
        """Initializes a data processor over different data formats
        
        The data processor is a utility for parsing orderbook
        data in different formats. The two types of formats
        supported are raw data (every order) and snapshots.
        These formats need to be specified along with the data
        directory and the dates of interest.
        
        Arguments:
            data_dir {str} -- Directory of data files
            dates {array} -- Array of dates to cross-reference
        
        Keyword Arguments:
            format {str} -- data format (raw or snapshot) (default: {"raw"})
        """
        super(DataProcessor, self).__init__()
        self.data_dir = data_dir
        self.date = dates[0]
        self.time = 0

        for file in os.scandir(data_dir):
            if str(self.date) in file.name:
                with open("{}/{}".format(data_dir, file.name)) as f:
                    self.f = [line for line in csv.reader(f, delimiter=",")]
                    self.fields = self.f[0]
                    break

        

    def next_file_pointer(self):
        pass

    def next(self):
        pass
