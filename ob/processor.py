import csv
import os


class DataProcessor(object):

    def __init__(self, data_dir, dates, exchange, data_format="raw"):
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
            data_format {str} -- data format (raw or snapshot)
                                    (default: {"raw"})
        """
        super(DataProcessor, self).__init__()
        self.data_dir = data_dir
        self.exchange = exchange
        self.data_format = data_format
        self.dates = dates
        self.date_index = 0
        self.line = 0
        self.time = 0
        self.fields = []

        self.initialize()

    def next_file_pointer(self):
        pass

    def curr(self):
        return self.f

    def next(self, count=1):
        self.line += count
        entries = []
        for i in range(count):
            if self.exchange == "GEMINI":
                order_entry = OrderEntry(self.parse_gemini(next(self.f)))
            else:
                raise ValueError("Invalid exchange")

            entries.append(order_entry)

        return entries if len(entries) > 1 else entries[0]

    def parse_gemini(self, data):
        """Parses gemini raw orderbook data

        Example fields for raw ETHUSD:
        ['Event ID', 'Event Date', 'Event Time', 'Event Millis',
         'Order ID', 'Execution Options', 'Event Type', 'Symbol',
         'Order Type', 'Side', 'Limit Price (USD)',
         'Original Quantity (ETH)', 'Gross Notional Value (USD)',
         'Fill Price (USD)', 'Fill Quantity (ETH)',
         'Total Exec Quantity (ETH)', 'Remaining Quantity (ETH)',
         'Avg Price (USD)']

        Example for snapshot: alternating bid/ask/vols with
                              timestamp at the end

        Arguments:
            data {array} -- Array of order information
        """
        return {
            "event_id": data[0],
            "date": data[1],
            "time": data[2],
            "millis": data[3],
            "order_id": data[4],
            "evt_type": data[6],
            "symbol": data[7],
            "type": data[8],
            "side": data[9],
            "price": data[10],
            "volume": data[11],
            "avg_price": data[15]
        } if self.data_format == "raw" else self.parse_snapshot(data)

    def parse_snapshot(self, data):
        """Parses orderbook snapshot

        A parsing utility for orderbook snapshots where
        ask/bid orders are displayed in alternating order
        with a timestamp at the end

        Arguments:
            data {array} -- Array of alternating orders and volumes

        Returns:
            tuple -- prices and volumes or corresponding sides of book
        """
        timestamp = data[-1]
        data = data[:-1]
        ask_prices, ask_volumes = num(data[0::4]), num(data[1::4])
        bid_prices, bid_volumes = num(data[2::4]), num(data[3::4])
        return ask_prices, ask_volumes, bid_prices, bid_volumes, timestamp

    def process_file(self, path):
        """Process the file line by line using the file's returned iterator

        A file generator that parses new csv files
        and returns a generator/iterator over lines

        Arguments:
            path {str} -- file path to open

        Yields:
            {csvreader} -- a generator/iterator over a csv file
        """
        try:
            self.date_index += 1
            with open(path) as file_handler:
                while True:
                    yield next(csv.reader(file_handler, delimiter=","))
        except (IOError, OSError):
            print("Error opening / processing file")
        except StopIteration:
            # get next available file after previous finishes or finish
            if self.date_index < len(self.dates):
                self.initialize()
            else:
                self.finished = True

    def initialize(self):
        """Initializes file pointer to current date file

        Iterates over all dates and sets the file pointer
        to the file of the corresponding date at which we
        have not seen.

        Raises:
            ValueError -- [description]
        """
        for file in os.scandir(self.data_dir):
            if str(self.dates[self.date_index]) in file.name:
                self.f = self.process_file(
                    "{}/{}".format(self.data_dir, file.name))
                if self.data_format == "raw":
                    self.fields = next(self.f)
                elif self.data_format == "snapshot":
                    continue
                else:
                    raise ValueError("Invalid data format")


class OrderEntry(object):

    def __init__(self, order):
        super(OrderEntry, self).__init__()
        self.event_id = order["event_id"] if "event_id" in order else None
        self.date = order["date"] if "date" in order else None
        self.time = order["time"] if "time" in order else None
        self.millis = order["millis"] if "millis" in order else None
        self.order_id = order["order_id"] if "order_id" in order else None
        self.event_type = order["evt_type"] if "evt_type" in order else None
        self.symbol = order["symbol"] if "symbol" in order else None
        self.order_type = order["type"] if "type" in order else None
        self.side = order["side"] if "side" in order else None
        self.price = float(order["price"]) if "price" in order else None
        self.volume = float(order["volume"]) if "volume" in order else None
        self.avg_price = float(order["avg_price"]) if "avg_price" in order else None

    def __str__(self):
        return "{}, {}, {}".format(self.side, self.price, self.volume)

def num(l):
    return [float(x) for x in l]
