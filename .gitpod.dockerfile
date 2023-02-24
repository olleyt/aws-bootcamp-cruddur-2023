FROM gitpod/workspace-full:latest

# installs AWS CLI on a local GitPod env (not container)
# the code copied from Jason's Paul blog: https://www.linuxtek.ca/2023/02/21/diving-deeper-gitpod-cloud-development-environment/
RUN cd /workspace \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo /workspace/aws/install
    
# installs PostreSQL on a local GitPod env (not container)
# command is adopted to Docker RUN command from Andrew's Brown week1.md instructions
RUN curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list \
    && sudo apt update \
    && sudo apt install -y postgresql-client-13 libpq-dev
