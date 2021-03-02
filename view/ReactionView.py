from BostoBot.view.View import View

class ReactionView(View):

    def __init__(self, client):
        super().__init__(client)

    @staticmethod
    async def selfReactionFailure(sendable, emoji):
        await View.info(sendable, f"You cant give yourself a {str(emoji)}!")
    
    @staticmethod
    async def fundsFailure(sendable, emojiName, emojiCode):
        await View.error(sendable, f"Looks like you are out of {emojiName}s {emojiCode}\nUse the `b/wallet` Command to see your {emojiCode}s\nUse the `b/buy` command to get more {emojiCode}")

    @staticmethod
    async def unknownAddFailure(sendable, emojiName):
        await View.error(sendable, f"Looks like you something went wrong when adding a {emojiName}")
    
    @staticmethod
    async def addSuccess(sendableReacter, sendableAuthor, emojiCode, value, fromName):
        if value > 1:
            await View.send(sendableReacter, f"A {emojiCode} has been removed from your wallet")
        await View.send(sendableAuthor, f"A Wild {emojiCode} has appeared in your wallet *from {fromName}*")

    @staticmethod
    async def attemptedRefundFailure(sendable, emojiCode, emojiName, messageAuthor, link):
        await View.info(sendable, f"You tried to remove a {emojiCode} from *{messageAuthor}'s* message!\n{emojiName}'s are **not** refundable!\n*(you can add the {emojiName} emoji back to {messageAuthor}'s **original message** if you would like for free)*\nOriginal Message: {link}")

        