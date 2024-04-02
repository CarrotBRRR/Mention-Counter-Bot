import json
import os

class Config:
    def __init__(self, name, id):
        """Initializes the Config object and 
        loads the guild's configuration from a file if it exists, 
        otherwise creates a new configuration file"""

        # Create the guild folder if it doesn't exist
        if not os.path.exists(str(id)):
            os.mkdir(f'./data/{str(id)}')
            os.makedirs(f'./data/{str(id)}', exist_ok=True)

        # Load the guild's configuration from a file if it exists
        try:
            with open(f'{id}/config.json', 'r') as f:
                config = json.load(f)

                self.name = config['name']
                self.id = config['id']
                self.qchannel = config['qchannel']
                self.lb = {
                    'channel': config['lb']['channel'],
                    'message': config['lb']['message']
                }
        # Create a new configuration file if it doesn't exist
        except FileNotFoundError:
            self.name = str(name)
            self.id = int(id)
            self.qchannel = config['qchannel']
            self.lb = {
                'channel': 0,
                'message': 0
            }

            self.save_config()

    def save_config(self):
        config = {
            'name': self.name,
            'id': self.id,
            'qchannel': self.qchannel,
            'lb': {
                'channel': self.lb['channel'],
                'message': self.lb['message']
            }
        }

        with open(f'{self.id}/config.json', 'w') as f:
            json.dump(config, f, indent=4)
