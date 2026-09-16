#!/bin/bash
sudo cp *.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wifi.service find_device.service remote.service button_scan.service
sudo systemctl start wifi.service find_device.service remote.service button_scan.service 
