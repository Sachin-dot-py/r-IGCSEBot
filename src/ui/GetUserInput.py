import nextcord as discord
from schemas.redis import TempSessionData

class GetUserInput(discord.ui.Modal):
    def __init__(self):
        super().__init__(timeout=300, title="Customise this session")
        self.minimum_year = discord.ui.TextInput(
            style=discord.TextInputStyle.short,
            placeholder="2018",
            label="Minimum year",
            custom_id="minimum_year",
            default_value="2018",
            min_length=4,
            max_length=4
        )
        self.limit = discord.ui.TextInput(
            style=discord.TextInputStyle.short,
            placeholder="10",
            label="Number of questions (max: 99)",
            custom_id="limit",
            default_value="10",
            max_length=2
        )

        self.add_item(self.minimum_year)
        self.add_item(self.limit)

    async def callback(self, interaction: discord.Interaction):
        
        tempdata = TempSessionData.get(interaction.user.id)
        tempdata.minimum_year = int(self.minimum_year.value)
        tempdata.limit = int(self.limit.value)
        tempdata.save()

        self.stop()

    async def on_error(self, interaction: discord.Interaction, exception: Exception):
        TempSessionData.delete(str(interaction.user.id))
        await interaction.send(f"An error occured, please try again.", ephemeral=True)

    async def on_timeout(self, interaction: discord.Interaction):
        TempSessionData.delete(str(interaction.user.id))
        await interaction.send(f"Timed out.", ephemeral=True)