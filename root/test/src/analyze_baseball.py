import json

def filterByNTeams(games, opps):
    gamesByOpponent = []
    for opp in opps:
        gamesPlayedAgainstOpp = []
        for game in games:
            #if teamOF and opp are playin each other
            if((opp == game["home"]["name"] or opp == game["away"]["name"]) and (game["input"]["focus_team"] == game["home"]["name"] or game["input"]["focus_team"] == game["away"]["name"])):
                gamesPlayedAgainstOpp.append(game)
        gamesByOpponent.append(gamesPlayedAgainstOpp)
    return gamesByOpponent

def applyInputs(input, games):
    gamesList = []
    for game in games.split("\n"):
        gameArr = game.split(",")
        if(len(gameArr) > 11):
            t0 = { "name" : gameArr[6], "score" : gameArr[10], "numHomeruns" : gameArr[25] , "winner" : 0}
            t1 = { "name": gameArr[3], "score": gameArr[9], "numHomeruns" : gameArr[53] , "winner" : 0}
            gamesList.append({"input": input,"home" : t0, "away" : t1})
    return gamesList

def getWinner(game):
     if(int(game["away"]["score"]) < int(game["home"]["score"])):
         return game["home"]["name"]
     else:
         return game["away"]["name"]
     
def getGameResults(gamesByOpp):
    gameResults = []
    for games in gamesByOpp:
        for game in games:
            winner = getWinner(game)
            if(winner == game["input"]["focus_team"]):
                winnerName = game["input"]["focus_team"]
            for oppName in game["input"]["oppNames"]:
                if(winner == oppName):
                    winnerName = oppName
            gameResults.append({"home": game["home"]["name"], "away": game["away"]["name"], "winner": winnerName, "score" : game["home"]["score"] + "-" + game["away"]["score"]})
    return gameResults

def getFocusWinResults(gameResults, focusName, oppName):
    focusTeamWonGames = []
    for result in gameResults:
        winner = result["winner"]
        if(winner == focusName and (result["home"] == oppName or result["away"] == oppName)):
            focusTeamWonGames.append(result)
    return focusTeamWonGames

def getOppWinResults(gameResults, oppName):
    oppWonGames = []
    for result in gameResults:
        winner = result["winner"]
        if(winner == oppName):
            oppWonGames.append(result)
    return oppWonGames

def getSeasonResults(input, gameResults):
    seasonResults = []
    for oppName in input["oppNames"]:
        focusResults = getFocusWinResults(gameResults, input["focus_team"], oppName)
        oppResults = getOppWinResults(gameResults, oppName)
        numGamesWonByFocus = len(focusResults)
        numGamesWonByOpp = len(oppResults)
        if(focusResults and numGamesWonByFocus > 0):
            winPercentage = numGamesWonByFocus/(numGamesWonByFocus+numGamesWonByOpp)
            seasonResults.append({"focus_name" :  input["focus_team"], "opp_name" : oppName, "win_percentage" : winPercentage, "focus_games_won" : numGamesWonByFocus})
        # if(oppResults and numGamesWonByOpp > 0):
        #     winPercentage = numGamesWonByOpp/(numGamesWonByFocus+numGamesWonByOpp)    
        #     seasonResults.append({"opp_name" : oppName, "focus_name" :  input["focus_team"], "win_percentage" : winPercentage, "opp_games_won" : numGamesWonByOpp})
    return seasonResults

def manyOpponentSeasonResult(games, input):
    gamesWithInputs = applyInputs(input, games)
    byTeamGames = filterByNTeams(gamesWithInputs, input["oppNames"])
    return getSeasonResults(input, getGameResults(byTeamGames))

# Field(s)  Meaning
#     1     Date in the form "yyyymmdd"
#     2     Number of game:
#              "0" -- a single game
#              "1" -- the first game of a double (or triple) header
#                     including seperate admission doubleheaders
#              "2" -- the second game of a double (or triple) header
#                     including seperate admission doubleheaders
#              "3" -- the third game of a triple-header
#              "A" -- the first game of a double-header involving 3 teams
#              "B" -- the second game of a double-header involving 3 teams
#     3     Day of week  ("Sun","Mon","Tue","Wed","Thu","Fri","Sat")
#   4-5     Visiting team and league
#     6     Visiting team game number
#           For this and the home team game number, ties are counted as
#           games and suspended games are counted from the starting
#           rather than the ending date.
#   7-8     Home team and league
#     9     Home team game number
# 10-11     Visiting and home team score (unquoted)
#    12     Length of game in outs (unquoted).  A full 9-inning game would
#           have a 54 in this field.  If the home team won without batting
#           in the bottom of the ninth, this field would contain a 51.
#    13     Day/night indicator ("D" or "N")
#    14     Completion information.  If the game was completed at a
#           later date (either due to a suspension or an upheld protest)
#           this field will include:
#              "yyyymmdd,park,vs,hs,len" Where
#           yyyymmdd -- the date the game was completed
#           park -- the park ID where the game was completed
#           vs -- the visitor score at the time of interruption
#           hs -- the home score at the time of interruption
#           len -- the length of the game in outs at time of interruption
#           All the rest of the information in the record refers to the
#           entire game.
#    15     Forfeit information:
#              "V" -- the game was forfeited to the visiting team
#              "H" -- the game was forfeited to the home team
#              "T" -- the game was ruled a no-decision
#    16     Protest information:
#              "P" -- the game was protested by an unidentified team
#              "V" -- a disallowed protest was made by the visiting team
#              "H" -- a disallowed protest was made by the home team
#              "X" -- an upheld protest was made by the visiting team
#              "Y" -- an upheld protest was made by the home team
#           Note: two of these last four codes can appear in the field
#           (if both teams protested the game).
#    17     Park ID
#    18     Attendance (unquoted)
#    19     Time of game in minutes (unquoted)
# 20-21     Visiting and home line scores.  For example:
#              "010000(10)0x"
#           Would indicate a game where the home team scored a run in
#           the second inning, ten in the seventh and didn't bat in the
#           bottom of the ninth.
# 22-38     Visiting team offensive statistics (unquoted) (in order):
#              at-bats
#              hits
#              doubles
#              triples
#              homeruns
#              RBI
#              sacrifice hits.  This may include sacrifice flies for years
#                 prior to 1954 when sacrifice flies were allowed.
#              sacrifice flies (since 1954)
#              hit-by-pitch
#              walks
#              intentional walks
#              strikeouts
#              stolen bases
#              caught stealing
#              grounded into double plays
#              awarded first on catcher's interference
#              left on base
# 39-43     Visiting team pitching statistics (unquoted)(in order):
#              pitchers used ( 1 means it was a complete game )
#              individual earned runs
#              team earned runs
#              wild pitches
#              balks
# 44-49     Visiting team defensive statistics (unquoted) (in order):
#              putouts.  Note: prior to 1931, this may not equal 3 times
#                 the number of innings pitched.  Prior to that, no
#                 putout was awarded when a runner was declared out for
#                 being hit by a batted ball.
#              assists
#              errors
#              passed balls
#              double plays
#              triple plays
# 50-66     Home team offensive statistics
# 67-71     Home team pitching statistics
# 72-77     Home team defensive statistics
# 78-79     Home plate umpire ID and name
# 80-81     1B umpire ID and name
# 82-83     2B umpire ID and name
# 84-85     3B umpire ID and name
# 86-87     LF umpire ID and name
# 88-89     RF umpire ID and name
#           If any umpire positions were not filled for a particular game
#           the fields will be "","(none)".
# 90-91     Visiting team manager ID and name
# 92-93     Home team manager ID and name
# 94-95     Winning pitcher ID and name
# 96-97     Losing pitcher ID and name
# 98-99     Saving pitcher ID and name--"","(none)" if none awarded
# 100-101   Game Winning RBI batter ID and name--"","(none)" if none
#           awarded
# 102-103   Visiting starting pitcher ID and name
# 104-105   Home starting pitcher ID and name
# 106-132   Visiting starting players ID, name and defensive position,
#           listed in the order (1-9) they appeared in the batting order.
# 133-159   Home starting players ID, name and defensive position
#           listed in the order (1-9) they appeared in the batting order.
#   160     Additional information.  This is a grab-bag of informational
#           items that might not warrant a field on their own.  The field 
#           is alpha-numeric. Some items are represented by tokens such as:
#              "HTBF" -- home team batted first.
#              Note: if "HTBF" is specified it would be possible to see
#              something like "01002000x" in the visitor's line score.
#           Changes in umpire positions during a game will also appear in 
#           this field.  These will be in the form:
#              umpchange,inning,umpPosition,umpid with the latter three
#              repeated for each umpire.
#           These changes occur with umpire injuries, late arrival of 
#           umpires or changes from completion of suspended games. Details
#           of suspended games are in field 14.
#   161     Acquisition information:
#              "Y" -- we have the complete game
#              "N" -- we don't have any portion of the game
#              "D" -- the game was derived from box score and game story
#              "P" -- we have some portion of the game.  We may be missing
#                     innings at the beginning, middle and end of the game.
 
# Missing fields will be NULL.