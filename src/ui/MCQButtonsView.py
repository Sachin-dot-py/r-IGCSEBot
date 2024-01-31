import nextcord as discord
from .MCQButton import MCQButton

options = ["A", "B", "C", "D"]

class MCQButtonsView(discord.ui.View):
    def __init__(self, question_name: str):
        super().__init__(timeout=None)
        
        for option in options:
            # This is a persistent view, custom IDs are required.
            button = MCQButton(label=option, custom_id=f"{question_name}_{option}")
            self.add_item(button)
            
        