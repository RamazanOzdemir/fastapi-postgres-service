FROM mcr.microsoft.com/devcontainers/base:jammy

# User account with sudo privileges
RUN deluser --remove-home vscode && \
useradd -mU --shell /bin/bash --uid 1000 appuser && usermod -aG sudo appuser && \
echo "appuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER appuser

# Shell customization
RUN touch "/home/appuser/.hushlogin"
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PATH="/workspace/.devcontainer/bin:$PATH"

RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" && \
sudo mkdir /commandhistory && sudo touch /commandhistory/.bash_history && sudo chown -R appuser:appuser /commandhistory && \
echo $SNIPPET >> "/home/appuser/.bashrc"

# Base development dependencies
RUN sudo apt-get update && sudo apt-get install -y build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git libpq-dev ca-certificates \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev


# Install Starship (installing via the website .sh file had some permission errors, so doing it manually)
RUN curl -fsSL https://github.com/starship/starship/releases/latest/download/starship-x86_64-unknown-linux-musl.tar.gz | \
    sudo tar xzv -C /usr/local/bin && \
    sudo chmod +x /usr/local/bin/starship && \
    mkdir -p /home/appuser/.config && \
    sudo chown -R appuser:appuser /home/appuser/.config
COPY starship.toml /home/appuser/.config/starship.toml
RUN echo 'eval "$(starship init bash)"' >> /home/appuser/.bashrc


# Postgres tooling
RUN sudo install -d /usr/share/postgresql-common/pgdg && \
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt jammy-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
sudo apt update && sudo apt install -y postgresql-client-16


# Docker CLI
RUN sudo install -m 0755 -d /etc/apt/keyrings && \
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
sudo chmod a+r /etc/apt/keyrings/docker.asc && \
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && \
sudo apt-get update && sudo apt-get install -y docker-ce-cli docker-compose-plugin && \
sudo groupadd docker && sudo usermod -aG docker appuser

# Playwright
RUN sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libatspi2.0-0 libxdamage1 libgbm1 \
libcairo2 libpango-1.0-0 libasound2 libxcursor1 libgtk-3-0 libpangocairo-1.0-0 libcairo-gobject2 libgdk-pixbuf-2.0-0

# Python configuration
ENV PYTHONUNBUFFERED 1
ENV PYTHON_DEFAULT_VERSION=3.14.0
ENV UV_LINK_MODE=copy
RUN curl -LsSf https://astral.sh/uv/0.9.10/install.sh | sh
RUN uv python install --default "$PYTHON_DEFAULT_VERSION"


# Add /workspace/backend/.venv/bin to PATH
RUN echo 'export PATH="/workspace/backend/.venv/bin:$PATH"' >> "/home/appuser/.bashrc"
# Add git auto-completion to the end of bash config
RUN echo "source /usr/share/bash-completion/completions/git" >> "/home/appuser/.bashrc"