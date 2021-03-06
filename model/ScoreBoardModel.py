import logging
import os
import BostoBot.toolbox.BostoGeneric as BostoGeneric
from BostoBot.toolbox.BostoGeneric import BostoResult
import BostoBot.model.Model as Model


class ScoreBoardModel(Model.Model):
    
    def __init__(self, client):
        super().__init__(client)

   
    async def getLocalScoreBoard(self, path):
        import json
        with open(path) as f:
            settings = json.load(f)
        sbChannel = self.client.get_channel(settings['score_board']['channel'])
        return await sbChannel.fetch_message(settings['score_board']['message'])


    @Model.BostoConnected
    def getScoreBoard(self, **kwargs):
        emojiValue = {key: emoji['value'] for key, emoji in self.BostoPoints.items()}
        return kwargs['connection'].getScoreBoard(emojiValue)    
 
    
   

        
    

