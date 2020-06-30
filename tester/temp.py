#Run the containers
subprocess.Popen("docker container start umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker container start alert-server", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()