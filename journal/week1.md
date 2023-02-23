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

