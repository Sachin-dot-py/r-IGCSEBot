# r/IGCSE Bot

r/IGCSE Bot is a Python Discord Bot primarly developed for the [r/IGCSE Discord Community](https://discord.gg/igcse) but also used by 100+ other servers. This bot provides a rep system & leaderboard, server suggestions voting, keyword auto-replies, moderation actions automatically updating your logging channel, reaction roles, and more!

The `v1.0` version of this bot rolled into use on July 5, 2021 and has come a long way since. The bot is currently hosted on the Heroku cloud platform.

[Add r/IGCSE Bot to your Discord Server](https://discord.com/api/oauth2/authorize?client_id=861445044790886467&permissions=8&scope=bot).

# Preview of Features

- Rep System (Leaderboard displaying the top Helpers in the community)
<img alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/09a27ee5-4cc3-41b5-8f0e-999f5edfa238" width="60%">

- Past Paper Keyword Search (Allows members to perform keyword searches to retrieve IGCSE Past Papers)
<img width="60%" alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/c9267594-d4ec-4bc6-acb4-050d5271a19e">

- Provide Convenient Access to Granting Server Roles (e.g. Subject Roles)
<img width="60%" alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/ee932b39-988a-4c11-8f6f-3288f433c425">

- Moderation System (Enables moderators to warn/timeout/kick/ban users not abiding by the rules)
<img alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/42f49852-565c-4ad5-8044-bd713ddb5720" width=60%>

- Suggestion System (Allow members to vote on and suggest new ideas for the community)
<img alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/e604eb40-f007-4554-a510-8f6c5691bb4c" width="60%">

- Easy Creation of Simple & Complex Polls
<img width="60%" alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/3d2e62b4-a129-4a72-9719-9545ff96e8da">

- Anti-Spam System (Automatically detect spam links and timeout the sender)
<img alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/1c1ff9f0-2ce4-4703-ad78-35c8f5be00f5" width="60%">

- Helper Ping System (Automatically notifying Subject Helpers of unanswered questions after 15 minutes)
<img alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/ca5af6f6-929d-4861-9bca-aa954a023964" width=60%>

- Create Informational Embeds to assist Server Moderators
<img width="60%" alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/d37b53e3-3de3-4b10-8eb5-25681c4341b4">

- Provide Convenient Direct Access to Available Resources
<img width="60%" alt="Image" src="https://github.com/Sachin-dot-py/r-IGCSEBot/assets/61686882/8a4a74d2-e183-4c3f-bbf8-acc3bc2827f5">

# Local Installation Guide 
1. Make sure you have Python 3.7+ installed and install the dependencies in `requirements.txt` using `pip`.
2. Generate a Discord Bot API Token from the Discord Developer Portal
3. Create a MongoDB account and add a new database named `IGCSEBot`.
4. Set the environment variables `IGCSEBOT_TOKEN` and `MONGO_LINK` as the Bot API Token and MongoDB Access Link respectively.
5. Run the bot using the command `python3 src/app.py`
