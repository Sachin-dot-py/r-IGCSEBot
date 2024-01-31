import nextcord as discord
from schemas.redis import TempSessionData

class Select(discord.ui.Select):
    def __init__(self, name, placeholder: str, options: list, max_values: int = 1):
        super().__init__(placeholder=placeholder, options=options, max_values=max_values)
        self.name = name

    async def callback(self, interaction: discord.Interaction):
        tempdata = TempSessionData.get(interaction.user.id)
        
        if tempdata[self.name] and type(tempdata[self.name]) == list:
            tempdata[self.name] = tempdata[self.name] + interaction.data["values"]
        elif len(interaction.data["values"]) == 1 and self.name != "topics":
            tempdata[self.name] = interaction.data["values"][0]
        else:
            tempdata[self.name] = interaction.data["values"]

        tempdata.save()