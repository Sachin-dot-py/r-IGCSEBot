import nextcord as discord
from schemas.redis import Session


class JoinSessionListView(discord.ui.View):
    def __init__(self, sessions: list[discord.SelectOption], interaction: discord.Interaction):
        super().__init__(timeout=300)
        select_menu = discord.ui.Select(custom_id="join_session", placeholder="Select a session", options=sessions)
        self.add_item(select_menu)
        
        self.join_button = discord.ui.Button(label="Join", style=discord.ButtonStyle.success, custom_id="join")
        async def join_callback(interaction: discord.Interaction):
            self.values = select_menu.values
            self.stop()
        
        self.cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel")
        async def cancel_callback(interaction: discord.Interaction):
            self.values = None
            self.stop()
            
        self.join_button.callback = join_callback
        self.cancel_button.callback = cancel_callback
            
        self.add_item(self.join_button)
        self.add_item(self.cancel_button)
        
        
        
        
        