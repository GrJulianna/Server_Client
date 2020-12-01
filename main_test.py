import socket, copy, sys, random, pickle
#pickle - обьект в поток байтов

#-----------------------------------------------------------------

lettersCoord = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
printNums = ['1   ', '2   ', '3   ', '4   ', '5   ', '6   ', '7   ', '8   ', '9   ', '10  ']

occupiedSpaces = []

hitSpots = []

messages = ["PLAYER_DISCONNECT", "PASS", "RESPONSE", "ATTACK_COORDS", "PLAYER_WON"]

ships = {
    "Aircraft Carrier": 5,
    "Battleship": 4,
    "Submarine": 3,
    "Destroyer": 3,
    "Patrol Boat": 2
}

destroyedShips = []

#-------------------------------------------------------------------

def set_canvas():
    """sets 10x10 matrix as a playing board"""
    
    return [['·' for c in range(10)] for r in range(10)]


def place_boat(board):
    """
    places boats to appropriate places
    If place occupied - tryagain
    """

    for name, spaces in ships.items():
        print_canvas(board)
        while True:
            start_input = input(f"Please enter a valid coord range (ex. B1;B5) for the {name} with {spaces} spots: ")

            tempBoard = check_ship(copy.deepcopy(board), start_input, spaces, name)

            if tempBoard:
                board = copy.deepcopy(tempBoard)
                break
            else:
                print("Wrong input! Try again!")
                continue

    return board


def check_ship(board, coords, amount, ship):
    """
    checks if ship is in valid place
    """
    global occupiedSpaces

    ID = ship[0] #first letter of the ship == name proected on the board

    try:
        coords = convertCoords(coords)

        #checks if the coords are correct
        if coords:
            iY,iX,fY,fX = coords[0], coords[1], coords[2], coords[3] 
        else:
            return False

        #checks if all coords are inside the board
        if is_inBoard(iY) and is_inBoard(iX) and is_inBoard(fY) and is_inBoard(fX):
            difY = abs(iY - fY)
            difX = abs(iX - fX)
        else:
            return False


        if difY and difX:
            return False

        if difY + 1 != amount and difX + 1 != amount:
            return False

        toChange = []

        #if ship is horizontal
        if difX:
            if iX < fX:
                rangeCoord = list(range(iX, fX + 1))
            else:
                rangeCoord = list(range(fX, iX + 1))
            #
            for z in rangeCoord:
                toChange.append([iY, z])
        #if ship is vertical
        else:
            if iY < fY:
                rangeCoord = list(range(iY, fY + 1))
            else:
                rangeCoord = list(range(fY, iY + 1))
            for z in rangeCoord:
                toChange.append([z, iX])

        if [z for z in toChange if z in occupiedSpaces]:
            return False

        occupiedSpaces += toChange

        return changeBoard(board, toChange, ID)

    except BaseException:
        return False


def print_canvas(copyboard):
    """
    prints canvas/matrix row by row
    - with adding X and Y axis 
    - with saved progress (placed ships, hit ships)
    """
    board = copy.deepcopy(copyboard)
    temp_lettersCoord = ['    '] + lettersCoord

    for counter, i in enumerate(board):
        board[counter].insert(0, printNums[counter])

    board.insert(0, temp_lettersCoord)
    board.insert(1, [])
    for i in board:
        print(' '.join(i))


def to_int(x):
    """
    converts (Xi;Yj) into numbers (coordinats on the matrix)
    """
    try:
        int(x)
        return True

    except BaseException:
        return False


def is_inBoard(x):
    """checks if coord is inside the boarders"""
    return 0 <= x <= 9


def changeBoard(board, coords, index):
    """
    prints new board with ship name
    """
    if not coords:
        return board

    tempBoard = copy.deepcopy(board)
    for col, row in coords:
        tempBoard[col][row] = index

    return tempBoard


def convertCoords(coords):
    """
    converts coordinates into number coordinates in matrix
    """
    try:
        coords = coords.split(';') #splits str into parts (between ';')

        if len(coords) != 2:
            return False
        if not (to_int(coords[0][1:]) and to_int(coords[1][1:])):
            return False

        iY = int(coords[0][1:]) - 1
        iX = lettersCoord.index(coords[0][0].upper())
        fY = int(coords[1][1:]) - 1
        fX = lettersCoord.index(coords[1][0].upper())

        return [iY, iX, fY, fX]
    except BaseException:
        return False


def convert_hitcoord(hitcoord):
    """
    converts the hit coordinate from Xi to [y,x] as matrix coords
    """
    try:
        lenC = len(hitcoord)

        if not (lenC == 2 or lenC == 3):
            return False

        if not to_int(hitcoord[1:]):
            return False

        Y = int(hitcoord[1:]) - 1
        X = lettersCoord.index(hitcoord[0].upper())

        if not is_inBoard(X) or not is_inBoard(Y):
            return False

        return [Y, X]

    except BaseException:
        return False



def getAttackCoord():
    """
    gets a hit coordinate
    """
    global hitSpots

    while True:
        print(f"Current board:")
        print_canvas(changeBoard(set_canvas(), hitSpots, 'X'))

        inp_hitcoord = input("Enter a coordinate which you want to hit (ex. A1): ")

        coord = convert_hitcoord(inp_hitcoord)

        if not coord:
            continue

        if coord in hitSpots or not (is_inBoard(coord[0]) and is_inBoard(coord[1])):
            continue

        hitSpots.append(coord)

        return coord


def getResponse(coord):
    """
    shows responce of which ship has been hit.
    checks if one of the players: hits ship, hits nothing or wins
    """
    global _BOARD, destroyedShips

    print(f"The enemy shot at {lettersCoord[coord[0]]}{coord[1]}!")

    hitSpot = _BOARD[coord[0]][coord[1]]

    hitShip = None

    sunkShip = False

    if hitSpot != '·':
        _BOARD[coord[0]][coord[1]] = 'X'

        if hitSpot == 'A':
            hitShip = "Aircraft Carrier"
            if not any('A' in sub for sub in _BOARD) and 'A' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('A')
        elif hitSpot == 'B':
            hitShip = "Battleship"
            if not any('B' in sub for sub in _BOARD) and 'B' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('B')
        elif hitSpot == 'S':
            hitShip = "Submarine"
            if not any('S' in sub for sub in _BOARD) and 'S' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('S')
        elif hitSpot == 'D':
            hitShip = "Destroyer"
            if not any('D' in sub for sub in _BOARD) and 'D' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('D')
        elif hitSpot == 'P':
            hitShip = "Patrol Boat"
            if not any('P' in sub for sub in _BOARD) and 'P' not in destroyedShips:
                sunkShip = True
                destroyedShips.append('P')

    _BOARD[coord[0]][coord[1]] = 'X'

    if len(destroyedShips) == 5:
        print("The opponent wins, he sunk all the ships!")
        return messages[4]

    if hitShip:
        print(f"They hit the {hitShip}!")
        toReturn = "You hit a ship!"
        if sunkShip:
            print("And they sunk it!")
            toReturn = "You sunk a ship!"

    else:
        print("They hit nothing!")
        toReturn = "You hit nothing!"

    print("Your current board:")
    print_canvas(_BOARD)

    return toReturn


def processResponse(message):
    """
    checks if one of the players has won the game
    """
    if message == messages[4]:
        print("You sunk all the ships, you win!")
        sys.exit()

    print(message)


def whoStarts():
    return random.randint(0, 100) < 50


#PROGRAM STARTS HERE------------------------------------------------------------------------------------------------

print('''
How To Play:

- from the first terminal start playing as "Server";
- from the second terminal start playing as "Client";
- wait for connection and play.

Note: the game will end once one of the players wins OR leaves the game.
''')

_BOARD = set_canvas()
_BOARD = place_boat(_BOARD)

print("This is your board:: ")
print_canvas(_BOARD)

serv = False
try:
    while True:
        inp = input("Are you a server (S) or a client (C)?: ")
        if inp.upper() == 'C':
            print("You are a client")
            break
        elif inp.upper() == 'S':
            print("You are a server")
            serv = True
            break

    if serv:

        player_name = input("Enter your server name: ")

        s = socket.socket()
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        port = 2222
        s.bind((host, port))

        print(f"\nThis computer: {host} - {ip}")

        s.listen(1)

        print("\nWaiting for connections")
        conn, addr = s.accept()
        print(f"\nreceived connection from {addr[0]} - {addr[1]}")

        other_name = conn.recv(1024).decode()

        print(f"\n{other_name} has joined the game")

        conn.send(player_name.encode())

        startOfGame = True
        while True:
            if startOfGame:
                if whoStarts():
                    conn.send(pickle.dumps([None, messages[1]]))

                else:
                    conn.send(pickle.dumps([getAttackCoord(), messages[3]]))

            startOfGame = False

            resp = conn.recv(4096)

            resp = pickle.loads(resp)

            if resp[1] == messages[1]:
                print("\n\n\n")
                conn.send(pickle.dumps([getAttackCoord(), messages[3]]))

            elif resp[1] == messages[2]:
                processResponse(resp[0])
                conn.send(pickle.dumps([None, messages[1]]))
                print("\n\n\n")

            elif resp[1] == messages[3]:
                conn.send(pickle.dumps([getResponse(resp[0]), messages[2]]))

    else:
        player_name = input("Enter your client name: ")

        s = socket.socket()
        hostClient = socket.gethostname()
        ipClient = socket.gethostbyname(hostClient)
        port = 2222

        print(f"\nThis computer: {hostClient} - {ipClient}")
        host = input("Enter the server address: ")
        print(f"\nTrying to connect to {host} by port {port}")

        s.connect((host, port))
        print("\nConnected successfully")

        s.send(player_name.encode())
        other_name = s.recv(1024).decode()

        print(f"You are playing against {other_name}")

        while True:
            resp = s.recv(4096)

            resp = pickle.loads(resp)

            if resp[1] == messages[1]:
                print("\n\n\n")
                s.send(pickle.dumps([getAttackCoord(), messages[3]]))

            elif resp[1] == messages[2]:
                processResponse(resp[0])
                s.send(pickle.dumps([None, messages[1]]))
                print("\n\n\n")

            elif resp[1] == messages[3]:
                s.send(pickle.dumps([getResponse(resp[0]), messages[2]]))

except BaseException as error:
    print(f"Connection lost. error: {error}")
