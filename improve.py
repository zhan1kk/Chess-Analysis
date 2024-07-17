import pandas as pd
import matplotlib.pyplot as plt


LIMITED_GAMES = 200000
FULL_PERCENTAGE = 100
ELO_LIMIT_UP = 3500
ELO_LIMIT_DOWN = 0
pd.set_option('display.max_columns', None)

COLUMNS = ["WhiteElo", "BlackElo", "Opening", "Result", "Termination", "TimeControl", "Category"]
COLUMNS.extend([f"Move_ply_{i}" for i in range(1, 201)])
DF_CHESS_DATA = pd.read_csv("200k_blitz_rapid_classical_bullet.csv", nrows=LIMITED_GAMES, low_memory=False,
                            usecols=COLUMNS)


def termination_reason():
    games = DF_CHESS_DATA[["Termination", "Category"]]
    normal = games[games["Termination"] == "Normal"]
    time_forfeit = games[games["Termination"] == "Time forfeit"]
    categories1 = [normal[normal["Category"] == "Bullet"].shape[0],
                   normal[normal["Category"] == "Blitz"].shape[0],
                   normal[normal["Category"] == "Rapid"].shape[0],
                   normal[normal["Category"] == "Classical"].shape[0]]

    categories2 = [time_forfeit[time_forfeit["Category"] == "Bullet"].shape[0],
                   time_forfeit[time_forfeit["Category"] == "Blitz"].shape[0],
                   time_forfeit[time_forfeit["Category"] == "Rapid"].shape[0],
                   time_forfeit[time_forfeit["Category"] == "Classical"].shape[0]]
    print(categories1, categories2)


def limit_moves(start, end, iteration):
    """Create a list to save 'Result' column and moves depending on condition, to use for 'usecols' in read_csv"""

    moves = []
    for i in range(start, end, iteration):
        moves.append(f"Move_ply_{i}")
    moves.append("Result")
    return moves


def calculate_no_castle(opening, till_move):
    start = 7
    end = till_move * 2 + 1
    moves = limit_moves(start, end, 1)
    moves.append("Opening")

    chess_games = DF_CHESS_DATA[moves]
    if len(opening) > 3:
        chess_games = chess_games[chess_games["Opening"].apply(lambda x: opening in x)]

    def find_castle(df, beginning, iteration, negative):
        if negative == "yes":
            games = df[df[moves[beginning:-2:iteration]].apply(lambda x: x.str.contains('O-O').any(), axis=1)]
            games = games[games[moves[beginning + 1:-2:iteration]].apply(lambda x: x.str.contains('O-O').any(), axis=1)]
        else:
            games = df[df[moves[beginning:-2:iteration]].apply(lambda x: not x.str.contains('O-O').any(), axis=1)]
        results = games["Result"]

        white_wins, draws, black_wins = 0, 0, 0
        for result in results:
            if result == "1-0":
                white_wins += 1
            elif result == "0-1":
                black_wins += 1
            else:
                draws += 1

        return [len(results), white_wins/len(results)*100, draws/len(results)*100, black_wins/len(results)*100]

    castle_happened = chess_games[chess_games[moves[:-2]].apply(lambda x: x.str.contains('O-O').any(), axis=1)]

    both_castled = find_castle(castle_happened, 0, 2, "yes")
    no_castle = find_castle(chess_games, 0, 1, "no")
    only_black_castled = find_castle(castle_happened, 0, 2, "no")
    only_white_castled = find_castle(castle_happened, 1, 2, "no")

    print(both_castled, no_castle, only_white_castled, only_black_castled)

    results = ["White won", "Draw", "Black won"]
    fig, axs = plt.subplots(2, 2)
    # fig.suptitle(f'{opening} openings played results \nwith impact of castle in first {till_move} moves')
    fig.suptitle(f'Impact of castle on game outcomes ({opening}) \nCastle happened during first {till_move} moves')

    axs[0, 0].bar(results, both_castled[1:])
    axs[0, 0].set_title(f"Both sides castled (Total: {both_castled[0]})")

    axs[0, 1].bar(results, no_castle[1:])
    axs[0, 1].set_title(f"No side castled (Total: {no_castle[0]})")

    axs[1, 0].bar(results, only_black_castled[1:])
    axs[1, 0].set_title(f"Only black castled (Total: {only_black_castled[0]})")

    axs[1, 1].bar(results, only_white_castled[1:])
    axs[1, 1].set_title(f"Only white castled (Total: {only_white_castled[0]})")

    for ax in axs.flatten():
        ax.set_ylabel('Percentage')
        ax.set_yticks(ticks=range(0, 61, 10))

    plt.tight_layout()
    plt.show()


# calculate_no_castle("Caro-Kann Defense", 10)
calculate_no_castle("Caro-Kann Defense", 15)
# calculate_no_castle("Caro-Kann Defense", 20)

# calculate_no_castle("Sicilian Defense", 10)
calculate_no_castle("Sicilian Defense", 15)
# calculate_no_castle("Sicilian Defense", 20)

# calculate_no_castle("Italian Game", 10)
calculate_no_castle("Italian Game", 15)
# calculate_no_castle("Italian Game", 20)

# calculate_no_castle("Queen's Pawn Game", 10)
calculate_no_castle("Queen's Pawn Game", 15)
# calculate_no_castle("Queen's Pawn Game", 20)

# calculate_no_castle("Ruy Lopez", 10)
calculate_no_castle("Ruy Lopez", 15)
# calculate_no_castle("Ruy Lopez", 20)

# calculate_no_castle("French Defense", 10)
calculate_no_castle("French Defense", 15)
# calculate_no_castle("French Defense", 20)

# calculate_no_castle("King's Pawn Game", 10)
calculate_no_castle("King's Pawn Game", 15)
# calculate_no_castle("King's Pawn Game", 20)

# calculate_no_castle("", 20)
# calculate_no_castle("", 15)
# calculate_no_castle("", 10)

# termination_reason()
