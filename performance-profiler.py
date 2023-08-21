import re
import subprocess


total_time = 0
runs = 100

for _ in range(runs):
    result = subprocess.run(["pytest", "--profile"], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    time_match = re.search(r"(\d+.\d+) seconds", output)
    if time_match:
        time_taken = float(time_match.group(1))
        total_time += time_taken

average_time = total_time / runs
print(f"Average time taken across {runs} runs: {average_time} seconds.")
