class GuildInfo:
    def __init__(self, name, id):
        self.name = str(name)
        self.id = int(id)
        self.messages = []

    def setMessages(self, messages):
        self.messages = messages

    def addMessage(self, message):
        self.messages.append(message)

    def hasMessages(self):
        if len(self.messages) >= 1:
            return True
        else:
            return False