import operator

# Dev Id for bot eval fxn
devId = '486703741257383937'

# Bot prefixes
prefixes = ['QuizBot ', 'qb ', 'QB ', 'Qb ', 'q?', '?']

# Set the running Tournament to be None by default
runningTournament = None

def validCategory(category):
    for cat in category:
        if cat not in catList:
            return False
    return True

# JUST REMOVE THIS ITS USELESS
# Get a bunch of aliases for the different bot commands
helloWords = ['Hi', 'Howdy']
tournamentWords = ['Tourney', 'T', 'Game', 'G']
fullTournamentWords = tournamentWords+['tournament']
startWords = ['ST']+['Start_'+i for i in fullTournamentWords]
joinWords = ['JT']+['Join_'+i for i in fullTournamentWords]
endWords = ['ET']+['End_'+i for i in fullTournamentWords]
leaderWords = ['LB']
createWords = ['CT']

def getDifferentNames(commandList, command, special=None): 
    # Fix this, command isn't used when not special...
    if special:
        return commandList+[i.lower() for i in commandList]+[i.upper() for i in commandList if i.upper() not in \
            commandList]+[i+special for i in commandList]+[i.lower()+'!' for i in commandList]+[command.lower(), 
            command.upper(), command.upper()+special, command+special, command.lower()+special]
    else:
        return commandList+[i.lower() for i in commandList]+[i.upper() for i in commandList if i.upper() not in commandList]

# Format answers
def ansFormat(ans):
    answers, prompts, befores = [[]]*3
    if '[' in ans:
        answers.append(ans[:ans.find('[')-1])
    else:
        answers.append(ans[:ans.find('&lt;')-1])
    return [answers, prompts, befores]

# Load all the questions/answers for all the categories
questionList = ['literature','science','history','fineArts','religion','mythology','philosophy','socialScience','geography','currentEvents','trash']
for cat in range(len(questionList)):
    with open('..\\Questions\\Tossups\\'+questionList[cat]+'.json', encoding='utf8') as f:
        questionList[cat] = eval(''.join(f.readlines()))
literatureQuestions, scienceQuestions, historyQuestions, fineArtsQuestions, religionQuestions, mythologyQuestions, philosophyQuestions, socialScienceQuestion, geographyQuestions, currentEventsQuestions, trashQuestions = questionList

# To validate the category that is selected for the type of tournament
catList = {'lit':literatureQuestions, 'literature':literatureQuestions, 'sci':scienceQuestions, 'science':scienceQuestions, 'hist':historyQuestions, 'history':historyQuestions, 'fa':fineArtsQuestions, 'finearts':fineArtsQuestions, 'religion':religionQuestions, 'myth':mythologyQuestions, 'mythology':mythologyQuestions, 'philosophy':philosophyQuestions, 'socialscience':socialScienceQuestion, 'geo':geographyQuestions, 'geography':geographyQuestions, 'ce':currentEventsQuestions, 'currentevents':currentEventsQuestions, 'trash':trashQuestions}

# Stores all tossup data
tossUps = {}

# Create a team class to represent the teams that players can create
class Team:
    def __init__(self, name, player):
        self.name = name
        self.players = []
        self.join_team(player)
    
    def join_team(self, player):
        self.players.append(player)
        player.in_team = True
        player.team = self
    
    def leave_team(self, player):
        del self.players[self.players.index(player)]

    def show_scores(self):
        compositeScore = 'Members of ' + self.name + ':\n'
        compositeScore = ''.join([player.show_score() for player in self.players])
        return compositeScore[:-1]
    
    @property
    def score(self):
        return sum([i.score for i in self.players])

# Create a player class to handle a players actions
class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.negs = 0
        self.in_team = False
        self.team = None
    
    def add_score(self, score):
        if score < 0:
            self.negs += 1
        self.score += score
    
    def leave_team(self, tournament):
        team = self.team
        self.in_team, self.team = False, None
        if len(team.players) == 1:
            tournament.remove_team(team.name)
            return 'You left the team ' + team.name + ', and the team was disbanded since you were the only one in it'
        else:
            team.leave_team(self)
            return 'You left the team ' + team.name
    
    def show_score(self):
        return 'Player Score:\n' + 'Name: ' + self.name + '\t Score:' + str(self.score) + '\t Negs:' + str(self.negs) + '\n'

# Creates a tournament class to handle interactions that a tournament has    
class Tournament:
    def __init__(self, types):
        self.type = types
        self.questions = []
        self.generate_questions()
        self.players = []
        self.teams = []
        self.top_teams = []
        self.top_players = []
        self.total_questions = 0
        self.score = 0
    
    def generate_questions(self):
        self.questions.append('')
    
    def add_player(self, player):
        self.players.append(player)
    
    def add_team(self, team):
        self.teams.append(team)
    
    def available_team(self, name):
        for team in self.teams:
            if team.name == name:
                return False
        return True

    def remove_team(self, name):
        for teamPos in range(len(self.teams)):
            if self.teams[teamPos].name == name:
                del self.teams[teamPos]

    def show_pos(self, player):
        self.refresh_leaderboards()
        if player.in_team:
            return 'Player Name: ' + player.name + '\nPlayer position: ' + str(self.top_players.index(player)+1) + '\nPlayer score: ' + str(player.score) + '\nPlayer negs: ' + str(player.negs) +\
                '\nPlayer\'s team position: ' + str(self.top_teams.index(player.team)+1)
        else:
            return 'Player Name: ' + player.name + '\nPlayer position: '+str(self.top_players.index(player)+1) + '\nPlayer score: ' + str(player.score) + '\nPlayer negs: ' + str(player.negs)
    
    def show_teamPos(self, team):
        self.refresh_leaderboards()
        for teamPos in range(len(self.top_teams)):
            if self.top_teams[teamPos].name == team:
                return 'Team Name: ' + self.top_teams[teamPos].name + '\nTeam position: '+str(teamPos+1) + '\nTeam score: ' + str(self.top_teams[teamPos].score)+\
                    '\nTeam players: ' + ''.join([player.name + ', ' for player in self.top_teams[teamPos].players])[:-2]

    def refresh_leaderboards(self):
        self.top_players = sorted(self.players, key=lambda player: player.score)
        self.top_teams = sorted(self.teams, key=lambda team: team.score)
     
    def create_team(self, name, player):
        if player.in_team:
            return 'You are already in a team, please leave the team first' 
    
    def rtn_player(self, name):
        for player in self.players:
            if player.name == name:
                return player

    @property    
    def leaderboard(self):
        self.refresh_leaderboards()
        leaderboard = 'Top Players:\n'
        playerCount, teamCount = len(self.players) if len(self.top_players) <= 5 else 5, len(self.top_teams) if len(self.top_teams) <= 5 else 5
        for playerPos in range(playerCount):
            leaderboard += '('+str(playerPos+1)+')'+self.top_players[playerPos].name+'\n'
        leaderboard += '\nTop Teams:\n'
        for teamPos in range(teamCount):
            leaderboard += '('+str(teamPos+1)+')'+self.top_teams[teamPos].name+'\n'    
        return leaderboard[:-1]
    
    @property
    def final_leaderboard(self):
        self.refresh_leaderboards()
        leaderboard = '\\*'*10 + '\nTHE GAME HAS ENDED\n' + '\\*'*10 + '\n\nThere were a total of ' + str(self.total_questions) + ' questions read'\
            '\nWith a total of ' + str(self.score) + ' points gained\n\nPlayers('+str(len(self.players)) + '):\n'
        for playerPos in range(len(self.players)):
            leaderboard += '('+str(playerPos+1) + ') ' + self.players[playerPos].name + '\tPoints: ' + str(self.players[playerPos].score)
            leaderboard += '\n' if not self.players[playerPos].in_team else '\t Team: ' + self.players[playerPos].team.name + '\n'
        leaderboard += '\nTeams('+str(len(self.teams)) + '):\n'
        for teamPos in range(len(self.teams)):
            leaderboard += '('+str(teamPos+1) + ') ' + self.teams[teamPos].name + '\tPoints: ' + str(self.teams[teamPos].score) + '\n'
        return leaderboard[:-1]