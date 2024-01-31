import nextcord as discord
from schemas.redis import TempSessionData

class UserSelect(discord.ui.UserSelect):
    def __init__(self, placeholder: str, max_values: int = 1):
        super().__init__(placeholder=placeholder, max_values=max_values)

    async def callback(self, interaction: discord.Interaction):
        tempdata = TempSessionData.get(interaction.user.id)
        tempdata.users = interaction.data["values"]
        tempdata.save()