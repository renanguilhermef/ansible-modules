#!/bin/bash
set -e

install_path=/usr/local/bin/entrocim_healthchecker
entrocim_healthchecker=/app/hepta/entrocim_healthchecker

if systemctl check entrocim_healthchecker; then
    echo "Stopping EntroCIM Healthchecker"
    systemctl stop entrocim_healthchecker
fi

echo "Installing EntroCIM healthchecker binary"

cp $entrocim_healthchecker $install_path
chmod +x $install_path 
chown entrocim:entrocim $install_path

echo "Creating EntroCIM Healthchecker service"
echo '[Unit]
Description=EntroCIM Healthchecker service
After=entrocim.service
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=10
User=entrocim
ExecStart=/usr/local/bin/entrocim_healthchecker

[Install]
WantedBy=multi-user.target' > /etc/systemd/system/entrocim_healthchecker.service

systemctl enable entrocim_healthchecker.service
systemctl start entrocim_healthchecker.service
