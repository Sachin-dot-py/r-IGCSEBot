from bot import bot
from db import gpdb

@bot.event
async def on_guild_join(guild):
    gpdb.set_pref('rep_enabled', True, guild.id)
    await guild.create_role(name="Reputed", color=0x3498db)  # Create Reputed Role
    await guild.create_role(name="100+ Rep Club", color=0xf1c40f)  # Create 100+ Rep Club Role
    await guild.create_role(name="500+ Rep Club", color=0x2ecc71)  # Create 500+ Rep Club Role
    await guild.system_channel.send("Hi! Please set all the server preferences using the slash command /set_preferences for this bot to function properly.")