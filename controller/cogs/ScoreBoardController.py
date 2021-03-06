import discord
from discord.ext import commands
import logging
import BostoBot.controller.Controller as Controller
from BostoBot.model.ScoreBoardModel import ScoreBoardModel
import BostoBot.toolbox.SuperPy.iterable as IsPy
from tabulate import tabulate


class ScoreBoardController(Controller.Controller):
    
    def __init__(self, client):
        super().__init__(client, ScoreBoardModel)


    @commands.command()
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


    
    
    @commands.command()
    @commands.check(Controller.EnsureBostoBase)
    @sbSet.after_invoke
    async def sbUpdate(self, ctx=None, *args):
        sbMessage = await self.model.getLocalScoreBoard("/usr/src/app/data/settings.json")
        data = self.model.getScoreBoard()
        headers = ["Ranking", "User", "BP Value"]
        table = tabulate(data, headers, tablefmt="pretty")
        #table =  "`" + table.replace("\n", "`\n`") +"`"
        
        #emjNum = self.model.BostoBase['code'][len(self.model.BostoBase['name']) + 3:len(self.model.BostoBase['code'])-1]
       
        embed = discord.Embed(title="Bosto ScoreBoard", 
        description="```\n"+table+"\n```", 
        color=0x0000FF,
        )
        await sbMessage.edit(content=None, embed=embed)

        #await sbMessage.edit(content="`" +table +"`")

    
def setup(client):
    client.add_cog(ScoreBoardController(client))