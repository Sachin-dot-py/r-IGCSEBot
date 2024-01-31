import nextcord as discord
from schemas.redis import Session, Question, User, ExtendedModel, View
from .DisabledButtonsView import DisabledButtonsView
from redis_om import NotFoundError

async def get_from_db(primary_key: str, db: ExtendedModel) -> bool:
    try:
        data = db.get(primary_key)
        return data
    except NotFoundError:
        return None

class MCQButton(discord.ui.Button):
    def __init__(self, label: str, custom_id: str):
        super().__init__(style=discord.ButtonStyle.primary, label=label, custom_id=custom_id)
        self.label = label
        self.view_name = custom_id[:-2]
        
    async def callback(self, interaction: discord.Interaction):
        user_db = await get_from_db(interaction.user.id, User)
        
        if not user_db or not user_db.playing:
            await interaction.response.send_message("You are not in a session.", ephemeral=True)
            return
        
        session = await get_from_db(user_db.session_id, Session)
        
        users = session["users"] + [session["started_by"]]
        
        if not session or str(interaction.user.id) not in users:
            await interaction.response.send_message("You are not in this session.", ephemeral=True)
            return
        
        question = Question.get(session.currently_solving)
        
        if str(interaction.user.id) in question.user_answers.keys():
            await interaction.response.send_message("You have already answered this question.", ephemeral=True)
            return
        
        question.user_answers[str(interaction.user.id)] = self.label
        if self.label == question.answers:
            await interaction.response.send_message("Correct!", ephemeral=True)
        else:
            await interaction.response.send_message("Incorrect!", ephemeral=True)
        
        if sorted(list(question.user_answers.keys())) == sorted(users):
            View.delete(self.view_name)
            question.solved = 1
            question.save()
            session.currently_solving = "none"
            session.save()
            thread = interaction.channel
            embed = discord.Embed(title="Question solved!")
            embed.description = f"Question: {question.question_name}\nCorrect answer: {question.answers}\n\n"
            for user in question.user_answers.keys():
                embed.description += f"<@{user}>: {question.user_answers[user]}\n"
                
            await interaction.message.edit(view=DisabledButtonsView(question.answers))
            await thread.send(embed=embed)
                
        question.save()