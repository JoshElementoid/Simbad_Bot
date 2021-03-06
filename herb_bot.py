# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 00:32:58 2021

@author: Josh
"""

import discord, nest_asyncio, requests, os

from helper_functions import helper, shop_helper

from discord.ext import commands
from discord.utils import get

# There's probably a better way to import everything...
from config.messages import *
from config.paths import *
from config.ids import *
from config.role_perms import *
from static.gifs import *
from static.public_roles import*

nest_asyncio.apply()    # Unnecessary for production

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)  # Bot commands start with "$"


# I should've used pathlib
key_path = "C:\\Users\\Josh\\Desktop\\Misc\\secret_key\\secret.txt"

with open(key_path, "r") as f:
    secret_key = f.readline()   # Oh so secret
    f.close()

market = shop_helper.shop(shop_money_path, shop_item_path)

bot.voice_bot_ids = []  # "Global" var to keep track of all the bot-created channel ids

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
                
        if after_id == click_to_create_id:
            # Create the voice channel:
            created_channel = await guild.create_voice_channel("new_channel", 
                                                               category=category) 
            # Adds the channel ID to "global" var
            bot.voice_bot_ids += [created_channel.id]
            
            # Move them to the channel
            await member.move_to(created_channel)
         
                    
@bot.command()
@commands.has_any_role(*command_role_perms["welcome"])
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
@commands.has_any_role(*command_role_perms["gif"])
async def gif (ctx, meme=None):
    if meme:
        link = gif_dict[str(meme).lower()]
        await ctx.send(link)
        
    else:
        info = helper.dict_list(gif_dict)
        await ctx.send("Available gifs: `{}`".format(info))
        
    
@bot.command()
@commands.has_any_role(*command_role_perms["voice"])
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


@bot.command()
@commands.has_any_role(*command_role_perms["roles"])
async def roles (ctx, *args):   
    
    guild = ctx.guild
    # If no args, sends a message of all the publicly available roles
    if not any(args):
        info = ", ".join(available_roles)   
        await ctx.send(info)
        
    # If the first arg is "toggle":
    elif args[0].lower() == "toggle":
        num_args = len(args)

        # If there is a mention (aka used on another person):
        if "@" in args[1]:  
            # Get the top role of the mentioned user:
            mentioned_id = helper.parse_into_id(args[1])
            mentioned_member = guild.get_member(int(mentioned_id))
            mentioned_top_role = mentioned_member.top_role
            
            # Get the top role of the message author:
            author = ctx.message.author
            author_top_role = author.top_role
            
            # If the message author has a higher role than the mentioned:
            if author_top_role > mentioned_top_role:
                # Parse into a list of wanted roles:
                wanted_roles = " ".join(args[2:]).split(",")
                # Check if the wanted roles are valid, publicly available roles
                check = set(wanted_roles).issubset(set(available_roles))
                
                if check:
                    req_roles = [get(guild.roles,name=x)   # Requested roles
                                 for x in wanted_roles]   
                    cur_roles = mentioned_member.roles     # Current roles
                    
                    to_add = [x for x in req_roles         # Roles to add 
                              if x not in cur_roles]
                    to_remove = [x for x in req_roles      # Roles to remove
                                 if x in cur_roles]
                    
                    # Messages to send
                    to_add_str = ", ".join([x.name for x in to_add])
                    to_remove_str = ", ".join([x.name for x in to_remove])

                    # Toggle the roles
                    await mentioned_member.add_roles(*to_add)
                    await mentioned_member.remove_roles(*to_remove)
                    
                    # Sends message in channel
                    if to_add:
                        await ctx.send("Roles added: `{}`".format(to_add_str))
                    if to_remove:
                        await ctx.send("Roles removed: `{}`".format(to_remove_str))
                     
                else:
                    await ctx.send("At least 1 specified role is invalid")
            
            else:
                await ctx.send("You do not have permission to modify that person's roles")
                
                
        else:   # If there is no mention, do the same things for the message's author
            author = ctx.message.author
            wanted_roles = " ".join(args[1:]).split(",")
            # Check if the wanted roles are valid, publicly available roles
            check = set(wanted_roles).issubset(set(available_roles))
            if check:
                req_roles = [get(guild.roles,name=x)   # Requested roles
                             for x in wanted_roles]   
                cur_roles = author.roles     # Current roles
                
                to_add = [x for x in req_roles         # Roles to add 
                          if x not in cur_roles]
                to_remove = [x for x in req_roles      # Roles to remove
                             if x in cur_roles]
                
                # Messages to send
                to_add_str = ", ".join([x.name for x in to_add])
                to_remove_str = ", ".join([x.name for x in to_remove])
                
                await author.add_roles(*to_add)
                await author.remove_roles(*to_remove)             
        
                # Sends message in channel
                if to_add:
                    await ctx.send("Roles added: `{}`".format(to_add_str))
                if to_remove:
                    await ctx.send("Roles removed: `{}`".format(to_remove_str))
                    
            else:
                await ctx.send("At least 1 specified role is invalid")
                
    else:
        print("Else")
        print(args)


@bot.command()
async def shop(ctx, *args):
    
    member = ctx.message.author
    member_id = member.id
    command_message = ctx.message.content
    
    shop_manager_role = get(member.guild.roles, name="Moderator")
    
    #### Initialization stuff ####
    arg_len = len(args)     # Profound statement
    

    if arg_len == 0:
        command = "help"
    else:
        command = args[0]
        
    # Check for mentions    
    if arg_len > 1:
        if "@" in args[1]:
            member_id = int(helper.parse_into_id(args[1]))        
        
    exist = any(market.bal_df["member_id"] == member_id)
        
    
    if not exist:
        market.member_init(member_id)   # Initializes member in the df
    
    #### Shop commands ####
    
    # show
    if command.lower() == "show":
        msg = market.shop_show()
        await ctx.send("```python\n{}```".format(msg))
    
    # inventory
    elif command.lower() == "inventory":
        """
        Shows your inventory. If there is a mention in the 1st index of the arg, 
        it will show the mentioned member's inventory instead.
        
        """
        msg = market.show_inv(member_id)
        
        await ctx.send("```python\n{}```".format(msg))
    
    
    elif command.lower() == "balance":
        bal = market.member_balance(member_id)
        msg = "```python\nYour account balance: {}```".format(float(bal))
        
        await ctx.send(msg)
        
    elif command.lower() == "award":
        """
        Increase someone's balance by amount. Only Moderator or higher can
        use this. This does not decrease your own balance
        
        """
    
        if member.top_role >= shop_manager_role:
            market.change_balance(member_id, args[-1])
            
            await ctx.send("Done.")
            
        else:
            await ctx.send("You don't have permission")
            
       
    elif command.lower() == "donate":
        """
        Gives some of your money to someone else
        
        """
        amount = args[-1]
        author_id = ctx.message.author.id
        
        msg = market.donate(author_id, member_id, float(amount))
        
        await ctx.send(msg)
        
        
    elif command.lower() == "buy":
        author_id = ctx.message.author.id
        
        if int(author_id) != int(member_id):
            await ctx.send("You can't buy for someone else, dummy")   
            
            return
        
        # Finds the item and quantity the member wants to buy:
        item = args[1]
        quantity = 1
        
        if len(args) > 2:
            quantity = args[2]
        
        # Call the buy method:
        msg = market.buy(author_id, item, quantity=int(quantity))   
        
        await ctx.send(msg)
    
    
    elif command.lower() == "remove":
        mod_role = get(member.guild.roles, name="Moderator")
        # Finds the item and quantity of the item to be removed:
        quantity = 1
        item = args[2]
        
        if len(args) > 3:
            quantity = int(args[3])
            
            if quantity <= 0:
                await ctx.send("What the fuck?")
                return
        
        if member.top_role >= mod_role:
            msg = market.remove_item(member_id, item, quantity)
            await ctx.send(msg)
            
            return   
        
        await ctx.send("You don't have permission :(") 
        
        
    elif command.lower() == "reload":
        """
        Reinitializes the market object. Reserved for Elementoid, Moderator, 
        and Admins
        
        """
        author = ctx.message.author
        is_elementoid = int(author.id) == 117431457202438148
        mod_role = get(member.guild.roles, name="Moderator")
        
        if is_elementoid or member.top_role >= mod_role:
            market.reload()
            
            await ctx.send("Market reinitialized!")
            return
        
        await ctx.send("Nah")
                
    
#%% Running the bot
bot.run(secret_key)


















