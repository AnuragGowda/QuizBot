import operator
runningTournament = None

catList = ['lit', 'literature', 'math', 'science', 'etc.']
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

def validCategory(category):
    for cat in category:
        if cat not in catList:
            return False
    return True


class Team:
    def __init__(self, name, player):
        self.name = name
        self.players = [player]
        player.in_team = True
        player.team = self
    
    def join_team(self, player):
        self.players.append(player)
    
    def leave_team(self, player):
        del self.players[self.players.index(player)]

    def show_scores(self):
        compositeScore = 'Members of '+self.name+':\n'
        for player in self.players:
            compositeScore += 'Name: ' + player.name + '\t Score:' + player.score + '\t Negs:' + player.negs + '\n'
        return compositeScore[:-1]
    
    @property
    def score(self):
        return sum([i.score for i in self.players])

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
        print(player)
    
    def add_team(self, team):
        for player in team.players:
            self.add_player(player)
        self.teams.append(self.teams)

    def show_pos(self, player):
        self.refresh_leaderboards()
        return 'Player Name:'+player.name+'\nYour position is: '+str(self.top_players.index(player)+1) + '\n Your team position is: ' + \
            str(self.top_teams.index(player.team)+1) if player.in_team else 'Your position is: ' + str(self.top_players.index(player)+1)

    def refresh_leaderboards(self):
        self.top_players = sorted(self.players, key=operator.attrgetter('score'))
        self.top_teams = sorted(self.teams, key=operator.attrgetter('score'))
     
    def create_team(self, name, player):
        if player.in_team:
            return "You are already in a team, please leave the team first" 
    
    def rtn_player(self, name):
        print(len(self.players))
        for player in self.players:
            if player.name == name:
                return player

    @property    
    def leaderboard(self):
        self.refresh_leaderboards()
        leaderboard = 'Top Players:\n'
        playerCount, teamCount = len(self.players) if len(self.players) <= 5 else 5, len(self.teams) if len(self.teams) <= 5 else 5
        for playerPos in range(playerCount):
            leaderboard += '('+str(playerPos+1)+')'+self.players[playerPos].name+'\n'
        leaderboard += '\nTop Teams:\n'
        for teamPos in range(teamCount):
            leaderboard += '('+str(teamPos+1)+')'+self.teams[teamPos].name+'\n'    
        return leaderboard[:-1]
    
    @property
    def final_leaderboard(self):
        self.refresh_leaderboards()
        leaderboard = '*'*10+'\nTHE GAME HAS ENDED\n'+'*'*10+'\n\nThere were a total of '+str(self.total_questions)+' questions read'\
            '\nWith a total of '+str(self.score)+' points gained\n\nPlayers('+str(len(self.players))+'):\n\n'
        for playerPos in range(len(self.players)):
            leaderboard += '('+str(playerPos+1)+') '+self.players[playerPos].name + '\tPoints: ' + str(self.players[playerPos].score) + '\n'
        leaderboard += 'Teams('+str(len(self.teams))+'):\n'
        for teamPos in range(len(self.teams)):
            leaderboard += '('+str(teamPos+1)+') '+self.teams[teamPos].name + '\tPoints: ' + str(self.players[playerPos].score) + '\n'
        return leaderboard[:-1]
        

        




