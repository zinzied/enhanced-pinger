#!/bin/bash
# Simple installation script for the Enhanced Pinger Tool

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}      Enhanced Pinger Tool Installation          ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}Found: ${python_version}${NC}"
else
    echo -e "${RED}Python 3 not found. Please install Python 3.6 or higher.${NC}"
    exit 1
fi

# Make scripts executable
echo -e "${YELLOW}Making scripts executable...${NC}"
chmod +x pinger.py
if [ -d "examples" ]; then
    chmod +x examples/*.sh
    echo -e "${GREEN}Example scripts are now executable${NC}"
fi

# Create examples directory if it doesn't exist
if [ ! -d "examples" ]; then
    echo -e "${YELLOW}Creating examples directory...${NC}"
    mkdir -p examples
    echo -e "${GREEN}Examples directory created${NC}"
fi

# Create a simple alias for easier access (optional)
echo -e "${YELLOW}Would you like to create an alias for the pinger tool? (y/n)${NC}"
read -r create_alias

if [[ "$create_alias" == "y" || "$create_alias" == "Y" ]]; then
    echo -e "${YELLOW}Adding alias to your shell configuration...${NC}"
    
    # Determine shell configuration file
    shell_config=""
    if [ -n "$BASH_VERSION" ]; then
        if [ -f "$HOME/.bashrc" ]; then
            shell_config="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            shell_config="$HOME/.bash_profile"
        fi
    elif [ -n "$ZSH_VERSION" ]; then
        shell_config="$HOME/.zshrc"
    fi
    
    if [ -n "$shell_config" ]; then
        # Add the alias
        echo "# Enhanced Pinger Tool alias" >> "$shell_config"
        echo "alias pinger='python3 $(pwd)/pinger.py'" >> "$shell_config"
        echo -e "${GREEN}Alias added to ${shell_config}${NC}"
        echo -e "${YELLOW}Please restart your terminal or run 'source ${shell_config}' to use the alias${NC}"
    else
        echo -e "${RED}Could not determine shell configuration file. Please add the alias manually:${NC}"
        echo -e "${YELLOW}alias pinger='python3 $(pwd)/pinger.py'${NC}"
    fi
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${YELLOW}You can now use the Enhanced Pinger Tool:${NC}"
echo -e "${BLUE}  - Interactive menu: ${NC}python3 pinger.py -m"
echo -e "${BLUE}  - Command line: ${NC}python3 pinger.py [target] [options]"
echo -e "${BLUE}  - Example scripts: ${NC}cd examples && ./continuous_monitoring.sh"
echo -e "${BLUE}==================================================${NC}"
