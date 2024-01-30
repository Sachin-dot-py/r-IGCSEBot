from bot import bot, discord, requests, json
from pyquery import PyQuery
from typing import List, cast

order = ["A", "B", "C", "D"]


class Question:
    def __init__(self, embed: discord.Embed, view: discord.ui.View):
        self.embed = embed
        self.view = view


async def build_question(
    interaction: discord.Interaction, question_pages, question_number: int
) -> Question | None:
    if question_number >= len(question_pages):
        await interaction.send(
            content="You have already reached the last question!", ephemeral=True
        )
        return
    question_page = question_pages[question_number]
    html = question_page[0]["problem"][0]["body"]
    pq = PyQuery(html)
    embed = discord.Embed(
        title=f"Question {question_number + 1}",
        description=str(pq.text()).replace("  ", " ").replace("\n", "\n\n"),
        color=0x5865F2,
    )
    options = []
    try:
        for item in order:
            option_html = question_page[0][f"choice{item}"][0]["body"]
            pq = PyQuery(option_html)
            options.append(pq.text())
        view = Choice(interaction, options, question_pages, question_number)
        if view.is_valid:
            return Question(embed, view)
        else:
            await interaction.send(
                content=f"Question {question_number + 1} contains data that is too complex to display!",
                ephemeral=True,
            )
            return await build_question(
                interaction, question_pages, question_number + 1
            )
    except Exception as e:
        print(e)
        return await build_question(interaction, question_pages, question_number + 1)


class MultiChoiceButton(discord.ui.Button):
    def __init__(self, name: str, interaction: discord.Interaction):
        super().__init__(label=name, style=discord.ButtonStyle.blurple)
        self.author = interaction.user

    async def callback(self, interaction: discord.Interaction):
        if self.author is None or self.view is None or interaction.user is None:
            return
        if self.author.id != interaction.user.id:
            await interaction.send(content="This is not for you!", ephemeral=True)
            return
        view = self.view
        await view.check_answer(interaction, self.label)


class SkipButon(discord.ui.Button):
    def __init__(
        self,
        name: str,
        interaction: discord.Interaction,
        question_pages,
        question_number: int,
    ):
        super().__init__(label=name, style=discord.ButtonStyle.gray)
        self.author = interaction.user
        self.question_pages = question_pages
        self.question_number = question_number

    async def callback(self, interaction: discord.Interaction):
        if self.author is None or self.view is None or interaction.user is None:
            return
        if self.author.id != interaction.user.id:
            await interaction.send(content="This is not for you!", ephemeral=True)
            return
        question = await build_question(
            interaction, self.question_pages, self.question_number + 1
        )
        if isinstance(question, Question):
            await interaction.edit(embed=question.embed, view=question.view)


class Choice(discord.ui.View):
    def __init__(
        self,
        interaction: discord.Interaction,
        options,
        question_pages,
        question_number: int,
    ):
        super().__init__()
        self.correct_choice = order.index(
            question_pages[question_number][0]["correctChoice"]
        )
        self.solution = question_pages[question_number][0]["solution"][0]["body"]
        self.options = options
        self.is_valid: bool = True
        for option in options:
            if len(option) > 0:
                self.add_item(MultiChoiceButton(option, interaction))
            else:
                self.is_valid = False
                break
        self.add_item(SkipButon("Next", interaction, question_pages, question_number))

    async def check_answer(self, interaction: discord.Interaction, choice):
        selected_choice = self.options.index(choice)
        buttons = cast(List[discord.ui.Button], self.children)
        for i, item in enumerate(buttons):
            if item.label != "Next":
                item.disabled = True
            if i == selected_choice:
                if i == self.correct_choice:
                    item.style = discord.ButtonStyle.green
                else:
                    item.style = discord.ButtonStyle.red
            else:
                item.style = discord.ButtonStyle.gray
        correct_answer = cast(discord.ui.Button, self.children[self.correct_choice])
        pq = PyQuery(self.solution)
        explanation = str(pq.text())
        embed = discord.Embed(title="Result", description=explanation, color=0x5865F2)
        embed.add_field(name="Your Answer", value=choice)
        embed.add_field(name="Correct Answer", value=correct_answer.label)
        await interaction.edit(embed=embed, view=self)


@bot.slash_command(
    description="Answer multiple choice questions from a savemyexams link"
)
async def mcq(
    interaction: discord.Interaction,
    url: str = discord.SlashOption(
        name="url", description="savemyexams url", required=True
    ),
):
    print(url)
    response = requests.get(url)
    pq = PyQuery(response.text)
    tag = pq("#__NEXT_DATA__")
    inner_html = str(tag.html())
    data = json.loads(inner_html)
    question_pages = data["props"]["pageProps"]["pages"]
    question_number = 0
    question = await build_question(interaction, question_pages, question_number)
    if isinstance(question, Question):
        await interaction.send(embed=question.embed, view=question.view)
