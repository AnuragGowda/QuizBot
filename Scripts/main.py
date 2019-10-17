# Import Files
import os
import random
from discord.ext.commands import Bot
from dotenv import load_dotenv
from setup import *

# Load token from .env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up the bot
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
            for team in runningTournament.teams:
                if team.name == ctx.message.content[ctx.message.content.rfind('-')+1:]:
                    return await ctx.send('There is already a team with that name!') 
            runningTournament.add_team(Team(ctx.message.content[ctx.message.content.rfind('-')+1:], runningTournament.rtn_player(str(ctx.message.author))))
            await ctx.send('Creating a team with the name of: '+ctx.message.content[ctx.message.content.rfind('-')+1:])
        else:
            await ctx.send('Please specify a name by typing -team name after the Create_Team call')

@bot.command(name='Join_Team', help='Joins a tournament team', aliases = ['join', 'j'])
async def join(ctx):
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        if ctx.message.content.rfind('-') != -1:
            for team in runningTournament.teams:
                if team.name == ctx.message.content[ctx.message.content.rfind('-')+1:]:

                    await ctx.send('You have joined the team '+ctx.message.content[ctx.message.content.rfind('-')+1:])
            return await ctx.send('There is no existing team with the name '+ctx.message.content[ctx.message.content.rfind('-')+1:])
        else:
            await ctx.send('Please specify a name by typing -team name after the Join_Team call')

@bot.command(name='Leave_Team', help='Leaves a tournament team', aliases=['leave', 'l'])
async def leave(ctx):
    if not runningTournament: 
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        if runningTournament.rtn_player(str(ctx.message.author)).in_team == False:
            await ctx.send('You aren\'t in a team!')
        else:
            await ctx.send(runningTournament.rtn_player(str(ctx.message.author)).leave_team(runningTournament))

@bot.command(name='Get_Pos', help='Gets a player or team position in a tournament', aliases=['gp'])
async def myPos(ctx):
    global runningTournament
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        if ctx.message.content.rfind('-') != -1:
            pass
        else:
            await ctx.send('Please specify a name by typing -team,team_name or -player,player_name after the Get_Pos call')
    
@bot.command(name='SUPER_HELP', help='You should run this command if you need help!', aliases=['h'])
async def hlp(ctx):
    helpString = \
        '\\\t\\\t**Commands and Usage for QuizBot**\n\n'+\
        '**Command-Prefix**: *(This is not an actual command)* To \"call\" the bot, either use QuizBot, qb or QB, each followed by a space character. This is used BEFORE EVERY COMMAND that is listed below\n\n\n'+\
        'For the following commands, to get the full alias (which is an alternate way to use the command, for example, instead of typing qb Hello, you may type qb hi!) list (and a brief description), type the Command-Prefix (QuizBot, qb, QB) followed by help and then a space and the command/keyword (ex. qb help Hello) you want the list for\n\n'+\
        'ADMIN and CREATOR commands: ADMIN commands are only useable for those who have the discord role \'ADMIN\' in a server that has the bot. CREATOR command is meant for the person who set up the bot.\n\n\n'+\
        '**Hello**: Says hello, or a version of hello (Howdy, Sup, Hi) to the person who invoked the call in the format: *Command-Prefix* Hello *username with 4 digits*\n\n'+\
        '**Start_Tournament**: *(This is an ADMIN command)* Starts a tournament, as the name implies, the format of this command is *Command-Prefix* Start_Tournament -**category** where category is a QuizBowl category. The supported categories for this bot are <<INPUT THE SUPPORTED CATEGORIES HERE (TODO)>>. A tournament is something that allows players to join, form teams and compete against each other, allowing them to also be able to veiw a leaderbaord and thier position in the overall tournament. There can only be ONE tournament per channel that the bot is in.\n\n'+\
        '**Join_Tournament**: This allows any user to join the tournament in progress, if a tournament is in progress, the format is *Command-Prefix* Join_Tournament\n\n'+\
        '**End_Tournament**: *(This is an ADMIN command)* This ends the tournament that is currently in progress, if one was in progress and displays the final leaderboard for that tournament.\n\n'+\
        '**Leaderbaord**: This allows any user to display the current tournament standings, if a tournament is running, the format is *Command-Prefix* Leaderboard\n\n'+\
        '**Create_Team**: This allows a player who is part of a tournament to create a tournament, the format of this command is *Command-Prefix* Create_Team -**team name** where the team name is a name of the creatros choice. However, the team name cannot be the same as a team that is already in the tournament\n\n'+\
        '**Leave_Team**: This allows the player to leave the team that they are in, if they are in a team, moreover, if they are the last player in the team, the team will be disbanded (removed from the tournament entirely), the format for this command is: *Command-Prefix* Leave_Team \n\n'+\
        '**Get_Pos**: This allows any member in a server to get the position/rank of a player or team in a tournament, if that player/team exists. The format of this command is *Command-Prefix* Get_Pos -player(<- this can also be p),**player_name** to find the rank of a player, and *Command-Prefix* Get_Pos -team(<- this can also be t),**team name** to find the rank of a team\n\n'+\
        '**Tossup**: TODO\n\n'+\
        '**EVAL**: *(This is a CREATOR command)* This command is primarily for the creator/or person who set the bot up to debug/test if the bot is working correctly. The format is *Command-Prefix* EVAL -**something to evaluate**\n\n'+\
        '\nOVERALL TODO: Tossups, generate questions, +- points after answering a question in a tournament, buzzing, display questions, there may be some bugs too?\'\'\''
    await ctx.send(helpString[:2000])
    await ctx.send(helpString[2000:])

@bot.command(name='EVAL', help='For bot tests (CREATOR ONLY)', aliases=['e'])
async def evaluate(ctx):
    if str(ctx.message.author.id) == '486703741257383937':
        await ctx.send(eval(ctx.message.content[ctx.message.content.find('-')+1:]))
    else:
        await ctx.send('You aren\'t the creator!')

@bot.event
async def on_ready():
    print(bot.user.name + ' has connected to Discord!')

# Run the bot
bot.run(token)