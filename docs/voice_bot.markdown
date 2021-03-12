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

To create a voice channel, simply join the channel called "click_to_create"
<img src=C:/Users/Josh/Desktop/Misc/Simbad/static/site_images/click_to_create.PNG>