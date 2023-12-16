class GuildData:
    def __init__(self, name, id):
        self.name = str(name)
        self.id = int(id)
        self.messages = []

    def addMessage(self, message):
        self.messages.append(message)