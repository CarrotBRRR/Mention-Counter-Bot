"""
Global Logger that logs all events and messages to a single file
"""

import os
import datetime

class GlobalLogger:
    def __init__(self):
        """Initializes the GlobalLogger object and creates a log file with the current timestamp"""
        self.timestamp = datetime.datetime.now()

        self.folder = './data/logs'
        self.file = f'{self.timestamp.strftime("%Y-%m-%d_%H-%M-%S")}.log'
        self.filepath = f'{self.folder}/{self.file}'

        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)

    def log(self, message):
        print(f'{message}')
        with open(f'{self.folder}/{self.file}', 'a') as log_file:
            log_file.write(f'{message}\n')

    def done(self):
        print('Done!')
        with open(self.filepath, 'a') as log_file:
            log_file.write(f'Done!\n')