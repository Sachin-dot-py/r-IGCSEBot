import nextcord as discord

class AddRemoveUserView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        user_select = discord.ui.UserSelect(custom_id="add_remove_user", placeholder="Select a user", max_values=1)
        self.add_item(user_select)
        self.values = []
        
        self.confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success, custom_id="confirm")
        async def confirm_callback(interaction: discord.Interaction):
            self.values = user_select.values
            self.stop()
        
        self.cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel")
        async def cancel_callback(interaction: discord.Interaction):
            self.values = None
            self.stop()
            
        self.confirm_button.callback = confirm_callback
        self.cancel_button.callback = cancel_callback
            
        self.add_item(self.confirm_button)
        self.add_item(self.cancel_button)
        
        