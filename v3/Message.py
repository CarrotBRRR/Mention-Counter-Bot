"""
A class to represent a message
"""

class Message:
    def __init__(self, message):
        """Create a message object and store the message's content, author, and attachments"""
        self.id = message.id

        self.message = message
        self.author = message.author

        self.content = message.content
        self.attachments = message.attachments

    def get_message(self):
        return self.message

    def get_content(self):
        return self.message.content

    def get_author(self):
        return self.message.author

    def get_id(self):
        return self.message.id

    def get_attachments(self):
        return self.message.attachments
