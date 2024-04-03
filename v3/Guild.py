"""
This file contains the Guild class
used to store information about the guild and its channels.

Implments GuildConfig and Channels classes
"""
import os
from GuildConfig import Config
from Channels import Channels
from Logger import Logger

class Guild:
    def __init__(self, guild):
        """Initializes the Guild object and sets up the guild folder and channels object"""
        self.guild = guild

        self.config = Config(guild.name, guild.id)
        self.guild_folder = f'./data/{guild.id}'

        self.channels = Channels(guild)
        self.logs = Logger(guild)

        if not os.path.exists(self.guild_folder):
            os.mkdir(self.guild_folder)
            os.makedirs(self.guild_folder, exist_ok=True)

    def get_guild(self):
        return self.guild
    
    def get_config(self):
        return self.config
    
    def get_channels(self):
        return self.channels
    
    def get_logs(self):
        with open(self.logs, 'r') as log_file:
            return log_file
    
    def get_guild_folder(self):
        return self.guild_folder
    
    def get_guild_id(self):
        return self.guild.id
    

