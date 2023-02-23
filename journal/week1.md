# Week 1 — App Containerization

## Challenges I faced and how I overcome them

### GitPod not persisting AWS CLI installations between start stops

Prebuild was added to .gitpod.yml
```bash
github:
  prebuilds:    
    master: true    
    branches: true    
    pullRequests: true    
    pullRequestsFromForks: false    
    addCheck: true    
    addComment: false    
    addBadge: false
```

AWS CLI needed to be reinstalled even with activating prebuild on GitPod like so:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws --version
bash: aws: command not found
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ cd ..
gitpod /workspace $ sudo ./aws/install
You can now run: /usr/local/bin/aws --version
gitpod /workspace $ aws --version
aws-cli/2.10.2 Python/3.9.11 Linux/5.15.0-47-generic exe/x86_64.ubuntu.20 prompt/off
gitpod /workspace $ 
```

### GitPod did not have Docker extension preinstalled

This can be probably rectified with .gitpod.yml by adding ms-azuretools.vscode-docker into extensions

### Docker compose file was in incorrect folder

When I ran compose up first time from the left navigation pane, Docker did not produce working containers and both containers were in red status. 
* _Trobleshooting steps:_
    * I looked into the logs and the error was saying that FLASK_APP variable is not set and some files are not found. 

* _Solution:_
    * The problem was that I created docker-compose not on the root but inside the the front-end folder when clicked adding file on the left side pane! Sometimes I love bash commands better than point & click approach. It was such a baffling and silly error to create file in a wrong place. 

* _Status:_
    * It's all working now. 
