import datetime
import time
import typing
import pymongo
import requests
import nextcord as discord
import traceback
import ast
import json

from nextcord.ext import tasks, commands

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=".", intents=intents)
keywords = {}