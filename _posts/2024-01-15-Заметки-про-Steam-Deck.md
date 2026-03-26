---
title: "Заметки про steam deck"
author: kright
permalink: /2024/01/15/zametki-pro-steam-deck/
redirect_from:
  - /2024/01/15/%D0%97%D0%B0%D0%BC%D0%B5%D1%82%D0%BA%D0%B8-%D0%BF%D1%80%D0%BE-Steam-Deck.html
---
Внутри arch linux, пакетный менеджер - pacman

Вначале надо будет придумать и установить свой пароль для sudo. Как сделал я уже забыл.

```sh
sudo steamos-readonly disable
sudo steamos-readonly enable
```

Если я правильно понимаю, после обновления ОС все эти изменения пропадут (кроме того что в home)

Для установки пакетов недостаточно выключить readonly:

```sh
sudo pacman-key --init
sudo pacman -S archlinux-keyring 
sudo pacman-key --populate archlinux
```

но к сожалению у меня не заработало, пришлось отключить проверку подписи файлов. В /etc/pacman.conf:
```
SigLevel = TrustAll
#SigLevel = Required Databaseoptional
```

## SSH

генерация ssh ключа
```
ssh-keygen =t ecdsa -b 521
```
либо более старый подход типа 
```
ssh-keygen -t rsa -b 4096
```
подробнее [тут](https://www.ssh.com/academy/ssh/keygen#choosing-an-algorithm-and-key-size)

ssh сервер уже установлен, полезные команды:

```sh
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl restart sshd
```

ключи добавить в ~/.ssh/authorized_keys

узнать адрес:
```
ip addr
```

```
ssh deck@192.168.*.*
```

