import subprocess

tool_pipe = subprocess.PIPE

#Create the containers
subprocess.Popen("docker container create -it --name umbox u0-sniffer-based", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker container create -it --name e1 c_eth1", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker run -d --name e2 library/alpine:3.5 sleep 3600d", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker run -d --name e3 library/alpine:3.5 sleep 3600d", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Create the networks
subprocess.Popen("docker network create eth1", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create eth2", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create eth3", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Connect the networks
subprocess.Popen("docker network connect eth1 umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth2 umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth3 umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth1 e1", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth2 e2", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth3 e3", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Run the containers
subprocess.Popen("docker container start umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker container start e1", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()