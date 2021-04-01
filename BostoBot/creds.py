import os
import json
config = os.path.abspath("./config.json")
io = open(config, 'r')

if not CONFIG['USE_ENV_VARS']:
    CONFIG = json.load(io)
else:
    CONFIG = {
        'TOKEN': os.getenv('BOSTOBOT_TOKEN'),
        'MYSQL_HOST': os.getenv('BOSTOBOT_MYSQL_HOST'),
        'MYSQL_USER': os.getenv('BOSTOBOT_MYSQL_USER'),
        'MYSQL_PASS': os.getenv('BOSTOBOT_MYSQL_PASS'),
        'MYSQL_PORT': os.getenv('BOSTOBOT_MYSQL_PORT'),
        'MYSQL_DATABASE': os.getenv('BOSTOBOT_MYSQL_DATABASE'),
        'LOCAL_FILE_STORAGE': os.getenv('BOSTOBOT_LOCAL_FILE_STORAGE')
    }


