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
	py3-pip \
	binutils \
	gcc \
	g++  \
	make \
	curl \
	tzdata \
	sqlite

# configure neovim
WORKDIR /root/.config
RUN git clone "https://github.com/Cow-Fu/.nvim.git"

# install python lsp server
RUN nvim --headless -c "Lazy sync" -c "MasonInstall python-lsp-server" -c qall

# enable autocomplete of site packages
RUN sed -i 's/false/true/' /root/.local/share/nvim/mason/packages/python-lsp-server/venv/pyvenv.cfg

# install requirements
COPY ./requirements.txt /usr/src/requirements/
RUN pip3 install -r /usr/src/requirements/requirements.txt -U

WORKDIR /usr/src/app
CMD ['python3', 'cowbot.py']
