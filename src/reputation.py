from bot import bot, discord, time
from mongodb import repdb
from roles import is_moderator, is_bot_developer
from  constants import MODLOG_CHANNEL_ID


@bot.slash_command(name="rep", description="View someone's current rep")
async def rep(interaction: discord.Interaction,
              user: discord.User = discord.SlashOption(name="user", description="User to view rep of", required=False)):
    await interaction.response.defer()
    if user is None:
        user = interaction.user
    rep = repdb.get_rep(user.id, interaction.guild.id)
    if rep is None:
        rep = 0
    await interaction.send(f"{user} has {rep} rep.", ephemeral=False)

@bot.slash_command(name="change_rep", description="Change someone's current rep (for mods)")
async def change_rep(interaction: discord.Interaction, user: discord.User = discord.SlashOption(name="user", description="User to view rep of", required=True), new_rep: int = discord.SlashOption(name="new_rep", description="New rep amount", required=True, min_value=0, max_value=99999)):
    if await is_moderator(interaction.user):
        await interaction.response.defer()
        Logging = bot.get_channel(MODLOG_CHANNEL_ID)
        timern = int(time.time()) + 1
        user_id = int(user.id)
        new_rep = int(new_rep)
        guild_id = int(interaction.guild.id)
        rep = repdb.change_rep(user_id, new_rep, guild_id)
        embed = discord.Embed(description="Rep Changed", colour=discord.Colour.blurple())
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        embed.add_field(name="New Rep", value={new_rep}, inline=False)
        embed.add_field(name="Date", value=f"<t:{timern}:F>", inline=False)
        embed.add_field(name="ID", value= f"```py\nUser = {interaction.user.id}\nBot = 861445044790886467```", inline=False)
        embed.set_footer(text=f"r/IGCSE Bot#2063")
        await Logging.send(embed=embed)          
        await interaction.send(f"{user} now has {rep} rep.", ephemeral=False)
    else:
        await interaction.send("You are not authorized to use this command.", ephemeral=True)

@bot.slash_command(description="View the current rep leaderboard")
async def leaderboard(interaction: discord.Interaction, page: int = discord.SlashOption(name="page", description="Page number to to display", required=False, min_value=1, max_value=99999), user_to_find: discord.User = discord.SlashOption(name="user", description="User to find on the leaderboard", required=False)):
    await interaction.response.defer()
    leaderboard = repdb.rep_leaderboard(interaction.guild.id)
    leaderboard = [item.values() for item in leaderboard]
    chunks = [list(leaderboard)[x:x + 9] for x in range(0, len(leaderboard), 9)]
    pages = []
    for n, chunk in enumerate(chunks):
        embed = discord.Embed(title="Reputation Leaderboard", description=f"Page {n + 1} of {len(chunks)}", colour=discord.Colour.blurple())
        for user, rep in chunk:
            if user_to_find:
                if user_to_find.id == user:
                    page = n + 1
            user_name = interaction.guild.get_member(user)
            if rep == 0 or user_name is None:
                repdb.delete_user(user, interaction.guild.id)
            else:
                embed.add_field(name=user_name, value=str(rep) + "\n", inline=True)
        pages.append(embed)

    if not page: page = 1

    first, prev = discord.ui.Button(emoji="⏪", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.blurple)
    if page == 1:
        first.disabled, prev.disabled = True, True

    nex, last = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⏩", style=discord.ButtonStyle.blurple)
    view = discord.ui.View(timeout=120)

    async def timeout():
        nonlocal message
        disabled = discord.ui.View()
        for b in view.children:
            d = b
            d.disabled = True
            disabled.add_item(d)
        await message.edit(view=disabled)
    view.on_timeout = timeout

    async def f_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        view = discord.ui.View(timeout=None)
        first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        page = 1
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def p_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        page -= 1
        view = discord.ui.View(timeout=None)
        if page == 1:
            first.disabled, prev.disabled, nex.disabled, last.disabled = True, True, False, False
        else:
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def n_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        page += 1
        view = discord.ui.View(timeout=None)
        if page == len(pages):
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
        else:
            first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, False, False
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    async def l_callback(b_interaction):
        if b_interaction.user != interaction.user:
            await b_interaction.response.send_message("This is not for you.", ephemeral=True)
            return
        nonlocal page
        view = discord.ui.View(timeout=None)
        first.disabled, prev.disabled, nex.disabled, last.disabled = False, False, True, True
        view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)
        page = len(pages)
        await b_interaction.response.edit_message(embed=pages[page - 1], view=view)

    first.callback, prev.callback, nex.callback, last.callback = f_callback, p_callback, n_callback, l_callback
    view.add_item(first); view.add_item(prev); view.add_item(nex); view.add_item(last)

    message = await interaction.send(embed=pages[page - 1], view=view)