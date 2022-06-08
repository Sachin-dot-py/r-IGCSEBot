# r/IGCSE Bot

r/IGCSE Bot is a bot made primarly for the r/IGCSE Discord server. This bot provides a rep system & leaderboard, server suggestions voting, keyword auto-replies, moderation actions automatically updating your #modlog channel, reaction roles, and more!

# Installation
1. Make sure you have Python 3.7+ installed and install the dependencies in `requirements.txt` using `pip`.
2. Generate a Discord Bot API Token and make a MongoDB account and add a database named `IGCSEBot`.
3. Create a `.env` file and add your Discord bot token and MongoDB access url in the below format to it. 
```
IGCSEBOT_TOKEN="ABCDEFGHIJKLMNOP123"
MONGO_LINK="mongodb+srv://Username:Password@abcdefg.net"
```
3. Install the Heroku CLI and run the code using the command `heroku local`.
