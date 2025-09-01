from dataclasses import dataclass, field
import discord

@dataclass
class GuildInfo:
    name: str
    id: int
    messages: list[discord.Message] = field(default_factory=list)

    def setMessages(self, messages):
        self.messages = messages

    def addMessage(self, message):
        self.messages.append(message)

    def hasMessages(self) -> bool:
        return bool(self.messages)
