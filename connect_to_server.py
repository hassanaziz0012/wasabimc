import subprocess
subprocess.run('ssh -i "~/Desktop/.ssh/wasabimc.pem" ubuntu@ec2-44-206-19-124.compute-1.amazonaws.com', shell=True)
