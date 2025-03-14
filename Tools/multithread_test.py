import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Number of times to run the game
num_runs = 10
wins = 0
ties = 0

working_path = os.getcwd()
home_path = os.path.dirname(working_path)

# Command to run AI_Runner.py
if int(sys.argv[1]) == 1:
    command = [
        "python3", "AI_Runner.py", "7", "7", "2", "l",
        os.path.join(home_path, "src/checkers-python/main.py"),
        os.path.join(home_path, "Tools/Sample_AIs/Average_AI/main.py")
    ]
    win_condition = "player 1 wins"

elif int(sys.argv[1]) == 2:
    command = [
        "python3", "AI_Runner.py", "7", "7", "2", "l",
        os.path.join(home_path, "Tools/Sample_AIs/Average_AI/main.py"),
        os.path.join(home_path, "src/checkers-python/main.py")
    ]
    win_condition = "player 2 wins"
else:
    sys.exit(1)

# Function to run a single game
def run_game(game_num):
    print(f"Starting game {game_num}...")  # Print the game number
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(f"Game {game_num} finished.")  # Print when the game finishes

    if win_condition in result.stdout:
        return 1  # win
    if "Tie" in result.stdout:
        return 0  # tie
    return -1  # loss

# Function to handle results from multiple threads
def handle_results(future):
    global wins, ties
    result = future.result()
    if result == 1:
        wins += 1
    elif result == 0:
        ties += 1

# Using ThreadPoolExecutor to run games concurrently
with ThreadPoolExecutor() as executor:
    futures = [executor.submit(run_game, i+1) for i in range(num_runs)]

    # Wait for all threads to complete and handle results
    for future in futures:
        future.add_done_callback(handle_results)

# Print the results
print(f"\nYour AI won {wins} out of {num_runs} games.")
print(f"Win rate: {(wins / num_runs) * 100:.2f}%")
print(f"\nYour AI won and tied {wins + ties} out of {num_runs} games.")
print(f"Win and tie rate: {((wins + ties) / num_runs) * 100:.2f}%")