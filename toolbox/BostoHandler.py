import logging
class BostoHandler:
    def __init__(self, client, method='msg'):
        self.client = client

    async def Message(self, message, *args):
        dm = not message.guild
        msgContent = tuple(message.content.split(' '))
        ctx = await self.client.get_context(message)
        
        
        if ctx.prefix == self.client.command_prefix:
            logging.info(message.author.name + "#" + message.author.discriminator  + " -> " + message.content)


        # Trigger commands in DM channel without prefix needed
        if dm:
            
            if ctx.prefix == None and msgContent[0].lower() in [str(i) for i in self.client.commands]:
                logging.info(message.author.name + "#" + message.author.discriminator  + " -> " + message.content)
                await ctx.invoke(self.client.get_command(message.content), *msgContent[1:])
                return


        await self.client.process_commands(message) #Send Message to automatic command sender
        
        

    async def Reaction(self, payload):
        pass
    
    #Note: This should be the controller in MVC!