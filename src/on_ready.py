from bot import bot, discord
from constants import GUILD_ID, BOTLOG_CHANNEL_ID, BOTBETA, BOTMAIN, BETA, CHAT_MODERATOR_ROLES, IGCSE_HELPER_ROLE, AL_HELPER_ROLE, BOT_DEVELOPER_ROLES, TEMP_MOD_ROLE, STAFF_MODERATOR_ROLE
from monitor_tasks import checklock, checkmute

@bot.event
async def on_ready():
    print(f"Logged in as {str(bot.user)}.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="r/IGCSE"))
    checklock.start()
    checkmute.start()
    igcse = bot.get_guild(GUILD_ID)
    botlogs = await igcse.fetch_channel(BOTLOG_CHANNEL_ID)
    user = bot.user 
    format = "%d-%m-%Y"           
    embed = discord.Embed(title=f"r/IGCSE bot restarted successfully!", colour=0x51BB56)
    embed.add_field(name="Bot Information", value=f"```Name: {bot.user}\nCreated on: {'28-02-2022' if BETA else '05-07-2021'}\nJoined on: {'30-09-2022' if BETA else '08-06-2022'}\nBeta: {BETA}\nVerified: {user.verified}\nID: {user.id}```", inline=False)
    embed.add_field(name="Guild Information", value=f"```Name: {igcse.name}\nOwner: {igcse.owner}\nCreated on: {igcse.created_at.strftime(format)}\nMembers: {igcse.member_count}\nBoosts: {igcse.premium_subscription_count}\nID: {igcse.id}```", inline=False)
    embed.add_field(name="Role Statistics", value=f"```IGCSE Helpers: {len(igcse.get_role(IGCSE_HELPER_ROLE).members)}\nAS/AL Helpers: {len(igcse.get_role(AL_HELPER_ROLE).members)}\nBot Developers: {len(igcse.get_role(BOT_DEVELOPER_ROLES).members)}\nStaff Moderators: {len(igcse.get_role(STAFF_MODERATOR_ROLE).members)}\nTemp Moderators: {len(igcse.get_role(TEMP_MOD_ROLE).members)}\nChat Moderators: {len(igcse.get_role(CHAT_MODERATOR_ROLES).members)}```", inline=False)
    embed.set_footer(text=f"{bot.user}", icon_url=bot.user.display_avatar.url)
    await botlogs.send(embed=embed)
