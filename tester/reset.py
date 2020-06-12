import subprocess
tool_pipe = subprocess.PIPE

subprocess.Popen("docker stop $(docker ps -a -q)", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker rm $(docker ps -a -q)", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()