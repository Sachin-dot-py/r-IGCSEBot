from .SelectUsersView import SelectUsersView
import nextcord as discord
from schemas.redis import TempSessionData

class SelectMenuVisibility(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=300)

        self.public = discord.ui.Button(label="Public", style=discord.ButtonStyle.primary)
        async def public_callback(interaction: discord.Interaction):
            tempdata = TempSessionData.get(interaction.user.id)
            
            tempdata["private"] = False
            tempdata.save()
            self.stop()

        self.private = discord.ui.Button(label="Private", style=discord.ButtonStyle.primary)
        async def private_callback(interaction: discord.Interaction):
            tempdata = TempSessionData.get(interaction.user.id)
            
            tempdata["private"] = True
            tempdata.save()
            self.stop()

        self.public.callback = public_callback
        self.private.callback = private_callback

        self.add_item(self.public)
        self.add_item(self.private)