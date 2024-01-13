from bot import bot, discord, time, pymongo
from constants import GUILD_ID, LINK, FORCED_MUTE_ROLE
from roles import has_role, get_role, is_helper, is_moderator, is_server_booster, is_bot_developer, is_chat_moderator


@bot.slash_command(name="gostudy", description="disables the access to the offtopics for 1 hour.")
async def gostudy(interaction: discord.Interaction,
                  user: discord.User = discord.SlashOption(name="name", description="who do you want to use this command on? (for mods)", required=False)):
        
      forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
      if user == None:
            user_id = interaction.user.id
            user = bot.get_guild(GUILD_ID).get_member(user_id)        
            view = discord.ui.View(timeout=None)
            proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
            cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            async def proceedCallBack(interaction):
                 unmute_tim = int(((time.time()) + 1) + 3600)
                 await message.delete()
                 dm = await user.create_dm()
                 embed = discord.Embed(description = f"Study time! You've been given a temporary break from the off-topic channels for the next hour, thanks to <@{interaction.user.id}>. Use this time to focus on your studies and make the most of it!\n\nThe role will be removed at <t:{unmute_tim}:f>, which is <t:{unmute_tim}:R>", color=0xAFE1AF)
                 await dm.send(embed=embed)
                 await user.add_roles(forced_mute_role)
                 timern = int(time.time()) + 1
                 unmute_time = int(((time.time()) + 1) + 3600)
                 client = pymongo.MongoClient(LINK)
                 db = client.IGCSEBot
                 mute = db["mute"]
                 mute.insert_one({"_id": str(timern), "user_id": str(user_id),
                                  "unmute_time": str(unmute_time), "muted": True})
            proceedBTN.callback = proceedCallBack
            async def cancelCallBack(interaction):
                 await message.delete()
            cancelBTN.callback = cancelCallBack
            view.add_item(proceedBTN)
            view.add_item(cancelBTN)
            message = await interaction.send("Are we ready to move forward?", view=view, ephemeral=True)
      else:
            unmute_tim = int(((time.time()) + 1) + 3600)
            if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
            user_id = user.id
            user = bot.get_guild(GUILD_ID).get_member(user_id)
            view = discord.ui.View(timeout=None)
            proceedBTN = discord.ui.Button(label="Proceed", style=discord.ButtonStyle.blurple)
            cancelBTN = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
            async def proceedCallBack(interaction):
                 await message.delete()
                 dm = await user.create_dm()
                 embed = discord.Embed(description = f"Study time! You've been given a temporary break from the off-topic channels for the next hour, thanks to <@{interaction.user.id}>. Use this time to focus on your studies and make the most of it!\n\nThe role will be removed at <t:{unmute_tim}:f>, which is <t:{unmute_tim}:R>", color=0xAFE1AF)
                 await dm.send(embed=embed)
                 await user.add_roles(forced_mute_role)
                 await interaction.send(f"{user.name} has been put on forced mute until <t:{unmute_tim}:f>, which is <t:{unmute_tim}:R>.")
                 timern = int(time.time()) + 1
                 unmute_time = int(((time.time()) + 1) + 3600)
                 client = pymongo.MongoClient(LINK)
                 db = client.IGCSEBot
                 mute = db["mute"]
                 mute.insert_one({"_id": str(timern), "user_id": str(user_id),
                                  "unmute_time": str(unmute_time), "muted": True})
            proceedBTN.callback = proceedCallBack
            async def cancelCallBack(interaction):
               await message.delete()
               cancelBTN.callback = cancelCallBack
            view.add_item(proceedBTN)
            view.add_item(cancelBTN)
            message = await interaction.send("Are you sure?", view=view, ephemeral=True)

@bot.slash_command(name="remove_gostudy", description="remove the Forced Mute role. (for mods)")
async def remove_gostudy(interaction: discord.Interaction,

                  user: discord.User = discord.SlashOption(name="name", description="who do you want to use this command on?", required=False)):
        await interaction.response.defer(ephemeral = True)
        if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
        
        forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
        if user == None:
            user_id = interaction.user.id
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
            await member.remove_roles(forced_mute_role)
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            mute = db["mute"]
            mute.delete_one({"user_id": str(user_id)})
            await interaction.send(f"the Forced mute role has been removed from <@{user_id}>.", ephemeral=True)

        else:
            user_id = user.id
            user = bot.get_guild(GUILD_ID).get_member(user_id)
            guild = bot.get_guild(GUILD_ID)
            member = guild.get_member(user_id)
            forced_mute_role = bot.get_guild(GUILD_ID).get_role(FORCED_MUTE_ROLE)
            await member.remove_roles(forced_mute_role)
            client = pymongo.MongoClient(LINK)
            db = client.IGCSEBot
            mute = db["mute"]
            mute.delete_one({"user_id": str(user_id)})
            await interaction.send(f"the Forced mute role has been removed from <@{user_id}>.", ephemeral=True)