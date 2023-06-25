import subprocess

# run a command
subprocess.run(["git add --all"], shell=True)
subprocess.run(["git commit -m 'chat-pdf in clone mode'"], shell=True)
subprocess.run(["git push ai_github master"], shell=True)