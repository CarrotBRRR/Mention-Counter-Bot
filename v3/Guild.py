"""
This file contains the Guild class
used to store information about the guild and its channels.

Implments GuildConfig and Channels classes
"""
import os
from GuildConfig import Config
from Channels import Channels

class Guild:
    def __init__(self, guild):
        """Initializes the Guild object and sets up the guild folder and channels object"""
        self.config = Config(guild.name, guild.id)
        self.guild = guild
        self.guild_folder = f'./data/{guild.id}'
        self.channels = Channels(guild)

        if not os.path.exists(self.guild_folder):
            os.mkdir(self.guild_folder)
            os.makedirs(self.guild_folder, exist_ok=True)

    def get_guild(self):
        return self.guild