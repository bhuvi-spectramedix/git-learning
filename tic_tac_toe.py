
class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol


class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[" " for _ in range(size)] for _ in range(size)]

    def display(self):
        print("\n" + "-" * (self.size * 4))
        for row in self.grid:
            print(" | ".join(row))
            print("-" * (self.size * 4))

    def update_cell(self, row, col, symbol):
        if self.grid[row][col] == " ":
            self.grid[row][col] = symbol
            return True
        return False

    def is_full(self):
        return all(cell != " " for row in self.grid for cell in row)


class Game:
    def __init__(self):
        self.players = []
        self.board = None

    def setup_game(self):
        # Board size selection
        size = int(input("Enter board size (N for N x N board): "))
        self.board = Board(size)

        # Number of players
        num_players = int(input("Enter number of players: "))

        used_symbols = set()

        # Player setup
        for i in range(num_players):
            name = input(f"Enter name for Player {i+1}: ")

            while True:
                symbol = input(f"Enter a single-character symbol for {name}: ")
                if len(symbol) != 1:
                    print("Symbol must be a single character!")
                elif symbol in used_symbols:
                    print("Symbol already taken. Choose another.")
                else:
                    used_symbols.add(symbol)
                    break

            self.players.append(Player(name, symbol))

    def check_win(self, symbol):
        size = self.board.size
        g = self.board.grid

        # Check rows
        for row in g:
            if all(cell == symbol for cell in row):
                return True

        # Check columns
        for col in range(size):
            if all(g[row][col] == symbol for row in range(size)):
                return True

        # Check main diagonal
        if all(g[i][i] == symbol for i in range(size)):
            return True

        # Check anti-diagonal
        if all(g[i][size - 1 - i] == symbol for i in range(size)):
            return True

        return False

    def play(self):
        self.setup_game()
        turn = 0

        while True:
            self.board.display()
            current_player = self.players[turn % len(self.players)]
            print(f"\n{current_player.name}'s turn ({current_player.symbol})")

            # Input move
            try:
                row = int(input("Enter row (0-based index): "))
                col = int(input("Enter column (0-based index): "))

                if not (0 <= row < self.board.size and 0 <= col < self.board.size):
                    print("Invalid move! Position out of range.")
                    continue

                if not self.board.update_cell(row, col, current_player.symbol):
                    print("Cell already occupied! Try another move.")
                    continue
            except ValueError:
                print("Invalid input! Enter numbers only.")
                continue

            # Check win
            if self.check_win(current_player.symbol):
                self.board.display()
                print(f"\n🎉 {current_player.name} wins!")
                break

            # Check draw
            if self.board.is_full():
                self.board.display()
                print("\nIt's a draw!")
                break

            turn += 1


# Run the game
if __name__ == "__main__":
    game = Game()
    game.play()