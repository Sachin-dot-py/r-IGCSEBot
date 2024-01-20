from bot import bot, discord, time, pymongo
from constants import GUILD_ID, LINK, FORCED_MUTE_ROLE, MODLOG_CHANNEL_ID
from roles import has_role, get_role, is_helper, is_moderator, is_server_booster, is_bot_developer, is_chat_moderator
from pytimeparse import parse
from typing import Optional


@bot.slash_command(name="gostudy", description="disables the access to the offtopics for 1 hour.")
async def gostudy(interaction: discord.Interaction,
                  mute_time: Optional[str] = discord.SlashOption(name="time", description="how long should the mute last for? (default: 1 hour)", required=False),
                  user: Optional[discord.User] = discord.SlashOption(name="name", description="who do you want to use this command on? (for mods)", required=False)):
      
      client = pymongo.MongoClient(LINK)
      db = client.IGCSEBot
      mute = db["mute"]
      timern = int(time.time()) + 1
      channel = interaction.channel
      Logging = bot.get_channel(MODLOG_CHANNEL_ID)
      forced_mute_role = interaction.guild.get_role(FORCED_MUTE_ROLE)
      time_to_mute = 3600
      if mute_time:
            time_to_mute = parse(mute_time) or 3600
            if time_to_mute < 600:
                  await interaction.send("The minimum time for gostudy is 10 minutes!", ephemeral=True)
                  return
      if user == None:
            user_id = interaction.user.id
            user = interaction.guild.get_member(user_id)
            dm = await user.create_dm()    
            view = discord.ui.View(timeout=None)
            proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
            cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            async def proceedCallBack(interaction):
                  unmute_time = ((int(time.time()) + 1) + time_to_mute)
                  await message.delete()
                  await user.add_roles(forced_mute_role)
                  embed = discord.Embed(description="Go Study Mode Activated", colour=discord.Colour.red())
                  embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                  embed.add_field(name="User", value=f"{user.mention}", inline=False)
                  embed.add_field(name="Duration", value= f"<t:{unmute_time}:R>", inline=False)
                  embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
                  embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nRole = {FORCED_MUTE_ROLE}```", inline=False)
                  embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
                  await Logging.send(embed=embed)                  
                  await channel.send(f"{user.name} has been put on forced mute until <t:{unmute_time}:f>, which is <t:{unmute_time}:R>.")
                  embed = discord.Embed(description = f"Study time! You've been given a temporary break from the off-topic channels for the next hour, thanks to <@{interaction.user.id}>. Use this time to focus on your studies and make the most of it!\n\nThe role will be removed at <t:{unmute_time}:f>, which is <t:{unmute_time}:R>", color=0xAFE1AF)
                  await dm.send(embed=embed)                  
                  mute.insert_one({"_id": timern, "user_id": str(user_id), "unmute_time": str(unmute_time), "muted": True})
            proceedBTN.callback = proceedCallBack
            
            async def cancelCallBack(interaction):
                  await message.delete()
            cancelBTN.callback = cancelCallBack
            view.add_item(proceedBTN)
            view.add_item(cancelBTN)
            message = await interaction.send("Are we ready to move forward?", view=view, ephemeral=True)
      else:
            if not await is_moderator(interaction.user) and not await is_bot_developer(interaction.user) and not await is_chat_moderator(interaction.user):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
            user_id = user.id
            user = interaction.guild.get_member(user_id)
            dm = await user.create_dm()
            view = discord.ui.View(timeout=None)
            proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
            cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            async def proceedCallBack(interaction):
                  unmute_time = int(((time.time()) + 1) + time_to_mute)
                  mute.insert_one({"_id": timern, "user_id": str(user_id), "unmute_time": str(unmute_time), "muted": True})                  
                  await message.delete()
                  await user.add_roles(forced_mute_role)
                  embed = discord.Embed(description="Go Study Mode Activated", colour=discord.Colour.red())
                  embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
                  embed.add_field(name="User", value=f"{user.mention}", inline=False)
                  embed.add_field(name="Duration", value= f"<t:{unmute_time}:R>", inline=False)
                  embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
                  embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nRole = {FORCED_MUTE_ROLE}```", inline=False)
                  embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
                  await Logging.send(embed=embed)                   
                  embed = discord.Embed(description = f"Study time! You've been given a temporary break from the off-topic channels for the next hour, thanks to <@{interaction.user.id}>. Use this time to focus on your studies and make the most of it!\n\nThe role will be removed at <t:{unmute_time}:f>, which is <t:{unmute_time}:R>", color=0xAFE1AF)
                  await dm.send(embed=embed)                  
                  await channel.send(f"{user.name} has been put on forced mute until <t:{unmute_time}:f>, which is <t:{unmute_time}:R>.")
            proceedBTN.callback = proceedCallBack
            
            async def cancelCallBack(interaction):
                  await message.delete()
            cancelBTN.callback = cancelCallBack
            view.add_item(proceedBTN)
            view.add_item(cancelBTN)
            message = await interaction.send("Are you sure?", view=view, ephemeral=True)

@bot.slash_command(name="remove_gostudy", description="remove the Forced Mute role. (for mods)")
async def remove_gostudy(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="name", description="who do you want to use this command on?", required=False)):
        await interaction.response.defer(ephemeral = True)

        if not await is_moderator(interaction.user) and not await is_bot_developer(interaction.user) and not await is_chat_moderator(interaction.user):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
        
        client = pymongo.MongoClient(LINK)
        db = client.IGCSEBot
        mute = db["mute"] 
        timern = int(time.time()) + 1
        forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
        Logging = bot.get_channel(MODLOG_CHANNEL_ID)          
        if user == None:
            user_id = interaction.user.id
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
            await member.remove_roles(forced_mute_role)
            mute.delete_one({"user_id": str(user_id)})
            embed = discord.Embed(description="Go Study Mode Deactivated", colour=discord.Colour.green())
            embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
            embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
            embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nRole = {FORCED_MUTE_ROLE}```", inline=False)
            embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
            await Logging.send(embed=embed)                  
            await interaction.send(f"the Forced mute role has been removed from <@{user_id}>.", ephemeral=True)

        else:
            user_id = user.id
            user = bot.get_guild(GUILD_ID).get_member(user_id)
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
            await member.remove_roles(forced_mute_role)
            mute.delete_one({"user_id": str(user_id)})
            embed = discord.Embed(description="Go Study Mode Deactivated", colour=discord.Colour.green())
            embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
            embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
            embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nRole = {FORCED_MUTE_ROLE}```", inline=False)
            embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
            await Logging.send(embed=embed)              
            await interaction.send(f"the Forced mute role has been removed from <@{user_id}>.", ephemeral=True)
