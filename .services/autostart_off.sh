#!/bin/bash

# Aranea Server Autostart Disable Script
# This script disables the Aranea server service autostart and stops the service

echo "Disabling Aranea server autostart..."

# Stop the service if it's running
if sudo systemctl is-active --quiet aranea-server.service; then
    echo "Stopping aranea-server service..."
    sudo systemctl stop aranea-server.service
else
    echo "Service is not running."
fi

# Disable the service for autostart
echo "Disabling aranea-server service..."
sudo systemctl disable aranea-server.service

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Show status
echo "Service status:"
sudo systemctl status aranea-server.service --no-pager -l

echo "Autostart disabled successfully!"
echo "The Aranea server will no longer start automatically on boot."
echo "To start it manually, run: sudo systemctl start aranea-server.service" 