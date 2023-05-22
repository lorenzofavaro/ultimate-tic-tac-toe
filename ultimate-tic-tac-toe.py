import sys
import copy
import random

def game_tie(board):
    return all(element != '' for sublst in board for element in sublst)


def check_tris(player, board):
    for row in board:
        if row == [player, player, player]:
            return True
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] == player:
            return True
    if board[0][0] == board[1][1] == board[2][2] == player or board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False


def minimax(max_turn, board, depth=0, alpha=float('-inf'), beta=float('inf')):
    if check_tris('X', board):
        return 10 - depth
    elif check_tris('O', board):
        return depth - 10
    elif game_tie(board):
        return 0

    scores = []
    for i, row in enumerate(board):
        for j, box in enumerate(row):
            if box == '':
                board_copy = copy.deepcopy(board)
                board_copy[i][j] = 'X' if max_turn else 'O'
                score = minimax(not max_turn, board_copy, depth+1, alpha, beta)

                if max_turn:
                    alpha = max(alpha, score)
                else:
                    beta = min(beta, score)

                if alpha >= beta:
                    break

                if depth == 0:
                    scores.append([(i, j), score])
                else:
                    scores.append(score)

    if not scores:  # No move available
        return 0
    
    if depth == 0:
        return list(max(scores, key=lambda x: x[1])[0] if max_turn else min(scores, key=lambda x: x[1])[0])
    else:
        return max(scores) if max_turn else min(scores)


def update_board(player, coordinates, board):
    (row, col) = coordinates
    if player is not None and 0 <= row and 0 <= col and board[row][col] == '':
        board[row][col] = player


def compute_min_sub_board_coordinates(x, y):
    return [x//3*3, y//3*3]


def get_sub_board_from_coordinates(board, min_x, min_y):
    return [col[min_y:min_y+3] for col in board[min_x:min_x+3]]


def compute_move(board, min_coord=None):
    print(f'compute_move, is macro_board? ', min_coord is None, file=sys.stderr, flush=True)
    print(f'board: {board}', file=sys.stderr, flush=True)

    valid_coordinates = compute_valid_coordinates(board)
    if len(valid_coordinates) == 9:
        move = [random.choice([0,2]),random.choice([0,2])]
    elif len(valid_coordinates) == 8:
        move = [1,1] if [1,1] in valid_coordinates else [random.choice([0,2]),random.choice([0,2])]
    else:
        move = minimax(True, copy.deepcopy(board))

    if min_coord:
        move[0] += min_coord[0]
        move[1] += min_coord[1]
    return move


def compute_valid_coordinates(board):
    valid_coordinates = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == '':
                valid_coordinates.append([i, j])
    return valid_coordinates


def update_macro_board(player, coordinates, macro_board, board):
    if 0 <= coordinates[0] and 0 <= coordinates[1]:
        min_x, min_y = compute_min_sub_board_coordinates(*coordinates)
        sub_board = get_sub_board_from_coordinates(board, min_x, min_y)

        mark = None
        for player in ['X', 'O']:
            if check_tris(player, sub_board):
                mark = player
        
        if not mark and game_tie(sub_board):
            mark = '.'
        
        update_board(mark, [min_x//3, min_y//3], macro_board)


def compute_sub_board(macro_board, board, valid_coordinates):
    x_set = set([coord[0]//3 for coord in valid_coordinates])
    y_set = set([coord[1]//3 for coord in valid_coordinates])

    if len(x_set) == 1 and len(y_set) == 1:
        coordinates = compute_min_sub_board_coordinates(*valid_coordinates[0])
    else:
        coordinates = compute_move(macro_board)
        coordinates[0] *= 3
        coordinates[1] *= 3
        print(f"CHOSEN {coordinates}", file=sys.stderr, flush=True)
    sub_board = get_sub_board_from_coordinates(board, *coordinates)
    return sub_board, coordinates



print("STARTED!", file=sys.stderr, flush=True)
macro_board = [['' for _ in range(3)] for _ in range(3)]
board = [['' for _ in range(9)] for _ in range(9)]

# GAME LOOP
while True:

    # INPUTS
    opponent_row, opponent_col = [int(i) for i in input().split()]
    valid_action_count = int(input())
    valid_coordinates = [[int(j) for j in input().split()] for _ in range(valid_action_count)]

    print(f"ADV: {opponent_row, opponent_col}", file=sys.stderr, flush=True)

    # UPDATE BOARDS - after opponent move
    update_board('O', [opponent_row, opponent_col], board)
    update_macro_board('O', [opponent_row, opponent_col], macro_board, board)
    print(f'macro_board: {macro_board}', file=sys.stderr, flush=True)

    # SUB_BOARD COMPUTATION (OBLIGATED OR NOT)
    sub_board, min_coord = compute_sub_board(macro_board, board, valid_coordinates)

    print(f'sub_board: {sub_board}', file=sys.stderr, flush=True)
    print(f'min_coord: {min_coord}', file=sys.stderr, flush=True)
    
    # MOVE COMPUTATION
    move = compute_move(sub_board, min_coord)

    # UPDATE BOARDS - after my move
    update_board('X', move, board)
    update_macro_board('X', move, macro_board, board)

    # OUTPUT MY MOVE
    print(*move)
