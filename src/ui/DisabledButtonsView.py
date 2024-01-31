import nextcord as discord

options = ["A", "B", "C", "D"]

class DisabledButtonsView(discord.ui.View):
    def __init__(self, correct_answer: str):
        super().__init__(timeout=5)
        
        for option in options:
            button = discord.ui.Button(style=discord.ButtonStyle.danger, label=option, disabled=True)
            if option == correct_answer:
                button.style = discord.ButtonStyle.success
            self.add_item(button)
        