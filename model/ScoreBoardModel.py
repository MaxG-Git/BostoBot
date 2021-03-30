import logging
import os
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
        return kwargs['connection'].getScoreBoard()
 
    
   

        
    

