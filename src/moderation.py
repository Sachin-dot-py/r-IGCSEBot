from bot import bot, discord, pymongo, datetime, time
from bans import is_banned
from roles import is_chat_moderator, is_moderator
from mongodb import gpdb
from constants import GUILD_ID
import re

def convert_time(time: tuple[str, str, str, str]) -> str:
    time_str = ""
    if time[0] != "0":
        time_str += f"{time[0]} day{'s' if int(time[0]) > 1 else ''} "
    if time[1] != "0":
        time_str += f"{time[1]} hour{'s' if int(time[1]) > 1 else ''} "
    if time[2] != "0":
        time_str += f"{time[2]} min{'s' if int(time[2]) > 1 else ''} "
    return time_str.strip()


async def match_message(message: str) -> dict[str, str]:
    lines = message.split("\n")
    lines.pop(1)

    action = ""
    action_by = ""
    reason_for_action = ""
    timeout_duration = ""
    
    for line in lines:
        match_first_line = re.findall(r"Case #\d{4} \| \[(.*)\]", line)
        if match_first_line:
            action = match_first_line[0]
            continue
        match_third_line = re.findall(r"Moderator: (.*)", line)
        if match_third_line:
            action_by = match_third_line[0]
            continue
        match_fourth_line = re.findall(r"Reason: (.*)", line)
        if match_fourth_line:
            reason_for_action = match_fourth_line[0]
            continue
        if action == "Timeout":
            match_fifth_line = re.findall(r"Duration: (\d+)d (\d+)h (\d+)m (\d+)s", line)
            if match_fifth_line:
                timeout_duration = match_fifth_line
                continue
    
    return {
        "action": action,
        "action_by": action_by,
        "reason_for_action": reason_for_action,
        "timeout_duration": timeout_duration
    }

@bot.slash_command(description="Check a user's previous offenses (warns/timeouts/bans)")
async def history(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="user", description="User to view history of", required=True)):
    if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
        await interaction.send("You are not permitted to use this command.", ephemeral=True)
    await interaction.response.defer()
    modlog = gpdb.get_pref("modlog_channel", interaction.guild.id)
    warnlog = gpdb.get_pref("warnlog_channel", interaction.guild.id)
    if modlog and warnlog:
        history = []
        actions = {}
        modlog = bot.get_channel(modlog)
        warnlog = bot.get_channel(warnlog)
        warn_history = await warnlog.history(limit=750).flatten()
        modlog_history = await modlog.history(limit=500).flatten()
        messages = warn_history + modlog_history
        for message in messages:
            if str(user.id) not in message.clean_content:
                continue
            parsed_message = await match_message(message.clean_content)
            if parsed_message['action'] not in actions:
                actions[parsed_message['action']] = 1
            else:
                actions[parsed_message['action']] += 1
            date_of_event = message.created_at.strftime("%d %b, %Y at %H:%M")
            duration = parsed_message['timeout_duration'][0] if parsed_message['action'] == 'Timeout' else ""
            duration_as_text = f" ({convert_time(duration)})" if parsed_message['action'] == 'Timeout' else ""
        
            reason = f" for {parsed_message['reason_for_action']}" if parsed_message['reason_for_action'] else ""

            final_string = f"[{date_of_event}] {parsed_message['action']}{duration_as_text}{reason} by {parsed_message['action_by'].strip()}"
            history.append(final_string)

        if len(history) == 0:
            await interaction.send(f"{user} does not have any previous offenses.", ephemeral=False)
        else:
            text = f"Moderation History for {user}:\n\n"
            text += "\n".join(list(map(lambda x:f"{x[0]}: {x[1]}", list(actions.items()))))
            text += '\n\n'
            text += ('\n'.join(history))[:1900]
            await interaction.send(f"```accesslog\n{text}```", ephemeral=False)
    else:
        await interaction.send("Please set up your moglog and warnlog through `/set_preferences` first!")

@bot.slash_command(description="Warn a user (for mods)")
async def warn(interaction: discord.Interaction, 
               user: discord.Member = discord.SlashOption(name="user", description="User to warn", required=True), 
               reason: str = discord.SlashOption(name="reason", description="Reason for warn", required=True)):
    
    action_type = "Warn"
    mod = interaction.user
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    warnlog_channel = gpdb.get_pref("warnlog_channel", interaction.guild.id)
    if warnlog_channel:
        ban_msg_channel = bot.get_channel(warnlog_channel)
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await interaction.send(f"{str(user)} has been warned.")
        await ban_msg_channel.send(ban_msg)
    channel = await user.create_dm()
    await channel.send(
        f"You have been warned in r/IGCSE by moderator {mod} for \"{reason}\".\n\nPlease be mindful in your further interaction in the server to avoid further action being taken against you, such as a timeout or a ban.")

@bot.slash_command(description="Timeout a user (for mods)")
async def timeout(interaction: discord.Interaction,
                  user: discord.Member = discord.SlashOption(name="user", description="User to timeout",
                                                             required=True),
                  time_: str = discord.SlashOption(name="duration",
                                                   description="Duration of timeout (e.g. 1d5h) up to 28 days (use 'permanent')",
                                                   required=True),
                  reason: str = discord.SlashOption(name="reason", description="Reason for timeout", required=True)):
    action_type = "Timeout"
    mod = interaction.user.mention
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    if time_.lower() == "unspecified" or time_.lower() == "permanent" or time_.lower() == "undecided":
        seconds = 86400 * 28
    else:
        seconds = 0
        if "d" in time_:
            seconds += int(time_.split("d")[0]) * 86400
            time_ = time_.split("d")[1]
        if "h" in time_:
            seconds += int(time_.split("h")[0]) * 3600
            time_ = time_.split("h")[1]
        if "m" in time_:
            seconds += int(time_.split("m")[0]) * 60
            time_ = time_.split("m")[1]
        if "s" in time_:
            seconds += int(time_.split("s")[0])
    if seconds == 0:
        await interaction.send("You can't timeout for zero seconds!", ephemeral=True)
        return
    await user.edit(timeout=discord.utils.utcnow() + datetime.timedelta(seconds=seconds))
    human_readable_time = f"{seconds // 86400}d {(seconds % 86400) // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s"
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)"""
        await ban_msg_channel.send(ban_msg)
    await user.send(f'''You have been given a timeout on the r/IGCSE server 
Reason: {reason}
Duration: {human_readable_time}
Until: <t:{int(time.time()) + seconds}> (<t:{int(time.time()) + seconds}:R>)''')
    await interaction.send(
        f"{str(user)} has been put on time out until <t:{int(time.time()) + seconds}>, which is <t:{int(time.time()) + seconds}:R>.")
    
@bot.slash_command(description="Untimeout a user (for mods)")
async def untimeout(interaction: discord.Interaction,
                    user: discord.Member = discord.SlashOption(name="user", description="User to untimeout",
                                                               required=True)):
    action_type = "Remove Timeout"
    mod = interaction.user.mention
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    if not await is_moderator(interaction.user) and not await is_chat_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    await user.edit(timeout=None)
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.send(f"Timeout has been removed from {str(user)}.")

@bot.slash_command(description="Kick a user from the server (for mods)")
async def kick(interaction: discord.Interaction,
               user: discord.Member = discord.SlashOption(name="user", description="User to kick", required=True),
               reason: str = discord.SlashOption(name="reason", description="Reason for kick", required=True)):
    action_type = "Kick"
    mod = interaction.user.mention
    if not await is_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        await user.send(
f"Hi there from {interaction.guild.name}. You have been kicked from the server due to '{reason}'.")
    except:
        pass
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.guild.kick(user)
    await interaction.send(f"{str(user)} has been kicked.")

@bot.slash_command(description="Ban a user from the server (for mods)")
async def ban(interaction: discord.Interaction,
        user: discord.Member = discord.SlashOption(name="user", description="User to ban", required=True),
        reason: str = discord.SlashOption(name="reason", description="Reason for ban", required=True),
        delete_message_days: int = discord.SlashOption(name="delete_messages", choices={"Don't Delete Messages" : 0, "Delete Today's Messages" : 1, "Delete 3 Days of Messages" : 3, 'Delete 1 Week of Messages' : 7}, default=0, description="Duration of messages from the user to delete (defaults to zero)", required=False)):
    action_type = "Ban"
    mod = interaction.user.mention

    if type(user) is not discord.Member:
        await interaction.send("User is not a member of the server", ephemeral=True)
        return 
    if not await is_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    if await is_banned(user, interaction.guild):
        await interaction.send("User is banned from the server!", ephemeral=True)
        return
    await interaction.response.defer()
    try:
        if interaction.guild.id == GUILD_ID:
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'. If you feel this ban was done in error, to appeal your ban, please fill the form below.\nhttps://forms.gle/8qnWpSFbLDLdntdt8")
        else:
            await user.send(
                f"Hi there from {interaction.guild.name}. You have been banned from the server due to '{reason}'.")
    except:
        pass
    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod} 
Reason: {reason}"""
        await ban_msg_channel.send(ban_msg)
    await interaction.guild.ban(user, delete_message_days=delete_message_days)
    await interaction.send(f"{str(user)} has been banned.")

@bot.slash_command(description="Unban a user from the server (for mods)")
async def unban(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="user", description="User to unban", required=True)):
    action_type = "Unban"
    mod = interaction.user.mention
    if not await is_moderator(interaction.user):
        await interaction.send(f"Sorry {mod}, you don't have the permission to perform this action.", ephemeral=True)
        return
    await interaction.response.defer()
    await interaction.guild.unban(user)
    await interaction.send(f"{str(user)} has been unbanned.")

    ban_msg_channel = bot.get_channel(gpdb.get_pref("modlog_channel", interaction.guild.id))
    if ban_msg_channel:
        try:
            last_ban_msg = await ban_msg_channel.history(limit=1).flatten()
            case_no = int(''.join(list(filter(str.isdigit, last_ban_msg[0].content.splitlines()[0])))) + 1
        except:
            case_no = 1
        ban_msg = f"""Case #{case_no} | [{action_type}]
Username: {str(user)} ({user.id})
Moderator: {mod}"""
        await ban_msg_channel.send(ban_msg)