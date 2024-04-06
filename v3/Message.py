"""
A class to represent a message
"""
import json

class Message:
    def __init__(self, message):
        """Create a message object and store the message's content, author, and attachments"""
        self.message = message

        self.id = message.id
        self.author = message.author
        self.content = message.content

    async def load_message(self, id, author, content):
        """Create a message object and store the message's content, author, and attachments"""
        self.message = None

        self.id = id
        self.author = author
        self.content = content

    def get_message(self):
        return self.message

    def get_content(self):
        return self.message.content

    def get_author(self):
        return self.message.author

    def get_id(self):
        return self.message.id
    
    def toObject(self):
        return {
            'id': self.id,
            'author': self.author.id,
            'content': self.content,
            'message': self.message
        }
    
    def toJSON(self):
        return json.dumps(self.toObject())
