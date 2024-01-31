from .UserSelect import UserSelect
import nextcord as discord
from schemas.redis import TempSessionData, Session

class SelectUsersView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=300)

        self.user_select = UserSelect(
            placeholder="Select users",
            max_values=25
        )

        self.continue_button = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green)
        async def continue_callback(interaction: discord.Interaction):
            self.stop()


        self.cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
        async def cancel_callback(interaction: discord.Interaction):
            await interaction.edit(content="Cancelled!", view=None)
            TempSessionData.delete(str(interaction.user.id))
            

        self.continue_button.callback = continue_callback
        self.cancel_button.callback = cancel_callback

        self.add_item(self.user_select)
        self.add_item(self.continue_button)
        self.add_item(self.cancel_button)