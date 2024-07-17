import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# TODO:
# Percentage of wins if white/black does not castle. STATUS: COMPLETED ✅
# Percentage diff between openings. STATUS: NOT STARTED 🟥
# How initiative/dangerous are openings. STATUS: NOT STARTED 🟥
# Percentage of time forfeit/resign etc for different time controls. STATUS: NOT STARTED 🟥
# How likely is it to win if opponent made a mistake in the opening (first 10-20 moves). STATUS: NOT STARTED 🟥
# How many games ended during certain amount of moves. STATUS: COMPLETED ✅
# Percentage of how often a certain piece delivered checkmate. STATUS: COMPLETED ✅🟡
# How likely is player to lose after taking out queen in first 5-10 moves. STATUS: NOT STARTED 🟥

LIMITED_GAMES = 5000
TURN_TO_PERCENTAGE = 100
ELO_LIMIT_UP = 2800
ELO_LIMIT_DOWN = 0
pd.set_option('display.max_columns', None)

COLUMNS = ["WhiteElo", "BlackElo", "Opening", "Result", "Termination", "TimeControl", "Category"]
COLUMNS.extend([f"Move_ply_{i}" for i in range(1, 201)])
DF_CHESS_DATA = pd.read_csv("200k_blitz_rapid_classical_bullet.csv", nrows=LIMITED_GAMES, low_memory=False,
                            usecols=COLUMNS)
# start_time = time.time()


def plot_all():
    """Show the percentage of wins by white/black pieces and draws, reading only 'Result' column"""

    games = DF_CHESS_DATA[["Result"]]
    total = games.shape[0]

    white_wins = games[games["Result"] == "1-0"].shape[0]
    draws = games[games["Result"] == "1/2-1/2"].shape[0]
    black_wins = total - white_wins - draws

    # by_amount = [white_wins, draws, black_wins]
    to_percent = TURN_TO_PERCENTAGE / total
    percentages = [white_wins * to_percent, draws * to_percent, black_wins * to_percent]
    results = ["1-0", "1/2-1/2", "0-1"]

    plt.bar(results, percentages)
    plt.ylim(0, 60)
    plt.xlabel('White won / Draw / Black won')
    plt.ylabel('Percentage')
    plt.title(f'Game outcomes (out of {LIMITED_GAMES}) percentage')
    plt.show()


def all_opening():
    openings = DF_CHESS_DATA["Opening"]
    opening_number = {}

    for opening in openings:
        if ":" in opening:
            opening = opening[:opening.index(":")]
        elif "," in opening:
            opening = opening[:opening.index(",")]
        elif "#" in opening:
            opening = opening[:opening.index("#") - 1]
        opening_number[opening] = 1 + opening_number.get(opening, 0)

    most_popular = {}
    for i, x in opening_number.items():
        if x > 5000:
            most_popular[i] = x
    print(most_popular)
    # plt.bar(range(1, len(names)+1), times_played)
    # plt.xticks(range(1, len(names) + 1))
    # plt.xlabel("Openings")i
    # plt.ylabel('Times played')
    # plt.title('Most often played openings')
    # plt.show()


def limit_moves(start, end, iteration):
    """Create a list to save 'Result' column and moves depending on condition, to use for 'usecols' in read_csv"""

    moves = []
    for i in range(start, end, iteration):
        moves.append(f"Move_ply_{i}")
    moves.append("Result")
    return moves


def calculate_no_castle(color, opening):
    start = 7
    end = 41
    if color == "White":
        moves = limit_moves(start, end, 2)
    else:
        moves = limit_moves(start+1, end, 2)

    moves.append("Opening")
    games = DF_CHESS_DATA[moves]
    games = games[games["Opening"].apply(lambda x: opening in x)]
    castle = games[games[moves[:-2]].apply(lambda x: x.str.contains('O-O').any(), axis=1)]
    no_castle = games[games[moves[:-2]].apply(lambda x: not x.str.contains('O-O').any(), axis=1)]
    result_no_castle = no_castle["Result"]
    result_castle = castle["Result"]

    loses = 0
    draws = 0
    wins = 0

    for result in result_no_castle:
        if result == "1-0":
            wins += 1
        elif result == "0-1":
            loses += 1
        else:
            draws += 1

    if color == "Black":
        wins, loses = loses, wins

    plot_no_castle([len(result_no_castle), wins, draws, loses, opening], color)


def plot_no_castle(statistics, color):
    results = ["1-0", "1/2-1/2", "0-1"]
    total, wins, draws, loses, opening = statistics

    percentage = [wins / total * TURN_TO_PERCENTAGE, draws / total * TURN_TO_PERCENTAGE, loses / total * TURN_TO_PERCENTAGE]

    plt.bar(results, percentage)
    plt.yticks(ticks=range(0, 61, 5))
    plt.xlabel(f'{color} won / Draw / {color} lost')
    plt.ylabel('Percentage')
    plt.title(f'{opening} outcomes (total of {total})] \nwhere {color} did not castle in first 20 moves')
    plt.show()


def game_longitude():
    diff = 10

    moves = limit_moves(diff*2+1, 200-diff, diff*2)
    amount = len(moves)
    moves.extend(["Move_ply_200", "WhiteElo", "BlackElo"])

    chess_games = DF_CHESS_DATA[moves]

    def proportions(games):
        longitude = {}
        total = games.shape[0]
        number_of_games = total

        for i in range(1, amount):
            games = games[games[f"Move_ply_{i * diff * 2 + 1}"].notna()]
            longitude[f"{i * diff}"] = (number_of_games - games.shape[0])/total*TURN_TO_PERCENTAGE
            number_of_games = games.shape[0]

        games = games[games["Move_ply_200"].notna()]
        temp = number_of_games - games.shape[0]

        # if not games.empty:
        #     temp += games["Move_ply_200"].apply(lambda x: '#' in x).sum()
        #     print(games["Move_ply_200"].apply(lambda x: '#' in x))

        longitude["100"] = temp/total*TURN_TO_PERCENTAGE
        longitude[">100"] = (number_of_games - temp)/total*TURN_TO_PERCENTAGE
        return longitude

    white_results = proportions(chess_games[
                            (chess_games["Result"] == "1-0") &
                            (chess_games["WhiteElo"] <= ELO_LIMIT_UP) &
                            (chess_games["WhiteElo"] >= ELO_LIMIT_DOWN)])
    black_results = proportions(chess_games[
                            (chess_games["Result"] == "0-1") &
                            (chess_games["BlackElo"] <= ELO_LIMIT_UP) &
                            (chess_games["BlackElo"] >= ELO_LIMIT_DOWN)])

    # print(white_results, black_results)

    width = 0.40
    x = np.arange(len(white_results.keys()))
    fig, ax = plt.subplots()
    ax.bar(x - width / 2, white_results.values(), width, label='White Wins', color='skyblue')
    ax.bar(x + width / 2, black_results.values(), width, label='Black Wins', color='salmon')

    ax.set_xlabel('Moves')
    ax.set_ylabel('Percentage')
    ax.set_title('Distribution of games ending after certain amount of moves\n'
                 f'Elo limit is from {ELO_LIMIT_DOWN} to {ELO_LIMIT_UP}')
    ax.set_xticks(x)
    ax.set_yticks(ticks=range(0, 46, 5))
    ax.set_ylim(0, 45)
    ax.set_xticklabels(white_results.keys())
    ax.legend()

    # def add_labels(rects):
    #     for rect in rects:
    #         height = rect.get_height()
    #         ax.annotate(f'{height:.1f}%',
    #                     xy=(rect.get_x() + rect.get_width() / 2, height),
    #                     xytext=(0, 3),  # 3 points vertical offset
    #                     textcoords="offset points",
    #                     ha='center', va='bottom')
    #
    # add_labels(rects1)
    # add_labels(rects2)

    fig.tight_layout()
    plt.show()


def which_piece_mated():
    start = 4
    end = 200

    moves = limit_moves(start, end+1, 1)
    moves.append("Termination")

    df_games = DF_CHESS_DATA[moves]
    df_games = df_games[df_games["Termination"] == "Normal"]
    mate_by_white = df_games[df_games["Result"] == "1-0"]
    mate_by_black = df_games[df_games["Result"] == "0-1"]

    piecesList = {}

    def find_mate(games, s, e):
        # game_ended = games[games[f"Move_ply_{e}"].isna()]
        # not_ended = games[~games[f"Move_ply_{e}"].notna()]
        a = 0
        for i in range(s, e, 2):
            mate_moves = games[(games[f"Move_ply_{i+1}"].isna()) & (games[f"Move_ply_{i}"].notna())]
            mate_moves = mate_moves[mate_moves[f"Move_ply_{i}"].apply(lambda x: '#' in x)]
            # games = games[games[f"Move_ply_{i+1}"].notna()]

            if not mate_moves.empty:
                a += mate_moves.shape[0]
                # print(mate_moves[f"Move_ply_{i}"].head(1))
                find_piece(mate_moves[f"Move_ply_{i}"])

        print(a)

    def find_piece(games):
        # first = games.iloc[0]
        # if games.shape[0] > 4:
        #     second = games.iloc[1]
        #     third = games.iloc[2]
        #     print(second[0])
        #     print(third[0])
        # print(first[0])
        piecesList["promotion"] = games.str.contains("=").sum() + piecesList.get("promotion", 0)
        piecesList["Queen"] = (games.str[0] == "Q").sum() + piecesList.get("Queen", 0)
        piecesList["Rook"] = (games.str[0] == "R").sum() + piecesList.get("Rook", 0)
        piecesList["Bishop"] = (games.str[0] == "B").sum() + piecesList.get("Bishop", 0)
        piecesList["Knight"] = (games.str[0] == "N").sum() + piecesList.get("Knight", 0)
        piecesList["King"] = (games.str[0] == "K").sum() + piecesList.get("King", 0)
        piecesList["pawn"] = (games.str.islower()).sum() + piecesList.get("pawn", 0)
        piecesList["castle"] = games.str.contains("O-O").sum() + piecesList.get("castle", 0)

    find_mate(mate_by_white, start+1, end)
    find_mate(mate_by_black, start, end-1)

    print(piecesList)

    # for i in range(4, 201, 28):
    #     find_mate()
    # if chess_games[f"Move_ply_{x}"].apply(lambda y: y.str.contains('#').any(), axis=1):
    #     a = 5
    #
    # if x > 5:
    #     before_x = chess_games[chess_games[f"Move_ply{x}"].isna()]
    #     which_piece_mated(x / 2, a)
    #
    #
    # after_x = chess_games[chess_games[f"Move_ply{x}"].notna()]


def main():
    # plot_all()

    # calculate_no_castle("White", "Caro-Kann Defense")
    # calculate_no_castle("Black", "Caro-Kann Defense")
    #
    # calculate_no_castle("White", "Sicilian Defense")
    # calculate_no_castle("Black", "Sicilian Defense")

    game_longitude()
    # which_piece_mated()

    # all_opening()


# main()
# end_time = time.time()
# print("It took", end_time-start_time)

