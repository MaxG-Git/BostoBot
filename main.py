import os
import json
import BostoBot.startup as app
import logging
import sys
import BostoBot.creds as creds

if __name__ == "__main__":
    COGS = os.listdir('./BostoBot/controller/')
    app.run(COGS)