import ast

def change_player(players,index_player):
    print(index_player)
    index_player = int(index_player)
    return 0 if index_player == len(players)-1 else index_player+1


def index_player(id_player, players):
    for player in players:
        if player.auto_increment_id == id_player:
            return players.index(player)
    return None
    
def calculate_position(player_pos, movement):
    position =  [player_pos[0]+movement[0], player_pos[1]+movement[1]]
    for pos in position:
        if pos < 0 or pos > 7:
            #Raise error
            return player_pos

    return position

def update_board_content(board, player, num_player):
    position = player.pos
    board[position[0]][position[1]] = num_player+1
    return board

def string_to_list(s):
    return ast.literal_eval(s)

def listing_game_players(game_players):
    game_players = list(game_players)
    game_players = listing_player_pos(game_players)
    return game_players

def listing_player_pos(players):
    return [convert_pos(p) for p in players]

def convert_pos(player):
    player.pos = string_to_list(player.pos)
    return player

def build_game_state(game_state_data, players, curr_player):

    players = build_players_entities(players)

    game_state = {
        "game_id" : game_state_data.auto_increment_id,
        "board" : game_state_data.board,
        "players" : players,
        "current_player" : curr_player,
        "code" : 0, 
    }

    return game_state

def build_players_entities(players):
    players_obj = []
    for player in players:
        dic = {
            "id":player.auto_increment_id,
            "name" : player.user.username,
            "color" : player.user.color1,
            "position" : player.pos
        }
        players_obj.append(dic)

    return players_obj

def move_pos(player, movement, game_state, players):
    player.pos = calculate_position(player.pos, movement)
    game_state.board = update_board_content(game_state.board, player, players.index(player))
    return game_state