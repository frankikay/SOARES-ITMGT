'''Python: Advanced

70 points

This assignment will develop your ability to manipulate data.
We expect that this assignment will equip you to understand
    Python tutorials.

Please refer to the file `advanced_sample_data.py` for examples of:
- the `social_graph` parameter for the relationship_status item
- the `board` parameter for the tic_tac_toe item
- the `route_map` parameter for the eta item
'''

def relationship_status(from_member, to_member, social_graph):
    '''Relationship Status.
    20 points.

    Let us pretend that you are building a new app.
    Your app supports social media functionality, which means that users can have
    relationships with other users.

    There are two guidelines for describing relationships on this social media app:
    1. Any user can follow any other user.
    2. If two users follow each other, they are considered friends.

    This function describes the relationship that two users have with each other.

    Please see `advanced_sample_data.py` for sample data. The social graph
    will adhere to the same pattern.

    Parameters
    ----------
    from_member: str
        the subject member
    to_member: str
        the object member
    social_graph: dict
        the relationship data

    Returns
    -------
    str
        "follower" if from_member follows to_member,
        "followed by" if from_member is followed by to_member,
        "friends" if from_member and to_member follow each other,
        "no relationship" if neither from_member nor to_member follow each other.
    '''
    # Replace `pass` with your code.
    # Stay within the function. Only use the parameters as input. The function should return your answer.

    x = social_graph[from_member]["following"]
    y = social_graph[to_member]["following"]

    if from_member in y:
        if to_member in x:
            return "friends"
        else:
            return "followed by"
    
    elif to_member in x:
        return "follower"
    else:
        return "no relationship"


def tic_tac_toe(board):
    '''Tic Tac Toe.
    25 points.

    Tic Tac Toe is a common paper-and-pencil game.
    Players must attempt to successfully draw a straight line of their symbol across a grid.
    The player that does this first is considered the winner.

    This function evaluates a tic tac toe board and returns the winner.

    Please see `advanced_sample_data.py` for sample data. The board will adhere
    to the same pattern. The board may by 3x3, 4x4, 5x5, or 6x6. The board will never
    have more than one winner. The board will only ever have 2 unique symbols at the same time.

    Parameters
    ----------
    board: list
        the representation of the tic-tac-toe board as a square list of lists

    Returns
    -------
    str
        the symbol of the winner, or "NO WINNER" if there is no winner
    '''
    # Replace `pass` with your code.
    # Stay within the function. Only use the parameters as input. The function should return your answer.

    board_length = len(board)
    winner = None

    for i in range(board_length):
        row_symbol = board[i][0]
        all_same_in_row = True
        
        for j in range(1, board_length):
            if board[i][j] != row_symbol:
                all_same_in_row = False
                break
            
        if all_same_in_row and row_symbol != "":
            winner = row_symbol
            break

    if not winner:
        for i in range(board_length):
            col_symbol = board[0][i]
            all_same_in_col = True
            
            for j in range(1, board_length):
                if board[j][i] != col_symbol:
                    all_same_in_col = False
                    break
                
            if all_same_in_col and col_symbol != "":
                winner = col_symbol
                break

    if not winner:
        diag_symbol = board[0][0]
        all_same_in_diag = True
        
        for i in range(1, board_length):
            if board[i][i] != diag_symbol:
                all_same_in_diag = False
                break
            
        if all_same_in_diag and diag_symbol != "":
            winner = diag_symbol

    if not winner:
        diag_symbol = board[0][board_length - 1]
        all_same_in_diag = True
        
        for i in range(1, board_length):
            if board[i][board_length - 1 - i] != diag_symbol:
                all_same_in_diag = False
                break
            
        if all_same_in_diag and diag_symbol != "":
            winner = diag_symbol

    return winner if winner else "NO WINNER"

def eta(first_stop, second_stop, route_map):
    '''ETA.
    25 points.

    A shuttle van service is tasked to travel along a predefined circlar route.
    This route is divided into several legs between stops.
    The route is one-way only, and it is fully connected to itself.

    This function returns how long it will take the shuttle to arrive at a stop
    after leaving another stop.

    Please see `advanced_sample_data.py` for sample data. The route map will
    adhere to the same pattern. The route map may contain more legs and more stops,
    but it will always be one-way and fully enclosed.

    Parameters
    ----------
    first_stop: str
        the stop that the shuttle will leave
    second_stop: str
        the stop that the shuttle will arrive at
    route_map: dict
        the data describing the routes

    Returns
    -------
    int
        the time it will take the shuttle to travel from first_stop to second_stop
    '''
    # Replace `pass` with your code.
    # Stay within the function. Only use the parameters as input. The function should return your answer.

    if first_stop == second_stop:
        return 0

    current_stop = first_stop
    time_elapsed = 0 
    
    while current_stop != second_stop:
        next_leg = None
        for leg, info in route_map.items():
            if leg[0] == current_stop:
                next_leg = leg
                break
        if next_leg is None:
            return None
        
        time_elapsed += info["travel_time_mins"]
        current_stop = next_leg[1]
    
    return time_elapsed
