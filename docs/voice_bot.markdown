---
layout: default
title: Voice Bot
nav_order: 2
permalink: /voice_bot
---
# Voice Bot
{: .fs-9 }

Commands for creating and modifying voice channels
{: .fs-6 .fw-300 }


## Creating a Voice Channel

<details>
<summary>Potato Code</summary>
<div class="code-example" markdown="1">
```python
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
            created_channel = await guild.create_voice_channel("new_channel", category=category) 
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
            created_channel = await guild.create_voice_channel("new_channel", category=category) 
            # Adds the channel ID to "global" var
            bot.voice_bot_ids += [created_channel.id]
            # Move them to the channel
            await member.move_to(created_channel)
```
</div>
</details>

To create a voice channel, simply join the channel called "click_to_create". A new channel will be created for you, and you will be moved to the new channel. <br>
<br>
<img src="https://cdn.discordapp.com/attachments/820010605628096522/820017949389619240/unknown.png" width="241" height="100"/>

--- 

## Voice Channel Commands

<details>
<summary>Potato Code</summary>
<div class="code-example" markdown="1">
```python
@bot.command()
async def voice (ctx, command, arg):
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
```
</div>
</details>

Changes the property of the voice channel you are currently in. Will only work for bot-created channels.

### Usage:

{% highlight markdown %}
$voice <attribute> <new> 
{% endhighlight %}

<br>

`attribute` - What you want to change about the channel. Currently supports:
- `name` - the name of the channel
- `limit` - the maximum number of members in the channel

<br>

`new` - The new value of the selected `attribute`.
 - If `limit` was passed, `new` must be a number between 1 and 99
 
 <br>
 
### Example Commands:
Changing voice channel name
{% highlight markdown %}
$voice name Braben_Tunnel
{% endhighlight %}

Limiting maximum number of users in voice channel to 3:
{% highlight markdown %}
$voice limit 3
{% endhighlight %}

<br>

<img src="https://cdn.discordapp.com/attachments/820010605628096522/820017850134691863/unknown.png" width="241" height="100"/>
















