from bot import bot, discord
from constants import GUILD_ID
from data import reactionroles_data

class DropdownRR(discord.ui.Select):
    def __init__(self, category, options):
        self._options = options
        selectOptions = [
            discord.SelectOption(emoji=option[0], label=option[1], value=option[2]) for option in options
        ]
        if category == "Colors":
            super().__init__(placeholder="Select your Color", min_values=0, max_values=1, options=selectOptions)
        else:
            super().__init__(placeholder=f"Select your {category}", min_values=0, max_values=len(selectOptions), options=selectOptions)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        added_role_names = []
        removed_role_names = []
        for option in self._options:
            role = interaction.guild.get_role(int(option[2]))
            if str(option[2]) in self.values:
                if role not in interaction.user.roles:
                    await interaction.user.add_roles(role)
                    added_role_names.append(role.name)
            else:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    removed_role_names.append(role.name)
        if len(added_role_names) > 0 and len(removed_role_names) > 0:
            await interaction.send(
                f"Successfully opted for roles: {', '.join(added_role_names)} and unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)
        elif len(added_role_names) > 0 and len(removed_role_names) == 0:
            await interaction.send(f"Successfully opted for roles: {', '.join(added_role_names)}.", ephemeral=True)
        elif len(added_role_names) == 0 and len(removed_role_names) > 0:
            await interaction.send(f"Successfully unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)

class DropdownViewRR(discord.ui.View):
    def __init__(self, roles_type):
        super().__init__(timeout=None)

        for category, options in reactionroles_data[roles_type].items():
            self.add_item(DropdownRR(category, options))

class RolePickerCategories(discord.ui.Select):
    def __init__(self):
        options = ["Subject Roles", "Session Roles", "Study Ping Roles", "Server Roles"]
        super().__init__(
            placeholder="Choose a roles category...",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=option) for option in options],
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        roles_type = self.values[0]
        view = DropdownViewRR(roles_type)
        await interaction.response.edit_message(content=f"Choose your {roles_type}", view=view)

class RolePickerCategoriesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RolePickerCategories())

    @discord.ui.button(label="Remove all Roles", style=discord.ButtonStyle.red, row=1)
    async def remove_roles_btn(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        removed_role_names = []
        for category in reactionroles_data.values():
            for options in category.values():
                for option in options:
                    role = interaction.guild.get_role(int(option[2]))
                    if role in interaction.user.roles:
                        await interaction.user.remove_roles(role)
                        removed_role_names.append(role.name)
        if len(removed_role_names) > 0:
            await interaction.send(f"Successfully unopted from roles: {', '.join(removed_role_names)}.", ephemeral=True)
        else:
            await interaction.send("No roles to remove! Please pick up roles first.", ephemeral=True)


@bot.slash_command(description="Pick up your roles", guild_ids=[GUILD_ID])
async def roles(interaction: discord.Interaction):
    await interaction.send(view=RolePickerCategoriesView(), ephemeral=True)

@bot.command(description="Dropdown for picking up reaction roles", guild_ids=[GUILD_ID])
async def roles(ctx):
    await ctx.send(view=RolePickerCategoriesView())