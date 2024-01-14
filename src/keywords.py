from bot import bot, discord, pymongo, keywords
from constants import LINK, GUILD_ID
from mongodb import kwdb
from roles import is_moderator, is_bot_developer

class AddKeywords(discord.ui.Modal):
    def __init__(self):
        super().__init__("Add a keyword", timeout=None)

        self.keyword = discord.ui.TextInput(label="Add keyword", style=discord.TextInputStyle.short, placeholder="The keyword you would like to add", required=True)
        self.autoresponse = discord.ui.TextInput(label="Add response", style=discord.TextInputStyle.paragraph, placeholder="The response you would like to be sent", required=True)

        self.add_item(self.keyword)
        self.add_item(self.autoresponse)
    
    async def callback(self, interaction: discord.Interaction):
        kwdb.add_keyword(self.keyword.value, self.autoresponse.value, interaction.guild.id)
        keywords[interaction.guild.id] = kwdb.get_keywords(interaction.guild.id)
        await interaction.send(f"Created keyword `{self.keyword.value}` for autoresponse `{self.autoresponse.value}`", ephemeral=True, delete_after=2)

class RemoveKeywords(discord.ui.Modal):
    def __init__(self):
        super().__init__("Delete a keyword", timeout=None)

        self.keyword = discord.ui.TextInput(label="Delete keyword", style=discord.TextInputStyle.short, placeholder="The keyword you would like to delete", required=True)

        self.add_item(self.keyword)
    
    async def callback(self, interaction: discord.Interaction):
        kwdb.remove_keyword(self.keyword.value, interaction.guild.id)
        keywords[interaction.guild.id] = kwdb.get_keywords(interaction.guild.id)
        await interaction.send(f"Deleted keyword `{self.keyword}`", ephemeral=True, delete_after=2)

@bot.slash_command(name="keywords", description="Adds or Deletes a keyword (for mods)")
async def keywordscommand(interaction: discord.Interaction,
                        action_type: str = discord.SlashOption(name="action_type", description= "ADD or DELETE?", choices=["Add Keywords", "Delete Keywords"], required=True)):
        if not await is_moderator(interaction.user) and not await is_bot_developer(interaction.user):
            await interaction.send("You do not have the permissions to perform this action")
            return
        if action_type == "Add Keywords":
            await interaction.response.send_modal(modal=AddKeywords())
        elif action_type == "Delete Keywords":
            await interaction.response.send_modal(modal=RemoveKeywords())

@bot.slash_command(description="Display all keywords")
async def list_keywords(interaction: discord.Interaction):
    page = 1
    
    await interaction.response.defer()
    keywords = kwdb.keyword_list(interaction.guild.id)
    keywords = [item.values() for item in keywords]
    chunks = [list(keywords)[x:x + 9] for x in range(0, len(keywords), 9)]

    pages = []
    for n, chunk in enumerate(chunks):
        embed = discord.Embed(title="List of keywords", description=f"Page {n + 1} of {len(chunks)}", colour=discord.Colour.blurple())
        for keyword, autoresponse in chunk:
            embed.add_field(name=keyword, value="" + "\n", inline=True)
        pages.append(embed)

    if not page: page = 1

    first, prev = discord.ui.Button(emoji="⏪", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⬅️", style=discord.ButtonStyle.blurple)

    nex, last = discord.ui.Button(emoji="➡️", style=discord.ButtonStyle.blurple), discord.ui.Button(emoji="⏩", style=discord.ButtonStyle.blurple)
    if page == 1:
        first.disabled, prev.disabled = True, True
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
