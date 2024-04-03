"""
Functions to log the messages and 
events of the bot of a specific guild to a file
"""

import os
import datetime

class Logger:
    def __init__(self, guild):
        self.timestamp = datetime.datetime.now()
        self.file = f'{self.timestamp.strftime("%Y-%m-%d_%H-%M-%S")}.log'
        self.guild_folder = f'./data/{guild.id}/logs'

        if not os.path.exists(self.guild_folder):
            os.makedirs(self.guild_folder, exist_ok=True)

    def log(self, message):
        print(f'{message}')
        with open(self.file, 'a') as log_file:
            log_file.write(f'{message}\n')

    def done(self):
        print('Done!')
        with open(self.file, 'a') as log_file:
            log_file.write(f'Done!\n')