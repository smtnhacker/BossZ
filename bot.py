"""
Copyright © Something Hacker

Description:
BossZ - Class Management Bot

Version 0.1
"""
import os, sys, asyncio, platform
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord.ext.commands import Bot

try:
    import config
except Exception as e:
    print(f'An exception of type {type(e).__name__} has occured: {e}')

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(command_prefix = config.BOT_PREFIX)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print(f'----------------------------------------')
    bot.loop.create_task(status_task())

# Manages the status of the bot
async def status_task():
    while True:
        await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f'{config.BOT_PREFIX}help'))
        await asyncio.sleep(120)
        await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f'cries for help'))
        await asyncio.sleep(60)
        await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"students' tears"))
        await asyncio.sleep(60)
        await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"LOA filing"))
        await asyncio.sleep(60)

@bot.event
async def on_message(msg):
    # if self or bot message, ignore
    if msg.author == bot.user or msg.author.bot:
        return
    
    await bot.process_commands(msg)

@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(' ')
    executedCommand = str(split[0])
    print(f'Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
                title = 'Error!',
                description = 'This command is on a %.2fs cool down. Retry later',
                color = config.COLOR_ERROR
        )
        await ctx.send(embed = embed)

if __name__ == '__main__':
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            extension = file[:-3]
            try:
                bot.load_extension(f'cogs.{extension}')
                print(config.MSG_COG_LOAD_SUCCESS.format(extension))
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(config.MSG_COG_LOAD_ERROR.format(extension, exception))

bot.run(TOKEN)