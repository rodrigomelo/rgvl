#!/bin/bash
# RGVL Services Monitor
# Checks if services are running and restarts if needed

LOG_FILE="/tmp/rgvl-monitor.log"

check_service() {
    local name=$1
    local port=$2
    local url="http://localhost:${port}"
    
    if curl -s --max-time 5 "${url}" > /dev/null 2>&1; then
        echo "$(date): ${name} is running on port ${port}" >> "${LOG_FILE}"
        return 0
    else
        echo "$(date): ${name} is NOT running on port ${port}, restarting..." >> "${LOG_FILE}"
        return 1
    fi
}

# Check API
if ! check_service "API" "5003"; then
    launchctl unload ~/Library/LaunchAgents/com.rgvl.api.plist 2>/dev/null
    sleep 1
    launchctl load ~/Library/LaunchAgents/com.rgvl.api.plist 2>/dev/null
    sleep 2
fi

# Check Web (runs on 5004, not 5002)
if ! check_service "Web" "5004"; then
    launchctl unload ~/Library/LaunchAgents/com.rgvl.web.plist 2>/dev/null
    sleep 1
    launchctl load ~/Library/LaunchAgents/com.rgvl.web.plist 2>/dev/null
    sleep 2
fi

echo "$(date): Monitor check completed" >> "${LOG_FILE}"
