# Import Files
import os
import random
import random
import asyncio
import textwrap
from discord.ext.commands import Bot
from dotenv import load_dotenv
from setup import *

# Load token from .env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Set up the bot
bot = Bot(command_prefix=prefixes)

@bot.command(name='Hello', help='Says hello to the invoker', aliases=getDifferentNames(helloWords, 'Hello', '!'))
async def hello(ctx):
    starter = ['Hello, ', 'Hi there, ', 'Howdy ', 'Hey ', 'Sup ']
    await ctx.send(random.choice(starter)+ctx.message.author.name+'!')

'''
Ignore this I explain in comments later on anyway

What tossUps must hold:
Since we want each channel to be able to have their own tossup running at a time, we create a dict that has keys which are 
the id's of the channels (which are unique throught all of discord). Each of these keys point to a list which eventually 
will contain a couple of values that are useful:
**  I changed this to be a dict as it's simply easier to store the data that way then to rememebr what data is at what index,
but the data is the same, the indices are the keys reading, question, fullquestion, fullanswer (the third index is split up)
currentBuzzer, and buzzList respectively **
The first is if there is currently a tossup running/being read. This is stored as a boolean, and while true, it means that there
is a tossup, and nobody has buzzed yet, or previous buzzes have been wrong, and therefore the current question must continue
being read. If false, the tossup isn't currently being read, which means that either someone has buzzed, or a tossup simply
hasn't been requested.
The second holds a direct reference to the message object in which we orignially sent question so that we can edit it later,
which can be used to create the appearance of it being read, add buzz emojis where people have buzzed, and to reveal the 
whole question once the time runs out or when somebody gets the answer right
The third is actually a dictionary which contains the full question and answer so that we can check if the answer is right later,
and also to read and complete the question which is stored in index 1 (the second value)
The fourth is the id of the person that has buzzed so that we can check that the person who answers later is the same person who
buzzed.
The fifth is a timeout boolean, which checks to see if the user actually answered the question after buzzing, if they didn't
we need to send a time's up message.
The sixth is a list of people who have already buzzed, as they can't buzz again.
'''

@bot.command(name='Tossup', help='Starts a tossup question', aliases=['t'])
async def toss(ctx):
    # If specified category
    if ctx.message.content.find('-') != -1:
        # Check if cat is valid
        if validCategory([ctx.message.content[ctx.message.content.find('-')+1:]]):

            # Set reading to true, get the answer (we get the question later) and create a counter (which will help us add on to the question later)
            # also create a buzzList which will keep track of who has buzzed
            tossUps[ctx.message.channel.id] = {'reading':True}
            cat, tossUps[ctx.message.channel.id]['counter'] = random.choice(catList[ctx.message.content[ctx.message.content.find('-')+1:]]), 1
            tossUps[ctx.message.channel.id]['fullanswer'] = cat['answer']
            tossUps[ctx.message.channel.id]['buzzList'] = []

            # Create "bits" to the question which we can then add on later - I thought that this would be the simplest method and best for readablity
            tossUps[ctx.message.channel.id]['fullquestion'] = textwrap.wrap(cat['question'], len(cat['question'])/15)
            
            # Send the beginning of the question
            question = await ctx.send(tossUps[ctx.message.channel.id]['fullquestion'][0])

            # Store question object (what is displayed in discord - the question message that is send) so we can edit it later
            tossUps[ctx.message.channel.id]['question'] = question

            # We only want to read the function if someone hasn't buzzed, or if they have and have answered incorrectly
            while tossUps[ctx.message.channel.id]['reading']:

                # Increment counter
                tossUps[ctx.message.channel.id]['counter'] += 1

                # If the counter is larger than the number of indicies we have, it means we have finished reading, so we have to stop
                if tossUps[ctx.message.channel.id]['counter'] >= len(tossUps[ctx.message.channel.id]['fullquestion']):
                    tossUps[ctx.message.channel.id]['reading'] = False

                # Otherwise, we keep reading
                else:

                    # Add on to the question
                    await question.edit(content=tossUps[ctx.message.channel.id]['question'].content+' '+tossUps[ctx.message.channel.id]['fullquestion'][tossUps[ctx.message.channel.id]['counter']])

                    # Use a special version of sleep so we can create the effect of being read
                    await asyncio.sleep(1)

            # Give 2 seconds before the timeout
            await asyncio.sleep(2)

            # The reading now ends with either a correct buzz or a timeout, but we don't want to timeout while someone has buzzed
            # Therefore we create a loop to constantly check to see if there is a buzzer or if there was a correct buzz, as soon as 
            # the buzzer has finished (if there is a buzzer) we have the reading timeout, similarly, the reading ends if the buzzer
            # we are waiting on gets a correct buzz
            while True:
                
                # Check to see if someone is answering
                if not 'currentBuzzer' in tossUps[ctx.message.channel.id] or not tossUps[ctx.message.channel.id]['currentBuzzer']:
                    
                    # We need to finish the question and give a times up and the answer
                    # Get rid of the ugly stuff at the end cause nobody cares where the question came from
                    if '&lt;' not in tossUps[ctx.message.channel.id]['fullanswer']:
                        return await ctx.send('**Time\'s up!** \nThe anwer was:\t'+tossUps[ctx.message.channel.id]['fullanswer'])
                    
                    # Otherwise 
                    return await ctx.send('**Time\'s up!** \nThe anwer was: '+tossUps[ctx.message.channel.id]['fullanswer'][:tossUps[ctx.message.channel.id]['fullanswer'].find('&lt;')-1])

                # If the answer was already guessed just exit as everything else is handled by other functions
                elif tossUps[ctx.message.channel.id]['answered']:
                    return

        # Invalid cat
        else:
            await ctx.send(ctx.message.content[ctx.message.content.find('-')+1:])
            await ctx.send('That is an invalid category')

    # No cat specified
    else:
        await ctx.send('Specify a category by typing -category_name after tossup call')

@bot.command(name='b')
async def buzz(ctx):
    if ctx.message.channel.id in tossUps and tossUps[ctx.message.channel.id]['reading']:
        tossUps[ctx.message.channel.id]['reading'] = False
        tossUps[ctx.message.channel.id]['currentBuzzer'] = ctx.message.author.id
        if 'buzzList' in tossUps[ctx.message.channel.id] and ctx.message.author.id in tossUps[ctx.message.channel.id]['buzzList']:
            return await ctx.send('You already buzzed!')
        elif 'buzzList' not in tossUps[ctx.message.channel.id]:
            tossUps[ctx.message.channel.id]['buzzList'] = [ctx.message.author.id]
        else: 
            tossUps[ctx.message.channel.id]['buzzList'].append(ctx.message.author.id)
        await tossUps[ctx.message.channel.id]['question'].edit(content=tossUps[ctx.message.channel.id]['question'].content+'🔔') 
        await ctx.send('Buzz by: <@'+str(ctx.message.author.id)+'>, 5 secs to answer!')
        # await tossUps[ctx.message.channel.id]['question'].edit(content=tossUps[ctx.message.channel.id]['question'].content+''.join([i for i in ['fullquestion'][tossUps[ctx.message.channel.id]['counter']:len(tossUps[ctx.message.channel.id]['fullquestion'])]))
    else:
        await ctx.send('Either you buzzed too late or there isn\'t a tossup going on right now')

@bot.command()
async def ans(ctx):
    if not ctx.message.channel.id in tossUps:
        await ctx.send('You have to start a tossup before answering')
    elif tossUps[ctx.message.channel.id]['currentBuzzer'] != ctx.message.author.id:
        await ctx.send('You have to buzz before answering!')
    else:

        # Fix this, there are prompts, and this inst acc at all

        if ctx.message.content in tossUps[ctx.message.channel.id]['fullanswer']:
            await ctx.send('That is correct!')
            await tossUps[ctx.message.channel.id]['question'].edit(content=tossUps[ctx.message.channel.id]['fullquestion'])
            await ctx.send('The anwer was (this needs to be formatted probably):\t'+tossUps[ctx.message.channel.id]['fullanswer'])
        else:
            await ctx.send('Incorrect!')
            await tossUps[ctx.message.channel.id]['question'].edit(content=tossUps[ctx.message.channel.id]['question'].content+'🔕') 
            # resume the reading idk how rn
            await resumeRead(ctx)

async def resumeRead(ctx):
    while tossUps[ctx.message.channel.id]['reading']:
        tossUps[ctx.message.channel.id]['counter'] += 1
        await tossUps[ctx.message.channel.id]['question'].edit(content=tossUps[ctx.message.channel.id]['fullquestion'][:int(len(tossUps[ctx.message.channel.id]['fullquestion'])*tossUps[ctx.message.channel.id]['counter']/15)])
        await asyncio.sleep(1)

@bot.command()
async def id(ctx):
    await ctx.send(ctx.message.author.id)

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
        if not runningTournament.rtn_player(str(ctx.message.author)):
            runningTournament.add_player(Player(str(ctx.message.author)))
            await ctx.send(str(ctx.message.author)+' has joined the tournament')
        else:
            await ctx.send('You are already in the tournament!')

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
    if not runningTournament: 
        await ctx.send('A tournament hasn\'t started yet!')
    elif not runningTournament.rtn_player(str(ctx.message.author)):
        await ctx.send('You need to join the tournament before trying to use this command!')
    else:
        if runningTournament.rtn_player(str(ctx.message.author)).in_team:
                return await ctx.send('You are already in a team! Leave the team before creating one!')
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
    elif not runningTournament.rtn_player(str(ctx.message.author)):
        await ctx.send('You need to join the tournament before trying to use this command!')
    else:
        if ctx.message.content.rfind('-') != -1:
            if runningTournament.rtn_player(str(ctx.message.author)).in_team:
                return await ctx.send('You are already in a team! Leave the team before joining another one!')
            for team in runningTournament.teams:
                if team.name == ctx.message.content[ctx.message.content.rfind('-')+1:]:
                        team.join_team(runningTournament.rtn_player(str(ctx.message.author)))
                        return await ctx.send('You have joined the team '+ctx.message.content[ctx.message.content.rfind('-')+1:])           
            return await ctx.send('There is no existing team with the name '+ctx.message.content[ctx.message.content.rfind('-')+1:])
        else:
            await ctx.send('Please specify a name by typing -team name after the Join_Team call')

@bot.command(name='Leave_Team', help='Leaves a tournament team', aliases=['leave', 'l'])
async def leave(ctx):
    if not runningTournament: 
        await ctx.send('A tournament hasn\'t started yet!')
    elif not runningTournament.rtn_player(str(ctx.message.author)):
        await ctx.send('You need to join the tournament before trying to use this command!')
    else:
        if not runningTournament.rtn_player(str(ctx.message.author)).in_team:
            await ctx.send('You aren\'t in a team!')
        else:
            await ctx.send(runningTournament.rtn_player(str(ctx.message.author)).leave_team(runningTournament))

@bot.command(name='Get_Pos', help='Gets a player or team position in a tournament', aliases=['gp'])
async def myPos(ctx):
    if not runningTournament:
        await ctx.send('A tournament hasn\'t started yet!')
    else:
        if ctx.message.content.find('-') != -1 or ctx.message.content.find('@') != -1:
            if ctx.message.content[ctx.message.content.find('-')+1:ctx.message.content.find('@')-1] not in ['team','player ']:
                await ctx.send('Please use the correct format of -team @team_name or -player @player_name after the Get_Pos call')
            else:
                if ctx.message.content[ctx.message.content.find('-')+1:ctx.message.content.find('@')-1] == 'team':
                    if ctx.message.content[ctx.message.content.find('@')+1:] not in [team.name for team in runningTournament.teams]:
                        await ctx.send('That team isn\'t in the tournament')
                    else:
                        await ctx.send(runningTournament.show_teamPos(ctx.message.content[ctx.message.content.find('@')+1:]))
                else:
                    if not runningTournament.rtn_player(str(ctx.guild.get_member(int(ctx.message.content[ctx.message.content.find('@')+2:-1])))):
                        await ctx.send('That player isn\'t in the tournament!')
                    else:
                        await ctx.send(runningTournament.show_pos(runningTournament.rtn_player(str(ctx.guild.get_member(int(ctx.message.content[ctx.message.content.find('@')+2:-1]))))))           
        else:
            await ctx.send('Please specify a name by typing -team @team_name or -player @player_name after the Get_Pos call')
    
@bot.command(name='SUPER_HELP', help='You should run this command if you need help!', aliases=['h'])
async def hlp(ctx):
    helpString = \
        '**Commands and Usage for QuizBot**\n\n'+\
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

@bot.command()
async def test(ctx):
    await ctx.edit(content="newcontent")

@bot.event
async def on_ready():
    print(bot.user.name + ' has connected to Discord!')

# Run the bot
bot.run(token)