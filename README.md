# Enhanced Pinger Tool

A powerful network monitoring and connection management tool that combines Python's networking capabilities with shell script execution.

![Enhanced Pinger Tool](https://img.shields.io/badge/Enhanced-Pinger-blue)
![Python](https://img.shields.io/badge/Python-3.6+-green)
![Shell](https://img.shields.io/badge/Shell-Integration-orange)

## Features

### 🌐 Multiple Ping Methods
- TCP/Socket-based pinging
- HTTP/HTTPS endpoint monitoring
- System ping with configurable packet sizes

### 🔄 Shell Integration
- Execute shell commands on successful pings
- Execute shell commands on failed pings
- Run existing shell scripts based on ping results
- Direct integration with your existing shell scripts

### 🖥️ User-Friendly Interface
- Interactive menu system with colorful output
- Command-line interface for scripting and automation
- Detailed statistics and reporting

### ⚙️ Advanced Options
- Configurable intervals, timeouts, and alert thresholds
- Duration-limited monitoring sessions
- Custom packet sizes for performance testing

### 🚀 Pre-configured Tests
- YouTube server speed tests
- Google DNS speed tests
- Customizable targets and commands

## Installation

No installation required! Just clone the repository and run the Python script.

```bash
git clone https://github.com/yourusername/enhanced-pinger.git
cd enhanced-pinger
```

## Requirements

- Python 3.6 or higher
- Standard Python libraries (all included in the script)
- Bash shell (for shell script integration)

## Usage

### Menu Interface

The easiest way to use the tool is through its interactive menu:

```bash
python pinger.py -m
```

This will display a menu with various options:

```
============================================================
                ENHANCED PINGER TOOL
============================================================
1. Standard Ping (TCP/Socket)
2. HTTP/HTTPS Ping
3. System Ping with Custom Packet Size
4. YouTube Speed Test
5. Google DNS Speed Test
6. Custom Target with Shell Command
7. Run Existing Shell Script
8. Advanced Options
0. Exit
============================================================
```

### Command Line Interface

For automation and scripting, use the command line interface:

```bash
python pinger.py [target] [options]
```

#### Basic Examples:

```bash
# Simple ping to Google DNS
python pinger.py 8.8.8.8

# HTTP ping to a website with verbose output
python pinger.py https://example.com -v

# Ping with custom packet size
python pinger.py 8.8.8.8 -p 1000

# Ping for a specific duration (in seconds)
python pinger.py 8.8.8.8 -d 60
```

#### Advanced Examples:

```bash
# Execute a command on successful pings
python pinger.py 8.8.8.8 -s "echo 'Connection OK' >> log.txt"

# Execute a command on failed pings
python pinger.py 8.8.8.8 -F "echo 'Connection failed' >> log.txt"

# Execute a shell script on successful pings
python pinger.py 8.8.8.8 -S "/path/to/success.sh"

# Execute a shell script on failed pings
python pinger.py 8.8.8.8 -X "/path/to/failure.sh"

# Combine multiple options
python pinger.py 8.8.8.8 -v -i 10 -t 5 -f 2 -p 1500 -d 300
```

### Command Line Options

| Option | Long Option | Description |
|--------|-------------|-------------|
| `-i` | `--interval` | Interval between pings in seconds (default: 5) |
| `-t` | `--timeout` | Timeout for each ping in seconds (default: 2) |
| `-d` | `--duration` | Duration to run in seconds (default: indefinitely) |
| `-f` | `--max-failures` | Number of consecutive failures before alerting (default: 3) |
| `-v` | `--verbose` | Print all ping results, not just failures |
| `-p` | `--packet-size` | Size of ping packets in bytes |
| `-s` | `--success-cmd` | Shell command to execute on successful ping |
| `-F` | `--failure-cmd` | Shell command to execute on failed ping |
| `-S` | `--success-script` | Shell script to execute on successful ping |
| `-X` | `--failure-script` | Shell script to execute on failed ping |
| `-m` | `--menu` | Show interactive menu |

## Shell Script Integration

The tool can work with your existing shell scripts. Place your `.sh` files in the same directory as `pinger.py`, and you can:

1. Run them directly from the menu (Option 7)
2. Execute them on successful or failed pings using the `-S` and `-X` options

## Example Output

```
Starting pinger for 8.8.8.8
Interval: 5.0s, Timeout: 2.0s
Press Ctrl+C to stop

[11:02:41] ✓ 8.8.8.8 - 6.59ms
[11:02:46] ✓ 8.8.8.8 - 5.02ms

--- Pinger Summary ---
Target: 8.8.8.8
Total pings: 2
Successful: 2 (100.0%)
Failed: 0
Average response time: 5.81ms
Min response time: 5.02ms
Max response time: 6.59ms
```

## Use Cases

### Network Monitoring
Monitor critical services and get alerted when they go down.

```bash
python pinger.py your-critical-server.com -v -F "notify-send 'Server Down!'"
```

### Keep-Alive Connections
Prevent session timeouts by sending periodic requests.

```bash
python pinger.py https://your-service.com/api -i 60
```

### Network Performance Testing
Test network performance with different packet sizes.

```bash
python pinger.py 8.8.8.8 -p 9000 -v
```

### Automated Response
Execute scripts to restart services when they fail.

```bash
python pinger.py your-service.com -X "/path/to/restart_service.sh"
```

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the need to combine Python's networking capabilities with shell script automation
- Thanks to all contributors and users of this tool
