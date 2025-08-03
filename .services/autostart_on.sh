#!/bin/bash

# Aranea Server Autostart Enable Script
# This script enables the Aranea server service to start automatically on boot

echo "Enabling Aranea server autostart..."

# Copy service file to systemd directory if it doesn't exist
if [ ! -f /etc/systemd/system/aranea-server.service ]; then
    echo "Copying service file to /etc/systemd/system/"
    sudo cp "$(dirname "$0")/aranea-server.service" /etc/systemd/system/
    sudo chmod 644 /etc/systemd/system/aranea-server.service
fi

# Reload systemd daemon to recognize the service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service for autostart
echo "Enabling aranea-server service..."
sudo systemctl enable aranea-server.service

# Start the service if it's not already running
if ! sudo systemctl is-active --quiet aranea-server.service; then
    echo "Starting aranea-server service..."
    sudo systemctl start aranea-server.service
else
    echo "Service is already running."
fi

# Show status
echo "Service status:"
sudo systemctl status aranea-server.service --no-pager -l

echo "Autostart enabled successfully!"
echo "The Aranea server will now start automatically on boot." 