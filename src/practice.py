from bot import bot, discord
from redis_om import NotFoundError, Migrator
from schemas.redis import Session, User, TempSessionData, ExtendedModel, Question, View
from ui import GetUserInput, SelectMenuSubject, SelectMenuTopic, SelectMenuVisibility, SelectUsersView, JoinSessionListView, AddRemoveUserView
from mongodb import questionsdb
from data import practice_subjects
import uuid

async def get_from_db(primary_key: str, db: ExtendedModel) -> bool:
    try:
        data = db.get(primary_key)
        return data
    except NotFoundError:
        return None
    
async def save_questions(questions: list, session_id: str) -> list[Question]:
    questions_mapped = list(map(lambda x: Question(question_name=f"{x['subject']}_{x['season']}{str(x['year'])[2:4]}_qp_{x['paper']}{x['variant']}_q{x['questionNumber']}", questions=x["questions"], answers=x["answers"], session_id=session_id), questions))
    for question in questions_mapped:
        question.save()
        
    return questions_mapped

async def close_session(session: Session, message: str):
    thread = bot.get_channel(int(session["thread_id"]))
    
    questions = Question.find(Question.session_id == session.session_id).all()
    
    number_of_correct_answers: dict[str, str] = {}
    number_of_answers = {}
    
    for question in questions:
        user_answers = question["user_answers"]
        correct_answer = question["answers"]
        for user in user_answers.keys():
            if user not in number_of_answers.keys():
                number_of_answers[user] = 0
                
            number_of_answers[user] += 1
            
            if user not in number_of_correct_answers.keys():
                number_of_correct_answers[user] = 0
            if user_answers[user] == correct_answer:
                number_of_correct_answers[user] += 1
                
    number_of_correct_answers = dict(sorted(number_of_correct_answers.items(), key=lambda x: x[1], reverse=True))
    solved_questions = list(filter(lambda x: x["solved"] == 1, questions))
    unsolved_message = ""
    if len(solved_questions) != len(questions):
        unsolved_message = f" out of which only {len(solved_questions)} were solved by everyone"
    
    embed = discord.Embed(title="Session Ended!")
    embed.description = f"This session had {len(questions)} questions{unsolved_message}.\nThe scores for each user are as follows:\n\n"
    for user, score in number_of_correct_answers.items():
        embed.description += f"<@{user}>: {score}/{number_of_answers[user]}\n"
        
    await thread.send(embed=embed)
    await thread.send(message)
    
    
    await thread.edit(archived=True, locked=True)
    
    for user_id in session["users"]:
        User.delete(user_id)

    User.delete(session["started_by"])
    
    for question in questions:
        Question.delete(question.question_name)
        View.delete(question.question_name)
        
    Session.delete(session.session_id)


async def new_session(interaction: discord.Interaction):
    user_in_session = await get_from_db(str(interaction.user.id), User)
    if user_in_session and user_in_session["playing"]:
        await interaction.response.send_message("You are already in a session! Please leave that session using `/practice leave`.", ephemeral=True)
        return

    if await get_from_db(str(interaction.user.id), TempSessionData):
        TempSessionData.delete(str(interaction.user.id))

    session_data = TempSessionData(user_id=str(interaction.user.id))
    session_data.save()

    modal = GetUserInput()
    await interaction.response.send_modal(modal=modal)
    timedout = await modal.wait()
    if timedout:
        TempSessionData.delete(str(interaction.user.id))

    views = [
        SelectMenuSubject,
        SelectMenuTopic,
        SelectMenuVisibility,
        SelectUsersView
    ]

    msg = interaction.message or None

    for view in views:
        view: discord.ui.View = view(interaction)
        if msg is None:
            msg = await interaction.send(view=view, ephemeral=True)
        else:
            await msg.edit(view=view)
    
        timedout = await view.wait()
        if timedout:
            await msg.edit(content="Timed out!", view=None)
            TempSessionData.delete(str(interaction.user.id))
            return

    tempdata = TempSessionData.get(interaction.user.id)
    
    questions = questionsdb.get_questions(
        subject_code=tempdata["subject"],
        minimum_year=int(tempdata["minimum_year"]),
        limit=int(tempdata["limit"]),
        topics=tempdata["topics"]
    )
    session_id = str(uuid.uuid4()).split('-')[0]
    questions = await save_questions(list(questions), session_id)
    
    if not questions or len(list(questions)) == 0:
        await msg.edit(content="No questions found for the selected subject and topics.", view=None)
        TempSessionData.delete(str(interaction.user.id))
        return

    if tempdata["private"]:
        thread_type = discord.ChannelType.private_thread
    else:
        thread_type = discord.ChannelType.public_thread

    thread = await interaction.channel.create_thread(name=f"{interaction.user}'s practice session", type=thread_type)

    await thread.add_user(interaction.user)

    await msg.edit(content=f"Created a new practice session in {thread.mention}!", view=None)
    
    if str(interaction.user.id) in tempdata["users"]:
        tempdata["users"].remove(str(interaction.user.id))
    
    session = Session(
        session_id=session_id,
        channel_id=str(interaction.channel.id),
        thread_id=str(thread.id),
        subject=tempdata["subject"],
        topics=tempdata["topics"],
        limit=tempdata["limit"],
        minimum_year=tempdata["minimum_year"],
        users=tempdata["users"],
        started_by=str(interaction.user.id),
        private=tempdata["private"],
        paused=False
    )

    for user_id in tempdata["users"]:
        user = interaction.guild.get_member(user_id) or await interaction.guild.fetch_member(user_id)
        await thread.add_user(user)

        user_db = User(
            user_id=str(user.id),
            playing=True,
            session_id=str(session.session_id),
            subject=tempdata["subject"],
        )
        user_db.save()

    user = User(
        user_id=str(interaction.user.id),
        playing=True,
        session_id=str(session.session_id),
        subject=tempdata["subject"],
    )
        
    user.save()

    TempSessionData.delete(str(interaction.user.id))

    mentioned_users = list(map(lambda x: f"<@{x}>", tempdata["users"]))

    await thread.send(f"{interaction.user.mention} has started a new practice session!\n\nUsers: {', '.join(mentioned_users)}\nSession ID: {session.session_id}")
    session.save()


async def leave_session(interaction: discord.Interaction):
    user = await get_from_db(str(interaction.user.id), User)
    if not user or not user["playing"]:
        await interaction.response.send_message("You are currently not in a session!", ephemeral=True)
        return

    session = await get_from_db(user["session_id"], Session)

    if session["started_by"] == str(interaction.user.id):
        await interaction.response.send_message("You cannot leave a session you started! Please end the session using `/practice end` instead.", ephemeral=True)
        return
    
    session["users"].remove(str(interaction.user.id))

    session.save()

    thread = interaction.guild.get_thread(int(session["thread_id"]))
    await thread.remove_user(interaction.user)

    User.delete(str(interaction.user.id))

    await interaction.response.send_message("Left the session!", ephemeral=True)

async def end_session(interaction: discord.Interaction):
    user = await get_from_db(str(interaction.user.id), User)
    if not user or not user["playing"]:
        await interaction.response.send_message("You are currently not in a session!", ephemeral=True)
        return

    session = await get_from_db(user["session_id"], Session)

    if session["started_by"] != str(interaction.user.id):
        await interaction.response.send_message("You cannot end a session you did not start! Use `/practice leave` to leave the session instead.", ephemeral=True)
        return
    
    await interaction.response.send_message("Ended the session!", ephemeral=True)
    
    await close_session(session, f"{interaction.user.mention} has ended the session!")
    
    

async def list_sessions(interaction: discord.Interaction):
    
    sessions = Session.find(Session.private == 0).all()

    if not sessions:
        await interaction.response.send_message("There are no public sessions available at the moment! Create one by running `/practice new`.", ephemeral=True)
        return
    
    embed = discord.Embed(title="Public sessions", color=discord.Color.random(), description="Use `/practice join <session_id>` to join a session!")
    for session in sessions:
        embed.add_field(name=f"Session ID: {session.session_id}", value=f"Subject: {practice_subjects[session['subject']]}\nUsers: {len(session['users'])}", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def pause_session(interaction: discord.Interaction):
    user = await get_from_db(str(interaction.user.id), User)
    if not user or not user["playing"]:
        await interaction.response.send_message("You are currently not in a session!", ephemeral=True)
        return

    session = await get_from_db(user["session_id"], Session)

    if session["started_by"] != str(interaction.user.id):
        await interaction.response.send_message("You cannot pause a session you did not start!", ephemeral=True)
        return
    
    if session["paused"] == 1:
        await interaction.response.send_message("The session is already paused!", ephemeral=True)
        return
    
    session["paused"] = True
    session.save()

    thread = interaction.guild.get_thread(int(session["thread_id"]))
    await thread.send(f"{interaction.user.mention} has paused this session!")
    await thread.edit(locked=True)

    await interaction.response.send_message("Paused the session!", ephemeral=True)


async def resume_session(interaction: discord.Interaction):
    user = await get_from_db(str(interaction.user.id), User)
    if not user or not user["playing"]:
        await interaction.response.send_message("You are currently not in a session!", ephemeral=True)
        return

    session = await get_from_db(user["session_id"], Session)

    if session["started_by"] != str(interaction.user.id):
        await interaction.response.send_message("You cannot resume a session you did not start!", ephemeral=True)
        return
    
    if session["paused"] == 0:
        await interaction.response.send_message("This session is not paused!", ephemeral=True)
        return
    
    session["paused"] = False
    session.save()

    thread = interaction.guild.get_thread(int(session["thread_id"]))
    await thread.send(f"{interaction.user.mention} has resumed this session!")
    await thread.edit(locked=False)

    await interaction.response.send_message("Resumed the session!", ephemeral=True)


async def add_to_session(interaction: discord.Interaction):
    
    user_in_session = await get_from_db(str(interaction.user.id), User)
    if not user_in_session or not user_in_session["playing"]:
        await interaction.response.send_message("You are currently not in a session!", ephemeral=True)
        return

    user_owns_session = Session.find(Session.started_by == str(interaction.user.id)).all()
    if not user_owns_session:
        await interaction.response.send_message("Only the owner of the session can add others!", ephemeral=True)
        return
    
    session = user_owns_session[0]
    
    userview = AddRemoveUserView()
    interaction.message = await interaction.send("Select a user to add to the session!", view=userview, ephemeral=True)
    
    timedout = await userview.wait()
    
    if timedout or not userview.values:
        await interaction.edit("Cancelled!", view=None)
        return
    
    user = userview.values[0]

    if str(user.id) in session["users"]:
        await interaction.edit("That user is already in this session!", ephemeral=True)
        return
    
    user_in_another_session = await get_from_db(str(user.id), User)
    if user_in_another_session and user_in_another_session["playing"]:
        await interaction.edit("That user is already in another session!", ephemeral=True)
        return

    thread = interaction.guild.get_thread(int(session["thread_id"]))
    await thread.add_user(user)
    await thread.send(f"{user.mention} has been added to the session!")
        
    user_db = User(
        user_id=str(user.id),
        playing=True,
        session_id=str(session.session_id),
        subject=session["subject"],
    )
    user_db.save()

    session["users"].append(str(user.id))
    session.save()

    await interaction.edit(f"Added {user.mention} to the session!", view=None)


async def remove_from_session(interaction: discord.Interaction):
    
    user_in_session = await get_from_db(str(interaction.user.id), User)
    if not user_in_session or not user_in_session["playing"]:
        await interaction.response.send_message("You are currently not in a session!", ephemeral=True)
        return

    user_owns_session = Session.find(Session.started_by == str(interaction.user.id)).all()
    if not user_owns_session:
        await interaction.response.send_message("Only the owner of the session can remove others!", ephemeral=True)
        return
    
    session = user_owns_session[0]
    
    userview = AddRemoveUserView()
    interaction.message = await interaction.send("Select a user to remove from the session!", view=userview, ephemeral=True)
    
    timedout = await userview.wait()
    
    if timedout or not userview.values:
        await interaction.edit("Cancelled!", view=None)
        return
    
    user = userview.values[0]
    
    if str(user.id) not in session["users"]:
        await interaction.edit("That user is not in this session!")
        return
    
    thread = interaction.guild.get_thread(int(session["thread_id"]))
    await thread.send(f"{user.mention} has been removed from the session!")
        
    User.delete(str(user.id))
    
    await thread.remove_user(user)

    session["users"].remove(str(user.id))
    session.save()

    await interaction.edit(f"Removed {user.mention} from the session!", view=None)


async def session_info(interaction: discord.Interaction):
    
    sessions = Session.find(Session.private == 0 or Session.started_by == interaction.user.id).all()
    
    if not sessions:
        await interaction.response.send_message("There are no public sessions available at the moment!", ephemeral=True)
        return
    
    list_of_sessions = list(map(lambda x: discord.SelectOption(
        label=f"{practice_subjects[x.subject]} ({x.subject}), {x.session_id}",
        value=x.session_id
    ), sessions))
    
    view = JoinSessionListView(list_of_sessions, interaction)
    interaction.message = await interaction.send("Select a session to see more information about!", view=view, ephemeral=True)
    
    timedout = await view.wait()
    if timedout or not view.values:
        await interaction.edit(content="Cancelled!", view=None)
        return
    
    session = Session.get(view.values[0])

    if not session:
        await interaction.edit("That session does not exist anymore!")
        return
    
    embed = discord.Embed(title=f"Session ID: {session.session_id}", color=discord.Color.random())
    embed.add_field(name="Subject", value=practice_subjects[session["subject"]])
    embed.add_field(name="Users", value=', '.join(list(map(lambda x: f"<@{x}>", session["users"]))))
    embed.add_field(name="Started by", value=f"<@{session['started_by']}>")
    embed.add_field(name="Topics", value='\n'.join(session["topics"]))
    embed.add_field(name="Limit", value=session["limit"])
    embed.add_field(name="Minimum year", value=session["minimum_year"])

    await interaction.edit(embed=embed, view=None)

async def join_session(interaction: discord.Interaction):
    user = await get_from_db(str(interaction.user.id), User)
    if user and user["playing"]:
        await interaction.response.send_message("You are already in a session! Please leave that session using `/practice leave`.", ephemeral=True)
        return
    
    sessions = Session.find(Session.private == 0).all()
    
    if not sessions:
        await interaction.response.send_message("There are no public sessions available at the moment!", ephemeral=True)
        return
    
    list_of_sessions = list(map(lambda x: discord.SelectOption(
        label=f"{practice_subjects[x.subject]} ({x.subject}), {x.session_id}",
        value=x.session_id
    ), sessions))
    
    view = JoinSessionListView(list_of_sessions, interaction)
    interaction.message = await interaction.send("Select a session to join!", view=view, ephemeral=True)
    
    timedout = await view.wait()
    if timedout or not view.values:
        await interaction.edit(content="Cancelled!", view=None)
        return
    
    session = Session.get(view.values[0])

    if not session:
        await interaction.edit("That session does not exist anymore!")
        return
    
    thread = interaction.guild.get_thread(int(session["thread_id"]))
    await thread.add_user(interaction.user)

    user = User(
        user_id=str(interaction.user.id),
        playing=True,
        session_id=str(session.session_id),
        subject=session["subject"],
    )
    user.save()

    session["users"].append(str(interaction.user.id))
    session.save()

    await interaction.edit(f"Joined the session, {thread.mention}!", view=None)


options = {
    "New Session": new_session,
    "Leave Session": leave_session,
    "End Session": end_session,
    "List Sessions": list_sessions,
    "Join Session": join_session,
    "Pause Session": pause_session,
    "Resume Session": resume_session,
    "Add to Session": add_to_session,
    "Remove from Session": remove_from_session,
    "Session Info": session_info
}

@bot.slash_command(name="practice", description="Choose a subject and practice with your friends.")
async def practice(interaction: discord.Interaction,
                   action: str = discord.SlashOption(name="action", description="Action to perform", required=True, choices=list(options.keys()))):
    await options[action](interaction)
    

# Index the schemas in RediSearch to allow search.
Migrator().run()