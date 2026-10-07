import random
class Game:
    def __init__(self):
        self.board = [
            [],
            [],
            [],
            [],
            [],
            [],
            []
        ]
        self.red = ""
        self.blue = ""
        self.turn = random.choice([0, 1])
        self.winner = ""
        self.connected = None
    
    def play(self, player, row):
        if self.turn == player and len(self.board[row]) < 6 and self.winner == "":
            self.board[row].append(player)
            self.turn = 0 if self.turn else 1
            if self.is_connected():
                self.connected = self.is_connected()
                self.winner = "red" if self.connected[-1] == 0 else "blue"
            elif self.is_draw():
                self.winner = "draw"
            return True
        return False

    def is_connected(self):
        for row in range(len(self.board)):
            if len(self.board[row]) >= 4:
                for col in range(len(self.board[row])-3):
                    if self.board[row][col] == self.board[row][col+1] == self.board[row][col+2] == self.board[row][col+3]:
                        return row, col, "col", self.board[row][col]
            if row < 4:
                for col in range(len(self.board[row])):
                    if col+1 <= len(self.board[row+1]) and col+1 <= len(self.board[row+2]) and col+1 <= len(self.board[row+3]):
                        if self.board[row][col] == self.board[row+1][col] == self.board[row+2][col] == self.board[row+3][col]:
                            return row, col, "row", self.board[row][col]
                    if col+1 <= len(self.board[row+1])-1 and col+1 <= len(self.board[row+2])-2 and col+1 <= len(self.board[row+3])-3:
                        if self.board[row][col] == self.board[row+1][col+1] == self.board[row+2][col+2] == self.board[row+3][col+3]:
                            return row, col, "inc", self.board[row][col]
                    if col >= 3 and col-1 <= len(self.board[row+1])-1 and col-2 <= len(self.board[row+2])-1 and col-3 <= len(self.board[row+3])-1:
                        if self.board[row][col] == self.board[row+1][col-1] == self.board[row+2][col-2] == self.board[row+3][col-3]:
                            return row, col, "dec", self.board[row][col]
        return None

    def is_draw(self):
        for row in range(len(self.board)):
            if len(self.board[row]) < 6:
                return
        return True