from bot import bot, discord, requests, json
from pyquery import PyQuery

order = ["A", "B", "C", "D"]

class Question:
    def __init__(self, embed: discord.Embed, view: discord.ui.View):
        self.embed = embed
        self.view = view

def build_question(interaction: discord.Interaction, question_pages, question_number: int):
    question_page = question_pages[question_number]
    html = question_page[0]["problem"][0]["body"]
    pq = PyQuery(html)
    embed = discord.Embed(title=f"Question {question_number + 1}", description=f"{pq.text().replace("  ", " ").replace("\n", "\n\n")}", color=0x5865f2)
    options = []
    for item in order:
        option_html = question_page[0][f"choice{item}"][0]["body"]
        pq = PyQuery(option_html)
        options.append(pq.text())
    view = Choice(interaction, options, order.index(question_page[0]["correctChoice"]), question_pages, question_number)
    return Question(embed, view)

class MultiChoiceButton(discord.ui.Button):
    def __init__(self, name: str, interaction: discord.Interaction):
        super().__init__(label=name, style=discord.ButtonStyle.blurple)
        self.author = interaction.user
    
    async def callback(self, interaction: discord.Interaction):
        if self.author.id != interaction.user.id:
            return await interaction.send(content="This is not for you!", ephemeral=True)
        view = self.view
        await view.check_answer(interaction, self.label)

class SkipButon(discord.ui.Button):
    def __init__(self, name: str, interaction: discord.Interaction, question_pages, question_number: int):
        super().__init__(label=name, style=discord.ButtonStyle.gray)
        self.author = interaction.user
        self.question_pages = question_pages
        self.question_number = question_number
    
    async def callback(self, interaction: discord.Interaction):
        if self.author.id != interaction.user.id:
            return await interaction.send(content="This is not for you!", ephemeral=True)
        question = build_question(interaction, self.question_pages, self.question_number + 1)
        await interaction.edit(embed=question.embed, view=question.view)

class Choice(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, options, correct_choice: int, question_pages, question_number: int):
        super().__init__()
        self.correct_choice = correct_choice
        self.options = options
        for option in options:
            self.add_item(MultiChoiceButton(option, interaction))
        self.add_item(SkipButon("Next", interaction, question_pages, question_number))

    async def check_answer(self, interaction: discord.Interaction, choice):
        selected_choice = self.options.index(choice)
        for i, item in enumerate(self.children):
            if item.label != "Next":
                item.disabled = True
            if i == selected_choice:
                if i == self.correct_choice:
                    item.style = discord.ButtonStyle.green
                else:
                    item.style = discord.ButtonStyle.red
            else:
                item.style = discord.ButtonStyle.gray
        embed = discord.Embed(title="Result", description=f"Your answer was {"correct" if selected_choice == self.correct_choice else "incorrect"}!", color=0x5865f2)
        embed.add_field(name="Your Answer", value=choice)
        embed.add_field(name="Correct Answer", value=self.children[self.correct_choice].label)
        await interaction.edit(embed=embed, view=self)

@bot.slash_command(description="Answer multiple choice questions from a savemyexams link")
async def mcq(interaction: discord.Interaction, url: str = discord.SlashOption(name="url", description="savemyexams url", required=True)):
    print(url)
    response = requests.get(url)
    pq = PyQuery(response.text)
    tag = pq("#__NEXT_DATA__")
    inner_html = tag.html()
    data = json.loads(inner_html)
    question_pages = data["props"]["pageProps"]["pages"]
    question_number = 0
    question = build_question(interaction, question_pages, question_number)
    await interaction.send(embed=question.embed, view=question.view)
