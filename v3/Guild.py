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
        self.guild = guild

        self.config = Config(guild.name, guild.id)
        self.guild_folder = f'./data/{guild.id}'

        self.channels = None

        if not os.path.exists(self.guild_folder):
            os.mkdir(self.guild_folder)

    @classmethod
    async def create_guild(self, guild):
        """Creates a new Guild object"""
        self.channels = await Channels.create_channels(guild)
        return Guild(guild)

    def get_guild(self):
        return self.guild
    
    def get_config(self):
        return self.config
    
    def get_channels(self):
        return self.channels
    
    def get_guild_folder(self):
        return self.guild_folder
    
    def get_guild_id(self):
        return self.guild.id
    
    def get_channels(self):
        return self.channels

    def get_random_message(self, channel_id=None):
        """Returns a random message from the a channel.
        Default channel is quotes channel if none is provided"""
        if channel_id is None:
            if self.config['qchannel'] != 0:
                return
            else:
                channel_id = self.config['qchannel']

        return self.channels.get_random(channel_id)