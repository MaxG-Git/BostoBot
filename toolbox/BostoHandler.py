import logging
class BostoHandler:
    def __init__(self, client, method='msg'):
        self.client = client

    async def Message(self, message, *args):
        dm = not message.guild
        
        # Trigger commands in DM channel without prefix needed
        if dm:
            ctx = await self.client.get_context(message)
            if ctx.prefix == None and message.content in [str(i) for i in self.client.commands]:
                await ctx.invoke(self.client.get_command(message.content), *args)
                return
                
            
           


        await self.client.process_commands(message) #Send Message to automatic command sender
        
        

    async def Reaction(self, payload):
        pass