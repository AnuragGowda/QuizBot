import os
import random
from discord.ext.commands import Bot
from dotenv import load_dotenv
from setup import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = Bot(command_prefix=['QuizBot ', 'qb ', 'QB '])

@bot.command(name='Hello', help='Says hello to the invoker', aliases=getDifferentNames(helloWords, 'Hello', '!'))
async def hello(ctx):
    starter = ['Hello, ', 'Hi there, ', 'Howdy ', 'Hey ', 'Sup ']
    await ctx.send(random.choice(starter)+ctx.message.author.name+'!')

@bot.command(name='Start_Tournament', help='Starts a tournament (ADMIN ONLY)', aliases=getDifferentNames(startWords, 'tournament'))
async def tournament(ctx):
    if not 'ADMIN' in [i.name for i in ctx.message.author.roles]:
        return await ctx.send('You aren\'t an admin!')
    global runningTournament
    if not runningTournament:
        if validCategory(ctx.message.content[ctx.message.content.rfind('-')+1:].split(' ')):
            runningTournament = Tournament(ctx.message.content[ctx.message.content.rfind('-')+1:].split(' '))
            msg = ctx.message.content[ctx.message.content.rfind('-')+1:].split(' ')
            if len(msg)>1:
                msg.insert(-1,'and')
                await ctx.send('Starting a tournament with the categories of: '+ ' '.join(msg))
            else:
                await ctx.send('Starting a tournament with the category of: '+ msg[0])
        else:
            await ctx.send('Please enter a valid category')
    else:
        await ctx.send('A tournament has already started')

@bot.command(name='Join_Tournament', help='Makes the user join a tournament', aliases=getDifferentNames(joinWords, 'join_tournament'))
async def joinTournament(ctx):
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        runningTournament.add_player(Player(str(ctx.message.author)))
        await ctx.send(str(ctx.message.author)+' has joined the tournament')

@bot.command(name='End_Tournament', help='Ends a tournament (ADMIN ONLY)', aliases=getDifferentNames(endWords, 'end_tournament'))
async def endTournament(ctx):
    if not 'ADMIN' in [i.name for i in ctx.message.author.roles]:
        return await ctx.send('You aren\'t an admin!')        
    global runningTournament
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        await ctx.send(runningTournament.final_leaderboard)
        runningTournament = None

@bot.command(name='Leaderboard', help='Displays tournament leaderboard', aliases=getDifferentNames(leaderWords, 'Leaderboard'))
async def leaderboard(ctx):
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        await ctx.send(runningTournament.leaderboard)

@bot.command(name='Create_Team', help='Creates a team for a tournament', aliases=getDifferentNames(createWords, 'create_team'))
async def create(ctx):
    global runningTournament
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        if ctx.message.content.rfind('-') != -1:
            runningTournament.add_team(Team(ctx.message.content[ctx.message.content.rfind('-')+1:].split(' '), runningTournament.rtn_player(ctx.message.author)))
            await ctx.send('Creating a team with the name of: '+ctx.message.content[ctx.message.content.rfind('-')+1:].split(' '))
        else:
            await ctx.send('Please specify a name by typing -team_name after the Create_Team call')
        


@bot.event
async def on_ready():
    print(bot.user.name + ' has connected to Discord!')

bot.run(token)