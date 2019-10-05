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

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.negs = 0
        self.in_team = False
        self.team = None
    
    def add_score(self, pts):
        if pts < 0:
            self.negs += 1
        self.score += pts
    
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
        self.pts = 0
    
    def generate_questions(self):
        self.questions.append('')
    
    def add_player(self, player):
        self.players.append(player)
    
    def add_team(self, team):
        for player in team.players:
            self.add_player(player)
        self.teams.append(self.teams)

    def show_pos(self, player):
        self.refresh_leaderboards()
        return 'Player Name:'+player.name+'\nYour position is: '+str(self.top_players.index(player)+1) + '\n Your team position is: ' + str(self.top_teams.index(player.team)+1) if player.in_team else 'Your position is: ' + str(self.top_players.index(player)+1)

    def refresh_leaderboards(self):
        for player in self.players:
            self.top_players = player.score.sort()
        for team in self.teams:
            self.top_teams = team.score.sort()
     
    #def create_team(self, name, player):

    @property    
    def leaderboard(self):
        self.refresh_leaderboards()
        leaderboard = 'Top Players:\n'
        playerCount, teamCount = len(self.players) if self.players <= 5 else 5, len(self.teams) if self.teams <= 5 else 5
        for playerPos in range(playerCount-1):
            leaderboard += '('+str(playerPos+1)+')'+self.players[playerPos].name+'\n'
        leaderboard += '\nTop Teams:\n'
        for teamPos in range(teamCount-1):
            leaderboard += '('+str(teamPos+1)+')'+self.teams[teamPos].name+'\n'    
        return leaderboard[:-1]
    
    @property
    def final_leaderboard(self):
        self.refresh_leaderboards()
        leaderboard = '*'*50+'\nTHE GAME HAS ENDED\n'+'*'*50+'\n\nThere were a total of '+self.total_questions+'\nWith a total of '+self.pts+'gained\n\nPlayers('+str(len(self.players))+'):\n'
        for playerPos in range(self.players):
            leaderboard += '('+str(playerPos+1)+') '+self.players[playerPos].name + '\n'
        leaderboard += 'Teams('+str(len(self.teams))+'):\n'
        for teamPos in range(self.teams):
            leaderboard += '('+str(teamPos+1)+') '+self.teams[teamPos].name + '\n'
        return leaderboard[:-1]
        

        




