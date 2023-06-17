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
	curl

# install neovim
# RUN wget 'https://github.com/neovim/neovim/releases/download/stable/nvim-linux64.deb'
# RUN apt install ./nvim-linux64.deb

WORKDIR /root/.config
RUN git clone "https://github.com/Cow-Fu/kickstart.nvim.git"
RUN mv kickstart.nvim nvim

# install python lsp server
RUN nvim --headless -c "Lazy sync" -c "MasonInstall python-lsp-server" -c qall

# enable autocomplete of site packages
RUN sed -i 's/false/true/' /root/.local/share/nvim/mason/packages/python-lsp-server/venv/pyvenv.cfg

# install requirements
COPY ./requirements.txt /usr/src/requirements/
RUN pip3 install -r /usr/src/requirements/requirements.txt -U

WORKDIR /usr/src/app
