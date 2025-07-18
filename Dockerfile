FROM alpine

# install dependencies
RUN apk add --update --no-cache fish \
  git \
  openssh \
  unzip \
  ffmpeg \
  ripgrep \
  neovim \
  python3 \
  python3-dev \
  py3-pip \
  binutils \
  gcc \
  g++  \
  make \
  curl \
  fzf
# RUN dnf install -y fish git ffmpeg ripgrep python3 pip3 gcc g++ make curl python3-dev
# RUN dnf clean all

# install requirements
COPY ./requirements.txt /usr/src/requirements/
# RUN pip install -r /usr/src/requirements/requirements.txt -U --break-system-packages
RUN cat /usr/src/requirements.txt | cut -d = -f1 | xargs -I{} pip install {} --break-system-packages


# configure neovim
WORKDIR /root/.config
RUN git clone "https://github.com/Cow-Fu/.nvim.git"
RUN mv .nvim nvim
RUN nvim --headless -c "Lazy sync" -c "MasonInstall python-lsp-server" -c "TSUpdate" -c qall
# enable autocomplete of site packages
RUN sed -i 's/false/true/' /root/.local/share/nvim/mason/packages/python-lsp-server/venv/pyvenv.cfg

# install python lsp server
WORKDIR /usr/src/app
CMD ["python3", "cowbot.py"]
