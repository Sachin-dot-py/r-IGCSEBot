import datetime
import time
import typing
import pymongo
import requests
import nextcord as discord
import traceback
import ast
import json
import random
import pyshorteners
import ast
import pyjokes

from nextcord.ext import tasks, commands
from constants import GUILD_ID

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=",", intents=intents)
guild = bot.get_guild(GUILD_ID)
keywords = {}