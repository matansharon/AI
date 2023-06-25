import subprocess

# run a command
subprocess.run(["git add --all"], shell=True)
subprocess.run(["git commit -m 'working on app.py'"], shell=True)
subprocess.run(["git push ai_github master"], shell=True)