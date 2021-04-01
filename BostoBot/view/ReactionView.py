from BostoBot.view.View import *
import discord

class ReactionView(View):

    def __init__(self, client):
        super().__init__(client)

    @staticmethod
    async def selfReactionFailure(sendable, emoji):
        await View.info(sendable, f"You cant give yourself a {str(emoji)}!")
    
    
    async def fundsFailure(self, sendable, emojiName, emojiCode, showTips):
        msg = f"Looks like you are out of {emojiName}s {emojiCode}"
        if showTips:
            msg +=  f"\nUse the `wallet` Command to see your {emojiCode}s\nUse the `trade` command to get more {emojiCode}"
        await View.error(sendable, msg)

    @staticmethod
    async def unknownAddFailure(sendable, emojiName):
        await View.error(sendable, f"Looks like you something went wrong when adding a {emojiName}")
    
    @staticmethod
    async def addSuccess(sendableReacter, sendableAuthor, emojiCode, value, fromName, reacterNotify, authorNotify):
        if value > 1 and reacterNotify:
            await View.send(sendableReacter, f"A {emojiCode} has been removed from your wallet")
        if authorNotify:
            await View.send(sendableAuthor, f"A Wild {emojiCode} has appeared in your wallet *from {fromName}*")

    
    async def attemptedRefundFailure(self, sendable, message, emojiCode, emojiName, link):
        await sendable.send(content=f"You tried to remove a {emojiCode} from *{message.author}'s* message: ")
        embed = discord.Embed(
        url=link,
        description="> " + message.content, 
        )
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        await sendable.send(embed=embed)
        await sendable.send(content=f"{emojiName}'s are **not** refundable!\n*(you can add the {emojiName} emoji back to {message.author.name}'s **original message** if you would like for free)*\nOriginal Link: "+link)
        #await View.info(sendable, f"You tried to remove a {emojiCode} from *{message.author.name}'s* message!\n{emojiName}'s are **not** refundable!\n*(you can add the {emojiName} emoji back to {messageAuthor}'s **original message** if you would like for free)*\nOriginal Message: {link}")

        