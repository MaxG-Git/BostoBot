import os
import sys

if '-env' not in sys.argv:
    import json
    config = os.path.abspath("./config.json")
    CONFIG = json.load(open(config, 'r'))
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




