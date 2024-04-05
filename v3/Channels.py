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

class Channels:
    def __init__(self, guild):
        """Initializes the Channels object and loads the messages from a file if it exists,"""
        self.guild_folder = f'./data/{guild.id}'
        self.channels = {}
        try:
            self.load()

        except FileNotFoundError:
            for channel in guild.channels:
                self.channels[channel.id] = []
            self.save()

    ### Message Functions ###
    def delete_message(self, channel_id, message_id):
        """Deletes a message from the channel"""
        self.channels[channel_id] = [message for message in self.channels[channel_id] if message.id != message_id]
        self.save()

    def add_message(self, channel_id, message):
        """Adds a message to the channel"""
        self.channels[channel_id].append(message.id)
        self.save()

    def get_messages(self, channel_id):
        """Gets all the messages from the channel"""
        return self.channels[channel_id]
    
    def get_message(self, channel_id, message_id):
        """Gets a message from a specified channel"""
        for message in self.channels[channel_id]:
            if message.id == message_id:
                return message

    def get_message(self, message_id):
        """Searches all channels for a message with the specified ID"""
        for channel_id in self.channels:
            return self.get_message(channel_id, message_id)

    ### Save/Load Functions ###
    def save(self):
        """Saves the message IDs of all channels to a file"""
        # Create the guild folder if it doesn't exist
        if not os.path.exists(self.guild_folder):
            os.mkdir(self.guild_folder)
            os.makedirs(self.guild_folder, exist_ok=True)

        # Save the channels to a file
        with open(f'{self.guild_folder}/messages.json', 'w') as f:
            json.dump(self.messages, f, indent=4)

    def load(self):
        """Loads the message IDs of all channels from a file"""
        with open(f'{self.guild_folder}/messages.json', 'r') as f:
            self.messages = json.load(f)