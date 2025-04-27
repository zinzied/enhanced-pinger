#!/bin/bash
# Example script for continuous monitoring of multiple targets

# Define colors for output
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
TARGETS_FILE="targets.txt"
LOG_DIR="logs"
INTERVAL=300  # 5 minutes between checks

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR

# Function to check if a target is responding
check_target() {
    local target=$1
    local log_file="${LOG_DIR}/$(echo $target | tr '/:.' '_').log"
    
    echo -e "${CYAN}Checking target: ${target}${NC}"
    
    # Run a quick ping test
    python ../pinger.py $target -d 5 -v > /tmp/ping_result.txt
    
    # Check if the ping was successful
    if grep -q "Successful: 0" /tmp/ping_result.txt; then
        echo -e "${RED}Target ${target} is DOWN${NC}"
        echo "$(date) - DOWN" >> $log_file
        return 1
    else
        echo -e "${GREEN}Target ${target} is UP${NC}"
        echo "$(date) - UP" >> $log_file
        return 0
    fi
}

# Main monitoring loop
echo -e "${YELLOW}Starting continuous monitoring...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"

while true; do
    echo "============================================"
    echo -e "${CYAN}Starting monitoring cycle at $(date)${NC}"
    
    # Check if targets file exists
    if [ ! -f "$TARGETS_FILE" ]; then
        echo -e "${RED}Targets file not found: ${TARGETS_FILE}${NC}"
        echo -e "${YELLOW}Creating example targets file...${NC}"
        echo "8.8.8.8" > $TARGETS_FILE
        echo "1.1.1.1" >> $TARGETS_FILE
        echo "https://example.com" >> $TARGETS_FILE
    fi
    
    # Read targets from file and check each one
    while IFS= read -r target; do
        # Skip empty lines and comments
        if [[ -z "$target" || "$target" == \#* ]]; then
            continue
        fi
        
        check_target "$target"
        sleep 2  # Brief pause between targets
    done < "$TARGETS_FILE"
    
    echo -e "${CYAN}Monitoring cycle completed at $(date)${NC}"
    echo -e "${YELLOW}Next check in ${INTERVAL} seconds...${NC}"
    echo "============================================"
    
    # Wait for the next cycle
    sleep $INTERVAL
done
