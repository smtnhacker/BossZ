"""
Remindering System

This cog aims to provide an interface for the bot to implement
a type of reminder saving and pinging system.
"""

import discord
from discord.ext import commands, tasks
from utils import formats, database
import config
import asyncio
import pprint

import datetime
from dateutil import tz

class Reminding(commands.Cog, name = 'reminding'):
    def __init__(self, bot):
        self.bot = bot
        self.remind_list = list()

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_reminding.start()
        self.remind_people.start()
    
    # Checks if there is any reminder at a given moment
    @tasks.loop(seconds=30.0)
    async def check_reminding(self):
        now = datetime.datetime.now(tz=tz.tzlocal())
        now = now.replace(second=0, microsecond=0)
        reminders = database.get_reminders(str(now))
        self.remind_list += reminders
    
    # Pings people when a reminder is due
    @tasks.loop(seconds=10.0)
    async def remind_people(self):
        while self.remind_list:
            uid = self.remind_list[-1]
            self.remind_list.pop(-1)
            if uid == -1:
                continue
            reminder = database.get_reminder(uid)
            if reminder and not reminder['done']:
                # send message to the server
                channel = self.bot.get_channel(reminder["channel"])
                reminder_embed = discord.Embed(
                    tite=f'Reminder!', 
                    description=f'{reminder["author"]} wanted to remind you of your agenda "{reminder["label"]}"'
                )
                await channel.send(f'{reminder["user_id"]}', embed=reminder_embed)
                database.finished_reminder(uid)

    @commands.command(aliases = ['r'])
    async def remind(self, ctx):
        """Creates a reminder event"""

        # Try to obtain who to remind
        try:
            msg = ctx.message.content.split(maxsplit=2)
            user = await self.bot.fetch_user(int(msg[2][3:-1]))
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
        
        @formats.is_proper_date_time
        def proper_reply2(reply):
            "Ensures that the reply came from the original sender"
            return reply.author == ctx.message.author and reply.content.isprintable()

        # Prompt the user regarding when the reminder must come
        await ctx.channel.send(f'When is this due?')
        try:
            print('I\'m now awaiting the response')
            reply = await self.bot.wait_for('message', check = proper_reply2, timeout = 30.0)
            remind_date_time = formats.get_date_time_format(reply.content)
        except asyncio.TimeoutError:
            print(f'But he was taking too long though, so I had to ignore him.')
            return await ctx.channel.send(config.MSG_TIMEOUT_ERROR)
        else:
            print(f'It was due on {remind_date_time}')

        # Make sure that the date is in the future
        now = datetime.datetime.now(tz=tz.tzlocal())
        if remind_date_time < now:
            print(f'But it was in the past!')
            return await ctx.channel.send(config.MSG_INVALID_REMINDER_DATE)

        await ctx.channel.send(f'Okay! Will do.')
        
        remind_date_time = remind_date_time.replace(second=0, microsecond=0)
        print(f'I got that he/she wanted to be reminded on {remind_date_time}')

        await ctx.channel.send(f'Will remind {user.name} {reply.content}')

        # TO-DO: Store in database
        uid = database.insert_unique({
            'label' : label,
            'author' : f'{ctx.message.author.name}',
            'user_id' : f'<@!{user.id}>',
            'done' : False,
            'guild' : ctx.message.guild.id,
            'channel' : ctx.message.channel.id,
        })
        database.insert_reminder(str(remind_date_time), uid)
        print(f'Uploaded reminder uid {uid} successfully!')

        # TO-DO: Fix the reminding system. So far, looks good tho
    

def setup(bot):
    bot.add_cog(Reminding(bot))
