import os
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=['QuizBot ', 'qb ', 'QB '])

hellowords = ['Hi', 'Howdy']

@bot.command(name='Hello', help='Says hello to the invoker', aliases=hellowords+[i.lower() for i in hellowords]+[i+'!' for i in hellowords]+[i.lower()+'!' for i in hellowords]+['hello', 'Hello!', 'hello!'])
async def hello(ctx):
    starter = ['Hello, ', 'Hi there, ', 'Howdy ', 'Hey ', 'Sup ']
    await ctx.send(random.choice(starter)+str(ctx.message.author)[:str(ctx.message.author).rfind('#')]+'!')


@bot.event
async def on_ready():
    print(bot.user.name + ' has connected to Discord!')

bot.run(token)