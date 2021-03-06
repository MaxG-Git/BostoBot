from BostoBot.view.View import View
import discord 
import asyncio
import logging

class PointView(View):

    def __init__(self, client):
        super().__init__(client)

    
    async def tradeGetSelected(self, ctx, emojiList):
        embed = discord.Embed(title="Trade Order", 
        description="**Select The Bosto-Emoji that you want**", 
        color=0xFF5733,
        )
        embed.set_footer(text="(or ❌ to cancel)")
        
        action = self.responceAction(
            check=lambda payload: payload.user_id == ctx.message.author.id, 
            reactionOptions= emojiList,
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
        value= f"{selected} (value {selectedVal})", 
        inline=False
        )

        action = self.responceAction(
            check=lambda payload: payload.user_id == ctx.message.author.id, 
            reactionOptions= availPayments,
            action='raw_reaction_add'
        )

        return await self.getResponce(ctx,
            actions = action,
            embed=embed
            )
        
    async def tradeGetQuant(self, ctx, selected, selectedVal, costEmojiCode, costEmojiVal, costEmojiTotal, availOptions, availOptionsString, url):
        embed = discord.Embed(title="Trade Order", 
        description=f"Please respond with **how many** {selected} you want\n\nYou have {costEmojiTotal} {costEmojiCode}\nYou can create a total of {availOptionsString} {selected}\n", 
        color=0xFF5733
        )
        embed.set_thumbnail(url=url)
        embed.set_footer(text=f"Respond with given options or \"cancel\"")
        embed.add_field(name="Trading Return",
         value= f"{selected} (value {selectedVal})", 
         inline=True
         )
        embed.add_field(name="Trading Cost",
         value= f"{costEmojiCode} (value {costEmojiVal})", 
         inline=True
         )

        messageAction = self.responceAction(
            check=lambda msg: msg.author.id == ctx.message.author.id and (str(msg.content) in availOptions or str(msg.content).lower() == "cancel"),
            timeout=55.0,
        
        )

        reactionAction = self.responceAction(
            check=lambda payload: payload.user_id == ctx.message.author.id,
            timeout=55.0,
            reactionOptions= ["❌"],
            action='raw_reaction_add'
        )
       
        return await self.getResponce(ctx, 
            actions=[messageAction, reactionAction],
            embed=embed,
            )
    
    async def tradeReceipt(self, message, selected, selectedQuant, costEmojiCode, costEmojiQuant):
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
        await message.edit(embed=embed, content=None)

        


    
    
'''
msg1 = await ctx.send(f"*Trading with {costEmojiCode} (value: {costEmojiVal})*  ➡  *Trading for {selected} (value: {selectedVal})*\nYou have {costEmojiTotal} {costEmojiCode}\nYou can create a total of {availOptionsString} {selected}")
        
        msg2, quantityResponce = await self.view.getResponce(ctx, 
            check=lambda msg: msg.author.id == ctx.message.author.id and (str(msg.content) in availOptions or str(msg.content).lower() == "cancel"),
            question= f"Please respond with how many {selected} to create *(or `cancel` to cancel)*",
            timeout=30.0,
            clearReactions=False,
            )
'''