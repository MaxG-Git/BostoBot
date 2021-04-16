from BostoBot.view.View import *
import discord 
import asyncio
import logging

class PointView(View):

    def __init__(self, client):
        super().__init__(client)


    async def sendWallet(self, user, image, tip=None):
        content="Your wallet:"
        await user.send(content=content, file=image)
        if tip != None:
            await user.send(content=tip)



    
    async def tradeGetSelected(self, ctx, emojiList):
        embed = discord.Embed(title="Trade Order", 
        description="**Select The Bosto-Emoji that you want**", 
        color=0xFF5733,
        )
        embed.set_footer(text="(or ❌ to cancel)")
        
        action = Action(
            check=lambda payload: payload.user_id == ctx.message.author.id, 
            reaction_options= emojiList,
            action='raw_reaction_add',
        )
        
        return await self.getResponce(ctx, 
            embed = embed,
            actions = action,
            )
    
    
    
    async def tradeGetCost(self, ctx, selected, selectedVal, availPayments, url):
        embed = discord.Embed(title="Trade Order", 
        description=f"Please Choose what you want to **offer me** for {selected}\n", 
        color=0xFF5733
        )
        embed.set_footer(text="(or ❌ to cancel)")
        embed.set_thumbnail(url=url)
        embed.add_field(name="Trading Return",
        value= f"{selected} *{selectedVal} BP each*", 
        inline=False
        )

        action = Action(
            check=lambda payload: payload.user_id == ctx.message.author.id, 
            reaction_options= availPayments,
            action='raw_reaction_add'
        )

        return await self.getResponce(ctx,
            actions = action,
            embed=embed
            )
        
    async def tradeGetQuant(self, ctx, selected, selectedVal, costEmojiCode, costEmojiVal, costEmojiTotal, availOptions, availOptionsString, url):
        embed = discord.Embed(title="Trade Order", 
        description=f"Please respond with **how many** {selected} you want\n\nYou have {costEmojiTotal} {costEmojiCode}\nYou can trade a total of {availOptionsString} {selected}\n", 
        color=0xFF5733
        )
        embed.set_thumbnail(url=url)
        embed.set_footer(text=f"Respond with given options or \"cancel\"")
        embed.add_field(name="Trading Return",
         value= f"{selected} *{selectedVal} BP each*", 
         inline=True
         )
        embed.add_field(name="Trading Cost",
         value= f"{costEmojiCode} *{costEmojiVal} BP each*", 
         inline=True
         )

        messageAction = Action(
            check=lambda msg: msg.author.id == ctx.message.author.id and (str(msg.content) in availOptions or str(msg.content).lower() == "cancel"),
            timeout=55.0,
            filter_reaction_options = False
        )

        reactionAction = Action(
            check=lambda payload: payload.user_id == ctx.message.author.id,
            timeout=55.0,
            reaction_options= ["❌"],
            action='raw_reaction_add'
        )
       
        return await self.getResponce(ctx, 
            actions=[messageAction, reactionAction],
            embed=embed,
            )
    
    async def tradeReceipt(self, message, selected, selectedQuant, costEmojiCode, costEmojiQuant, tip):

        embed = discord.Embed(title="Trade Receipt", 
        description=f"Trade Completed!\nYou can check your new points with the `b/wallet` command",
        color=0x149414
        )

        embed.set_thumbnail(url="https://emoji.gg/assets/emoji/CheckMark.png")
        
        embed.add_field(name="Trading Return",
         value= f"{selected} × {selectedQuant}", 
         inline=True
         )
        embed.add_field(name="Trading Cost",
         value= f"{costEmojiCode} × {costEmojiQuant}", 
         inline=True
         )
        await message.edit(embed=embed, content=tip)
        