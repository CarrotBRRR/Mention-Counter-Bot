# Mention Counter Bot
Developed by: Dominic Choi (CarrotBRRR)

If you're wondering why the commits are directly onto the main branch, 
this is because I'm the only developer working on the bot.
so I don't need to make new branches, since I will never
get merge conflicts. I do make new branches when I do something that may break the bot, though

## Current Features
- Fill this out eventually

## TODO: 
### General
- **Add info about the bot in readme**

### Version 2.2
- **Timing Feature**
    - log time taken in console to retrieve quotes

- **q.commands**
    - send list of commands and descriptions

### Version 2.3
- **Message History Database**
    - Store IDs of all messages in message_history
        - Other functions must retrieve message via ID 
    - When requested, if not exists, make a cache of message history
        - ./data/guildid/message_history/channelid.json
    - if exists, must update on_delete and on_message
        - do not create on_message, because that will cause rate-limiting

### Version 3.X
- **Separate Classes**
  - Use an MVC Architecture, to separate the monolith
