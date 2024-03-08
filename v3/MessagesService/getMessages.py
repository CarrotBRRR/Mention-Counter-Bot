import discord
import json

class getMessages:
    def __init__(self, token):
        self.token = token
        self.client = discord.Client()

    async def retrieve_messages(self, channel_id, limit=None):
        channel = self.client.get_channel(channel_id)
        messages = await channel.history(limit=limit).flatten()
        message_data = []
        for message in messages:
            message_data.append({
                'id': message.id,
                'content': message.content,
                'author': message.author.name,
                'timestamp': message.created_at.timestamp()
            })
        return message_data.reverse()

    async def save_messages_to_json(self, channel_id, limit=None, filename='messages.json'):
        messages = await self.retrieve_messages(channel_id)
        with open(filename, 'w') as file:
            json.dump(messages, file)

    def run(self):
        @self.client.event
        async def on_ready():
            print('Logged in as', self.client.user.name)
        
        self.client.run(self.token)