import subprocess

tool_pipe = subprocess.PIPE

subprocess.Popen("docker build -t alert-server-image ./server", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Reset
subprocess.Popen("docker stop $(docker ps -a -q)", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker rm $(docker ps -a -q)", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker system prune", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate(input=b"y")

#Create the networks
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth0 eth0_device", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth1 eth1_device", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth2 eth2_device", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network create --opt com.docker.network.bridge.name=br_eth3 eth3_device", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Create the containers
subprocess.Popen("docker container create -it --network eth0_device --name umbox u0-sniffer-based", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker container create -it --network eth0_device -p 6060:6060 --name alert-server alert-server-image", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Connect the networks
subprocess.Popen("docker network connect eth1_device umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth2_device umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker network connect eth3_device umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()

#Run the containers
subprocess.Popen("docker container start umbox", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()
subprocess.Popen("docker container start alert-server", shell=True, stdin=tool_pipe, stdout=tool_pipe, stderr=tool_pipe).communicate()