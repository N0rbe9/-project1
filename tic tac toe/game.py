import time

from player import HumanPlayer,GeniusComputerPlayer

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)] #pouzijeme jeden list na zobrazenie 3x3 boardu
        self.current_winner = None #kto vyhrava

    def print_board(self):
        #toto nam robi riadky
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            print("| " + " | ".join(row) + " |")

    @staticmethod
    def print_board_nums():
        # 0 | 1 | 2 atd (vravi nam ktore cislo koresponduje z ktorym boxom)
        number_board = [[str(i) for i in range(j*3, (j+1)*3)] for j in range(3)]
        for row in number_board:
            print("| " + " | ".join(row) + " |")

    def available_moves(self):
        #return[]
        return [i for i ,spot in enumerate(self.board) if spot == " "]
        # co robi enumarate: ["x", "x" , "o"] -->((0,"x") ,(1,"x"), (2,"x"))
        #for (i,spot) in enumerate(self.board):
            #if spot == " ":
                #moves.append(i)
        #return moves

    def empty_squares(self):
        return " " in self.board

    def num_empty_squares(self):
        return self.board.count(" ")

    def make_move(self, square, letter):
        #ked je platny(valid) move,potom spravi move(assign square to letter)
        #potom vrati True. Ked invalid,return False.
        if self.board[square] == " ":
            self.board[square] = letter
            if self.winner(square,letter):
                self.current_winner = letter
            return True
        return True

    def winner(self,square,letter):
        #winner if 3 in row anywhere we have to chech all of these

        #first lets check the row
        row_ind = square // 3
        row = self.board[row_ind * 3 : (row_ind+ 1) *3]
        if all([spot == letter for spot in row]):#all kontrouluje ci je vsetko v liste True
            return True

        #check column
        col_ind = square % 3
        column = [self.board[col_ind +i*3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True

        #check diagonals
        #but only if the square is an even number (0,2,4,6,8)
        #these are the only moves possible to win a diagonal
        if square % 2 == 0:

            diagonal1 = [self.board[i] for i in [0,4,8]] #left to right
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2,4,6]] # right to left
            if all([spot == letter for spot in diagonal2]):
                return True
        #if all of these fail
        return False



def play(game, x_player, o_player, print_game=True):
    #returns the winner of the game or None for tie
    if print_game:
        game.print_board_nums()

    letter = "X" #zaciatocne pisemo
    #bude sa opakovat pokial bude volne miesto
    while game.empty_squares():
        if letter == "O":
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)

        #definovanie funkcie pre pohyb
        if game.make_move(square,letter):
            if print_game:
                print(letter +f" makes a move to {square}")
                game.print_board()
                print("") #just empty line

            #ked vyhra niektto
            if game.current_winner:
                if print_game:
                    print(letter + " wins!")
                return letter

            #potom ako spravime move potrebujeme alternovat(vymenit hracov) pismena
            letter = "O" if letter == "X" else "X"
            #if letter == "X":
               # letter = "O"
           # else:
               # letter = "X"
        #pauza
        time.sleep(0.8)

    if print_game:
        print("It's tie")

if __name__ == "__main__":
    x_player = HumanPlayer("X")
    o_player = GeniusComputerPlayer("O")
    t = TicTacToe()
    play(t,x_player,o_player, print_game=True)