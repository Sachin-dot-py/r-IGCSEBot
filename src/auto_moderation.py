from bot import bot, time
from mongodb import gpdb, punishdb
from moderation import convert_time

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * 60
SECONDS_PER_DAY = SECONDS_PER_HOUR * 24

@bot.event
async def on_auto_moderation_action_execution(automod_execution):
    guild = automod_execution.guild
    action_type = "Timeout"

    if automod_execution.action.type.name == "timeout":
        rule = await guild.fetch_auto_moderation_rule(automod_execution.rule_id)

        reason = rule.name  # Rule Name
        member = automod_execution.member  # Member Name
        timeout_time_seconds = automod_execution.action.metadata.duration_seconds  # Timeout Time in seconds

        human_readable_time = f"{timeout_time_seconds // SECONDS_PER_DAY}d {(timeout_time_seconds % SECONDS_PER_DAY) // SECONDS_PER_HOUR}h {(timeout_time_seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE}m {timeout_time_seconds % SECONDS_PER_MINUTE}s"
        ban_message_channel = bot.get_channel(gpdb.get_pref("modlog_channel", automod_execution.guild_id))

        if ban_message_channel:
            try:
                last_ban_message = await ban_message_channel.history(limit=1).flatten()
                case_no = (int("".join(list(filter(str.isdigit, last_ban_message[0].content.splitlines()[0]))))+ 1)
            except:
                case_no = 1
            timeout_message = f"""Case #{case_no} | [{action_type}]\nUsername: {member.name} ({member.id})\nModerator: Automod\nReason: {reason}\nDuration: {human_readable_time}\nUntil: <t:{int(time.time()) + timeout_time_seconds}> (<t:{int(time.time()) + timeout_time_seconds}:R>)""" # PEP-8 line len limit crying, but it's better than before

            await ban_message_channel.send(timeout_message)
            timeout_duration_simple = convert_time((str(timeout_time_seconds // 86400), str((timeout_time_seconds % 86400) // 3600), str((timeout_time_seconds % 3600) // 60), str(timeout_time_seconds % 60)))
            punishdb.add_punishment(case_no, member.id, "Automod", reason, "Timeout", duration=timeout_duration_simple)
