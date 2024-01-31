from .Select import Select
from .SelectMenuTopic import SelectMenuTopic
import nextcord as discord
from schemas.redis import TempSessionData

practice_subjects = {
  '0455': "Economics",
  #'0606': "Additional Mathematics",
  #'0607': "International Mathematics",
  '0620': "Chemistry",
  #'0580': "Mathematics",
  '0625': "Physics",
  '0610': "Biology",
  #'0417': "Information & Communication Technology (ICT)"
}

class SelectMenuSubject(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=300)

        self.subject = Select(
            name="subject",
            placeholder="Choose a subject",
            options=list(map(lambda x: discord.SelectOption(label=f"{x[1]} ({x[0]})", value=x[0]), practice_subjects.items())),
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

        self.add_item(self.subject)
        self.add_item(self.continue_button)
        self.add_item(self.cancel_button)

