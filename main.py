import os
import json
import BostoBot.startup as app

if __name__ == "__main__":
    COGS = os.listdir('./BostoBot/controller/cogs/')
    app.run(COGS)