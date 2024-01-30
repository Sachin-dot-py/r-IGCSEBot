from bot import bot, discord
from constants import GUILD_ID
from roles import is_moderator, is_server_booster, has_role
from data import reactionroles_data


class DropdownRR(discord.ui.Select):
    def __init__(self, category, options):
        self._options = options
        selectOptions = [
            discord.SelectOption(emoji=option[0], label=option[1], value=option[2])
            for option in options
        ]
        if category == "Colors":
            super().__init__(
                placeholder="Select your Color",
                min_values=0,
                max_values=1,
                options=selectOptions,
            )
        else:
            super().__init__(
                placeholder=f"Select your {category}",
                min_values=0,
                max_values=len(selectOptions),
                options=selectOptions,
            )

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
                f"Successfully opted for roles: {', '.join(added_role_names)} and unopted from roles: {', '.join(removed_role_names)}.",
                ephemeral=True,
            )
        elif len(added_role_names) > 0 and len(removed_role_names) == 0:
            await interaction.send(
                f"Successfully opted for roles: {', '.join(added_role_names)}.",
                ephemeral=True,
            )
        elif len(added_role_names) == 0 and len(removed_role_names) > 0:
            await interaction.send(
                f"Successfully unopted from roles: {', '.join(removed_role_names)}.",
                ephemeral=True,
            )


class DropdownViewRR(discord.ui.View):
    def __init__(self, roles_type):
        super().__init__(timeout=None)

        for category, options in reactionroles_data[roles_type].items():
            self.add_item(DropdownRR(category, options))


@bot.slash_command(
    description="Choose a display colour for your name", guild_ids=[GUILD_ID]
)
async def colorroles(interaction: discord.Interaction):
    if (
        await is_moderator(interaction.user)
        or await is_server_booster(interaction.user)
        or await has_role(interaction.user, "100+ Rep Club")
    ):
        await interaction.send(view=DropdownViewRR("Color Roles"), ephemeral=True)
    else:
        await interaction.send(
            "This command is only available for Server Boosters and 100+ Rep Club members",
            ephemeral=True,
        )


@bot.command(description="Choose a display colour for your name", guild_ids=[GUILD_ID])
async def colorroles(ctx):
    if (
        await is_moderator(ctx.author)
        or await is_server_booster(ctx.author)
        or await has_role(ctx.author, "100+ Rep Club")
    ):
        await ctx.send(view=DropdownViewRR("Color Roles"))
    else:
        await ctx.send(
            "This command is only available for Server Boosters and 100+ Rep Club members"
        )
