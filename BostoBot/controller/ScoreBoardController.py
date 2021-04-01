import discord
from discord.ext import commands
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.ScoreBoardModel import ScoreBoardModel
import BostoBot.toolbox as IsPy
from tabulate import tabulate
import BostoBot.creds as creds


class ScoreBoardController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, ScoreBoardModel)


    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.check(Controller.EnsureBostoBase)
    async def sbSet(self, ctx, *args):
        
        settings = ScoreBoardModel.getSettings()

        settings['score_board']['channel'] = ctx.message.channel.id
        if any(arg.isdigit() for arg in args):
            settings['score_board']['message'] = IsPy.first(args, settings['score_board']['message'], lambda arg: arg.isdigit(), int) 
        else:
            sbMessage = await ctx.send("Score Board")
            settings['score_board']['message'] = sbMessage.id 

        ScoreBoardModel.setSettings(settings)

        
        await ctx.message.delete()


    
    
    @commands.command(hidden=True)
    @commands.check(Controller.EnsureBostoBase)
    @sbSet.after_invoke
    async def sbUpdate(self, ctx=None, *args):
        sbMessage = await self.model.getLocalScoreBoard("{}/settings.json".format(creds.CONFIG['LOCAL_FILE_STORAGE']))
        data = self.model.getScoreBoard()
        headers = ["Ranking", "User", "BP Value"]
        table = tabulate(data, headers, tablefmt="pretty")
        embed = discord.Embed(title="Bosto ScoreBoard", 
        description="```\n"+table+"\n```", 
        color=0x0000FF,
        )
        await sbMessage.edit(content=None, embed=embed)


    
def setup(client):
    client.add_cog(ScoreBoardController(client))