#!/bin/bash
# Example script to monitor a critical service and take action when it fails

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_URL="https://example.com"
LOG_FILE="service_monitor.log"
ALERT_EMAIL="admin@example.com"
RETRY_COUNT=3

echo -e "${YELLOW}Starting service monitoring for ${SERVICE_URL}${NC}"
echo "$(date) - Monitoring started" >> $LOG_FILE

# Function to send alert
send_alert() {
    echo -e "${RED}Service is DOWN! Sending alert...${NC}"
    echo "$(date) - SERVICE DOWN ALERT: ${SERVICE_URL} is not responding" >> $LOG_FILE
    
    # Send email alert (uncomment and configure for your system)
    # echo "Service ${SERVICE_URL} is DOWN!" | mail -s "SERVICE DOWN ALERT" $ALERT_EMAIL
    
    # You could also add other notification methods here:
    # - Slack webhook
    # - SMS notification
    # - Push notification
}

# Function to attempt service restart
attempt_restart() {
    echo -e "${YELLOW}Attempting to restart the service...${NC}"
    echo "$(date) - Attempting service restart" >> $LOG_FILE
    
    # Add your restart command here, for example:
    # ssh user@server "systemctl restart my-service"
    
    echo "Restart command executed, waiting to verify..."
    sleep 10
}

# Use the pinger tool to monitor the service
# If it fails, the failure command will be executed
python ../pinger.py $SERVICE_URL -i 30 -t 5 -f $RETRY_COUNT -v \
    -F "bash -c 'echo \"Service failed, taking action\"; $(declare -f send_alert); send_alert; $(declare -f attempt_restart); attempt_restart'" \
    -s "echo \"$(date) - Service is UP and responding normally\" >> $LOG_FILE"

echo -e "${GREEN}Monitoring complete${NC}"
