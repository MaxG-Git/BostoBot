import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult
import BostoBot.model.Model as Model


class ScoreBoardModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)

    def generateTable(self, data):
        from tabulate import tabulate
        headers = ["Ranking", "User", "Total Point Value"]
        table = tabulate(data, headers, tablefmt="pretty")
        table = table.replace("\n", "`\n`")
        return table
   
    async def getLocalScoreBoard(self, path):
        import json
        with open(path) as f:
            settings = json.load(f)
        sbChannel = self.client.get_channel(settings['score_board']['channel'])
        return await sbChannel.fetch_message(settings['score_board']['message'])


    @Model.BostoConnected
    def getScoreBoard(self, **kwargs):
        emojiValue = {key: emoji['value'] for key, emoji in self.client.BostoDict.items()}
        return kwargs['connection'].getScoreBoard(emojiValue)    
 
    
   

        
    

