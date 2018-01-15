FROM stephank/archlinux:arm-latest

RUN pacman -Syy --noconfirm && pacman -S --noconfirm python2 python2-pip && rm /var/cache/pacman/pkg/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip2 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["python2"]
