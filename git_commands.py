import subprocess

# Run a Git command

subprocess.run('git add --all', capture_output=True, text=True)

subprocess.run('git commit -m "moving to liam solution"', capture_output=True, text=True)
subprocess.run('git push ai_github master', capture_output=True, text=True)