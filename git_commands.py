import subprocess

# Run a Git command

subprocess.run('git add --all', capture_output=True, text=True)

subprocess.run('git commit -m "scraping a little bit"', capture_output=True, text=True)
subprocess.run('git push ai_github master', capture_output=True, text=True)