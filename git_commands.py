import subprocess

import os

# cmd1 = "git add --all"
# cmd2= "git commit -m 'finish the backend of chat-pdf with liam'"
# cmd3 = "git push ai_github master"
# returned_value1 = os.system(cmd1)  # returns the exit code in unix
# returned_value2 = os.system(cmd2)  # returns the exit code in unix
# returned_value3 = os.system(cmd3)  # returns the exit code in unix

# print('returned value:', returned_value1)
# print('returned value:', returned_value2)
# print('returned value:', returned_value3)
# Run a Git command

subprocess.run('git add --all')

subprocess.run('git commit -m "from mac"')
subprocess.run('git push ai_github master')