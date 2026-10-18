#!/bin/bash
ROJO="\e[1;31m"
VERDE="\e[1;32m"
CIAN="\e[1;36m"
FIN="\e[0m" 

echo -e "Installing ${CIAN}PomoPomo (⁠n__n⁠)...${FIN}"


sleep 0.2 && echo -ne "${ROJO}|---------------|\r${FIN}"
sleep 0.4 && echo -ne "\e[2K${ROJO}=--------------\r${FIN}"
sleep 0.3 && echo -ne "\e[2K${ROJO}==-------------\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}===------------\r${FIN}"
sleep 0.2 && echo -ne "\e[2K${ROJO}====-----------\r${FIN}"
sleep 0.2 && echo -ne "\e[2K${ROJO}=====----------\r${FIN}"
sleep 0.2 && echo -ne "\e[2K${ROJO}======---------\r${FIN}"
sleep 0.4 && echo -ne "\e[2K${ROJO}=======--------\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}========-------\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}=========------\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}==========-----\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}===========----\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}============---\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}=============--\r${FIN}"
sleep 0.1 && echo -ne "\e[2K${ROJO}==============-\r${FIN}"

sleep 0.1 && echo -e "\e[2K${VERDE}=============== ✔\n${FIN}"

chmod +x main.py

mkdir -p ~/.local/bin

ln -sf "$(pwd)/main.py" ~/.local/bin/pomopomo

echo -e "${VERDE}Installation complete!${FIN} You can now open a new terminal and simply type ${CIAN}'pomopomo'${FIN} :D."
