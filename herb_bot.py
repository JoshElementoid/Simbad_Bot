# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 00:32:58 2021

@author: Josh
"""

import discord, nest_asyncio, requests

from discord.ext import commands
from discord.utils import get

# There's probably a better way to import everything...
from config.messages import *
from config.secret import *
from config.paths import *
from config.ids import *
from static.gifs import *


nest_asyncio.apply()    # Unnecessary for production
bot = commands.Bot(command_prefix='$')  # Bot commands start with "$"

bot.voice_bot_ids = []  # "Global" var to keep track of all the created channel ids

@bot.event
async def on_ready ():
    print("Ready to gank!")


@bot.event
async def on_voice_state_update (member, before, after):    
    
    guild = member.guild
    category = get(guild.categories, name="voice_bot")    
    
    from_channel = before.channel
    after_channel = after.channel
    
    # Gets the ID of the channels the user came from and the channels
    # they went to. The ID is "none" if they connected for the first time or
    # disconnected from voice.
    
    if not from_channel:
        from_id = "none"
    else:
        from_id = from_channel.id
        
    if not after_channel:
        after_id = "none"
    else:
        after_id = after_channel.id
        

    # If they came from a non bot-created voice channel
    if from_id not in bot.voice_bot_ids:
        
        # If they went into the "click_to_create" channel OR disconnected:
        if after_id == click_to_create_id:
            # Create the voice channel:
            created_channel = await guild.create_voice_channel("new_channel", 
                                                               category=category) 
            # Adds the channel ID to "global" var
            bot.voice_bot_ids += [created_channel.id]
            
            # Move them to the channel
            await member.move_to(created_channel)
    
        # If they went into another channel OR disconnected:
        else:   
            # If the channel is bot-created:
            if from_id in bot.voice_bot_ids:
                # Check if empty:
                if not any(before.channel.members):
                    # Delete if empty:
                    bot.voice_bot_ids.remove(before.channel.id)
                    await before.channel.delete()                         

    # If they came from a bot-created channel:
    else:   
        # Same process as before. The else is probably not necessary actually
        if from_id in bot.voice_bot_ids:
            if not any(before.channel.members):
                bot.voice_bot_ids.remove(before.channel.id)
                
                await before.channel.delete()
         
                    
@bot.command()
async def welcome (ctx, user: discord.User):
    """
    Syntax: $welcome @User
    
    Gives User the roles "Simbian" and "Elite", pings them, and sends a 
    welcome message in #general.
    
    """
    
    # Get role:
    member = ctx.message.author
    role = get(member.guild.roles, name="Elite")
    role_2 = get(member.guild.roles, name="Simbian")

    # General chat:
    channel = discord.utils.get(member.guild.text_channels, 
                                name="general")
        
    # Give mentioned user the roles:
    await user.add_roles(role)
    await user.add_roles(role_2)
    
    # Send welcoming messages:
    await channel.send(welcome_message.format(user.mention, 
                                              general_id))
    

@bot.command()
async def free_money (ctx):
    """
    Never gonna give free money up
    """
    await ctx.send("https://giphy.com/gifs/rick-roll-lgcUUCXgC8mEo")
    
    
@bot.command()
async def gif (ctx, meme):
    link = gif_dict[str(meme).lower()]
    await ctx.send(link)
    
    
@bot.command()
async def voice (ctx, command, arg):
    """ 
    Modifies the user's current voice channel
    
    Syntax:
    $voice <command> <arg>
    
    commands:
        name: changes the voice channel name to arg
        limit: limits the voice channel's max number of people to arg
    
    
    """ 
    guild = ctx.guild
    member = ctx.message.author
    channel = member.voice.channel 
    
    
    if channel.id in bot.voice_bot_ids:
        if command.lower() == "name":
            new_name = str(arg)[:20]
            await channel.edit(name=new_name)
            await ctx.send("Voice channel renamed to {}".format(new_name))
    
        if command.lower() == "limit":
            await channel.edit(user_limit=int(arg[0]))
            await ctx.send("Limited to max {} people".format(int(arg[0])))
    
    else:
        await ctx.send("My creator does not allow me to rename human-made channels :(")







#%%
bot.run(secret_key)


















