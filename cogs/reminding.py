"""
Remindering System

This cog aims to provide an interface for the bot to implement
a type of reminder saving and pinging system.
"""

from discord.ext import commands
from utils import formats
import config
import asyncio
import pprint

class Reminding(commands.Cog, name = 'reminding'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases = ['r'])
    async def remind(self, ctx):
        """Creates a reminder event"""

        # Try to obtain who to remind
        try:
            msg = ctx.message.content.split(maxsplit=1)
            user = await self.bot.fetch_user(int(msg[1][3:-1]))
        except ValueError as e:
            exception = f"{type(e).__name__}: {e}"
            user = 'me'
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(exception)
            return
        else:
            print(f'Successfully retrieved {user.name}')

        # Internal print to tell about the author and who to reminder
        if type(user) == str and user.lower() == 'me':
            user = ctx.message.author
        if user == ctx.message.author:
            print(f'{user.name} wanted me to remind him.')
        else:
            print(f'{ctx.message.author} wanted me to remind {user.name}')

        def proper_reply(reply):
            "Ensures that the reply came from the original sender"
            return reply.author == ctx.message.author and reply.content.isprintable()

        # Prompt the user regarding what the reminder must be about
        await ctx.channel.send(f'What do you want?')
        try:
            reply = await self.bot.wait_for('message', check = proper_reply, timeout = 30.0)
            label = reply.content
            print(f'It was about his "{label}" agenda.')
        except asyncio.TimeoutError:
            print(f'But he was taking too long though, so I had to ignore him.')
            return await ctx.channel.send(config.MSG_TIMEOUT_ERROR)
        
        # Prompt the user regarding when the reminder must come
        await ctx.channel.send(f'When is this due?')
        try:
            print('I\'m now awaiting the response')
            reply = await self.bot.wait_for('message', check = formats.is_proper_date_time, timeout = 10)
            remind_date_time = reply.content
        except asyncio.TimeoutError:
            return await ctx.channel.send(config.MSG_TIMEOUT_ERROR)
        else:
            print(f'It was due on {remind_date_time}')

        await ctx.channel.send(f'Okay! Will do.')
    

def setup(bot):
    bot.add_cog(Reminding(bot))