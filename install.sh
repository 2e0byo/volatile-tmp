#!/bin/bash
TARGET=~/.local/bin
mkdir -p $TARGET
ln -rs ./volatile-tmp.py $TARGET/
chmod +x $TARGET/volatile-tmp.py
mkdir -p ~/.config/systemd/user/
rm ./systemd/volatile-tmp.service
cat<<EOF >./systemd/volatile-tmp.service
[Unit]
Description=Cleanup volatile tmp dir

[Service]
ExecStart=$HOME/.local/bin/volatile-tmp.py


[Install]
WantedBy=default.target
EOF
ln -rs ./systemd/volatile-tmp.service ~/.config/systemd/user/
ln -rs ./systemd/volatile-tmp.timer ~/.config/systemd/user/
systemctl --user enable volatile-tmp.service
systemctl --user enable volatile-tmp.timer
systemctl --user start volatile-tmp.timer

if [[ !  -d ~/volatile-tmp ]]; then
    cp -r template ~/volatile-tmp
fi
