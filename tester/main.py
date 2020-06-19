import subprocess

tool_pipe = subprocess.PIPE

#subprocess.Popen("docker build -t test ./test", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Reset
subprocess.Popen("docker stop $(docker ps -a -q)", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker rm $(docker ps -a -q)", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker system prune", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate(input=b"y")

#Create the networks
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth1 eth1", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth2 eth2", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth3 eth3", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
#subprocess.Popen("docker network create -d macvlan -o parent=enp0s31f6 eth0", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Create the containers
subprocess.Popen("docker container create -it --name umbox u0-sniffer-based", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
#subprocess.Popen("docker container create -it --network eth2 --name test test", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Connect the networks
subprocess.Popen("docker network connect eth1 umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth2 umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth3 umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Run the containers
subprocess.Popen("docker container start umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
#subprocess.Popen("docker container start test", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
