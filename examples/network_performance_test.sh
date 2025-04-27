#!/bin/bash
# Example script to test network performance with different packet sizes

# Define colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
TARGET="8.8.8.8"
DURATION=10  # seconds per test
OUTPUT_FILE="network_performance_results.csv"

# Create or clear the output file
echo "Packet Size (bytes),Average Response Time (ms),Min Response Time (ms),Max Response Time (ms),Success Rate (%)" > $OUTPUT_FILE

# Function to extract results from pinger output
extract_results() {
    local output=$1
    local avg_time=$(echo "$output" | grep "Average response time" | awk '{print $4}' | sed 's/ms//')
    local min_time=$(echo "$output" | grep "Min response time" | awk '{print $4}' | sed 's/ms//')
    local max_time=$(echo "$output" | grep "Max response time" | awk '{print $4}' | sed 's/ms//')
    local success_rate=$(echo "$output" | grep "Successful" | awk '{print $3}' | sed 's/(//' | sed 's/%)//')
    
    echo "$packet_size,$avg_time,$min_time,$max_time,$success_rate" >> $OUTPUT_FILE
}

# Run tests with different packet sizes
packet_sizes=(56 512 1024 2048 4096 8192)

for packet_size in "${packet_sizes[@]}"; do
    echo -e "${BLUE}Running test with packet size: ${packet_size} bytes${NC}"
    echo -e "${YELLOW}Test duration: ${DURATION} seconds${NC}"
    
    # Run the pinger with the current packet size
    result=$(python ../pinger.py $TARGET -v -p $packet_size -d $DURATION)
    
    # Extract and save the results
    extract_results "$result"
    
    echo -e "${GREEN}Test complete for packet size ${packet_size}${NC}"
    echo "----------------------------------------"
done

echo -e "${GREEN}All tests completed!${NC}"
echo -e "Results saved to ${OUTPUT_FILE}"
echo -e "${YELLOW}You can now analyze the results or create a graph from the CSV file${NC}"
