import subprocess
import sys

# Number of times to run the game
num_runs = 20
wins = 0
ties = 0

# Command to run AI_Runner.py
if int(sys.argv[1]) == 1:
    command = [
        "python3", "AI_Runner.py", "8", "8", "3", "l",
        "$HOME/cs171/CS171-Checkers/src/checkers-python/main.py",
        "$HOME/cs171/CS171-Checkers/Tools/Sample_AIs/Random_AI/main.py"
    ]
    win_condition = "player 1 wins"

elif int(sys.argv[1]) == 2:
    command = [
        "python3", "AI_Runner.py", "8", "8", "3", "l",
        "$HOME/cs171/CS171-Checkers/Tools/Sample_AIs/Random_AI/main.py",
        "$HOME/cs171/CS171-Checkers/src/checkers-python/main.py"
    ]
    win_condition = "player 2 wins"
else:
    sys.exit(1)

# Loop to run the game 100 times
for i in range(num_runs):
    print(f"Running game {i + 1} of {num_runs}...")

    # Run the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if Player 1 won
    if win_condition in result.stdout:
        wins += 1
    if "Tie" in result.stdout:
        ties += 1

# Print the results
print(f"\nYour AI won {wins} out of {num_runs} games.")
print(f"Win rate: {(wins / num_runs) * 100:.2f}%")
print(f"\nYour AI won and tied {wins + ties} out of {num_runs} games.")
print(f"Win and tie rate: {((wins + ties) / num_runs) * 100:.2f}%")