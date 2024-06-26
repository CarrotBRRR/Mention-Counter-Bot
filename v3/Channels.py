"""
Channel class for managing messages in a channel
Messages are stored as an ID in a dictionary with the channel ID as the key

channels = {
    "channel1" : [message1, message2, ...],
    "channel2" : [message1, message2, ...],
}
"""
import json
import os
import random as rand
import discord

from Message import Message

class Channels:
    def __init__(self, guild):
        """Initializes the Channels object and loads the messages from a file if it exists,"""
        self.guild_folder = f'./data/{guild.id}'
        self.channels= {}

    @classmethod
    async def create_channels(self, guild):
        """Creates a new Channels object"""
        channels = Channels(guild)

        try:
            channels.load()

        except FileNotFoundError:
            for channel in guild.channels:
                try:
                    await channels.add_channel(channel)

                except discord.Forbidden:
                    pass
            
            channels.save()
            return channels
        
    ### Message Functions ###
    def delete_message(self, channel_id, message):
        """Deletes a message from the channel"""
        self.channels[channel_id] = [m for m in self.channels[channel_id] if m.get_id() != message.id]
        self.save()

    def add_message(self, channel_id, message):
        """Adds a message to the channel"""
        self.channels[channel_id].append(Message(message))
        self.save()

    def get_messages(self, channel_id):
        """Gets all the message ids from the channel"""
        return self.channels[channel_id]

    def get_random(self, channel_id):
        """Returns a random message id from the channel"""
        return rand.choice(self.channels[channel_id])
    
    ### Channel Functions ###
    async def add_channel(self, channel):
        """Initializes a channel with an empty list of messages"""
        try:
            channel.history(limit = 1)
        except AttributeError:
            return
        except discord.Forbidden:
            return

        temp = []
        async for message in channel.history(limit=None):
            temp.append(Message(message))
        if temp != []:
            self.channels[channel.id] = temp

        self.save()

    def remove_channel(self, channel_id):
        """Removes a channel from the dictionary"""
        self.channels.pop(channel_id)
        self.save()

    ### Save/Load Functions ###
    def save(self):
        """Saves the message IDs of all channels to a file"""
        # Create the guild folder if it doesn't exist
        if not os.path.exists(self.guild_folder):
            os.makedirs(self.guild_folder, exist_ok=True)

        # Save the channels to a file
        with open(f'{self.guild_folder}/channels.json', 'w') as f:
            data = {}
            for channel in self.channels:
                messages = []
                for message in self.channels[channel]:
                    messages.append(message.toObject())
                data[channel] = messages

            json.dump(data, f, indent=4)

    async def load(self):
        """Loads the message IDs of all channels from a file"""
        with open(f'{self.guild_folder}/channels.json', 'r') as f:
            data = json.load(f)

            for channel, messages in data:
                messages = []
                for message in messages:
                    messages.append(Message(message))
                self.channels[channel] = messages