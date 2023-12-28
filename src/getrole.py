from bot import discord, bot, commands, pymongo, traceback, random
from constants import TOKEN, LINK, GUILD_ID
from roles import is_staff_moderator, has_role

questions = {
    "No. of members gained on Discord server": "143000",
    "No. of members reached by our repository": "321000",
    "No. of countries users are from (on Discord)": "1100",
    "The month we hit 20,000 users (on Discord)": "august",
    "No. of members gained on Subreddit": "132000",
    }

class GetRole(discord.ui.Modal):
      def __init__(self):
            super().__init__("Answer a question to get the '2023' role", timeout=None)

            self.question, self.answer = random.choice(list(questions.items()))

            self.user_answer = discord.ui.TextInput(
                  label=self.question, style=discord.TextInputStyle.short, placeholder="Please write in lower case and don't use commas...", required=True
            )

            self.add_item(self.user_answer)
            
      async def callback(self, interaction: discord.Interaction):
            role = interaction.guild.get_role(1188697866412236800)
            if role in interaction.user.roles:
                  await interaction.send("You already have this role!", ephemeral=True)
                  return
            if self.user_answer.value == self.answer:
                  await interaction.user.add_roles(role)
                  await interaction.send("Correct answer! The <@&1188697866412236800> role has been added to your profile.", ephemeral=True)
            else:
                  client = pymongo.MongoClient(LINK)
                  db = client.IGCSEBot
                  attempts = db["attempts"]
                  user = attempts.find_one({"id": interaction.user.id})
                  attempts.update_one({'id': interaction.user.id}, {"$inc": {"attempts_left": -1}})
                  user['attempts_left'] = user['attempts_left'] - 1
                  await interaction.send(f"Incorrect Answer! You have {int(user['attempts_left'])} attempts left.", ephemeral=True)

@bot.slash_command(name="getrole", description="answer the questions to get the 2023 role.", guild_ids=[GUILD_ID])
async def getrole(interaction: discord.Interaction):
      client = pymongo.MongoClient(LINK)
      db = client.IGCSEBot
      attempts = db["attempts"]
      user = attempts.find_one({"id": interaction.user.id})
      if not user:
            user = {"id": interaction.user.id, "attempts_left": 3}
            attempts.insert_one(user)
      if user['attempts_left'] == 0:
            await interaction.send("You can't answer more than 3 times.", ephemeral=True)
            return

      await interaction.response.send_modal(modal=GetRole())


@bot.slash_command(name = "reset_attempts", description = "Reset the attempts data", guild_ids = [GUILD_ID])
async def resetgttr(interaction: discord.Interaction,
                    user: discord.User = discord.SlashOption(name="user", description="reset someone's current attempts", required=False)):
      if not await is_staff_moderator(interaction.user) and not await has_role(interaction.user, "Bot Developer"):
                  await interaction.send("You do not have the necessary permissions to perform this action", ephemeral = True)
                  return
      await interaction.response.defer(ephemeral = True)
      client = pymongo.MongoClient(LINK)
      db = client.IGCSEBot
      attempts = db["attempts"]
      if user == None:
            user_id = interaction.user.id
            attempts.delete_one({"id": user_id})
            await interaction.send(f"{interaction.user.mention}'s attempts have been reset to 3.", ephemeral=True)
      else:
            user_id = user.id
            attempts.delete_one({"id": user_id})
            await interaction.send(f"{interaction.user.mention}'s attempts have been reset to 3.", ephemeral=True)
