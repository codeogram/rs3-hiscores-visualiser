import logging

class MyLogger:
    """
    Usage: MyLogger.logger.<level>/('<log_message>')
    This logger will log everything (DEBUG and above) to both the console and to the log file.
    """

    def __init__(self, file_name, log_file_path):
        self.file_name = file_name
        self.log_file_path = log_file_path

        # logger
        self.logger = logging.getLogger(self.file_name)
        self.logger.setLevel(logging.DEBUG) # by default it will log DEBUG and above

        # logger file handler (for ERROR and above)
        self.file_handler = logging.FileHandler(self.log_file_path)
        self.file_handler.setFormatter(
            logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s') # format of log lines
        )
        self.logger.addHandler(self.file_handler)

        # logger stream/console handler
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(
            logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        )
        self.logger.addHandler(self.stream_handler)