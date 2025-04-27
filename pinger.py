#!/usr/bin/env python3
"""
Enhanced Pinger - A tool for monitoring connections and executing shell commands.

This script provides functionality to:
1. Ping hosts/URLs at regular intervals
2. Track response times and connection status
3. Keep connections alive by sending periodic requests
4. Execute shell commands based on ping results
5. Provide a menu-based interface for network tools
"""

import argparse
import datetime
import http.client
import os
import platform
import socket
import subprocess
import sys
import time
import urllib.parse
from typing import Dict, List, Optional, Union


class Pinger:
    """A class to ping hosts and keep connections alive with shell command execution."""

    def __init__(
        self,
        target: str,
        interval: float = 5.0,
        timeout: float = 2.0,
        max_failures: int = 3,
        verbose: bool = False,
        success_cmd: Optional[str] = None,
        failure_cmd: Optional[str] = None,
        success_script: Optional[str] = None,
        failure_script: Optional[str] = None,
        packet_size: Optional[int] = None,
    ):
        """
        Initialize the Pinger.

        Args:
            target: The host/URL to ping
            interval: Time between pings in seconds
            timeout: Timeout for each ping in seconds
            max_failures: Number of consecutive failures before alerting
            verbose: Whether to print detailed information
            success_cmd: Shell command to execute on successful ping
            failure_cmd: Shell command to execute on failed ping
            success_script: Shell script to execute on successful ping
            failure_script: Shell script to execute on failed ping
            packet_size: Size of ping packets (for system ping)
        """
        self.target = target
        self.interval = interval
        self.timeout = timeout
        self.max_failures = max_failures
        self.verbose = verbose
        self.success_cmd = success_cmd
        self.failure_cmd = failure_cmd
        self.success_script = success_script
        self.failure_script = failure_script
        self.packet_size = packet_size

        self.consecutive_failures = 0
        self.total_pings = 0
        self.successful_pings = 0
        self.response_times: List[float] = []

        # Colors for terminal output
        self.colors = {
            'red': '\033[31;1m',
            'green': '\033[32;1m',
            'yellow': '\033[33;1m',
            'blue': '\033[34;1m',
            'purple': '\033[35;1m',
            'cyan': '\033[36;1m',
            'white': '\033[37;1m',
            'reset': '\033[0m'
        }

        # Determine if target is a URL or IP address
        if "://" in target:
            self.is_url = True
            self.parsed_url = urllib.parse.urlparse(target)
            self.host = self.parsed_url.netloc
            self.path = self.parsed_url.path or "/"
            self.protocol = self.parsed_url.scheme
        else:
            self.is_url = False
            self.host = target

    def colored_print(self, text: str, color: str = 'reset', end: str = '\n') -> None:
        """Print colored text to the terminal."""
        if color in self.colors:
            print(f"{self.colors[color]}{text}{self.colors['reset']}", end=end)
        else:
            print(text, end=end)

    def execute_shell_command(self, command: str) -> str:
        """Execute a shell command and return the output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Command failed: {e.stderr}"

    def execute_shell_script(self, script_path: str) -> str:
        """Execute a shell script and return the output."""
        if not os.path.exists(script_path):
            return f"Script not found: {script_path}"

        try:
            # Make sure the script is executable
            os.chmod(script_path, 0o755)

            # Execute the script
            result = subprocess.run(
                f"bash {script_path}",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Script execution failed: {e.stderr}"

    def system_ping(self) -> Dict[str, Union[bool, float, str]]:
        """Use the system's ping command for more accurate results."""
        ping_cmd = "ping"
        ping_args = []

        # Add platform-specific arguments
        if platform.system().lower() == "windows":
            ping_args = ["-n", "1"]  # One ping on Windows
            if self.packet_size:
                ping_args.extend(["-l", str(self.packet_size)])
        else:  # Linux, macOS, etc.
            ping_args = ["-c", "1"]  # One ping on Unix-like systems
            if self.packet_size:
                ping_args.extend(["-s", str(self.packet_size)])

        # Add timeout
        if platform.system().lower() == "windows":
            ping_args.extend(["-w", str(int(self.timeout * 1000))])
        else:
            ping_args.extend(["-W", str(int(self.timeout))])

        # Add target
        ping_args.append(self.host)

        # Build the full command
        cmd = [ping_cmd] + ping_args

        start_time = time.time()
        success = False
        error_msg = ""
        response_time = 0.0

        try:
            result = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            success = result.returncode == 0

            if success:
                # Try to extract the actual ping time from output
                output = result.stdout
                if "time=" in output or "time<" in output:
                    for line in output.splitlines():
                        if "time=" in line or "time<" in line:
                            try:
                                time_part = line.split("time=")[1].split()[0] if "time=" in line else line.split("time<")[1].split()[0]
                                response_time = float(time_part.replace("ms", ""))
                            except (IndexError, ValueError):
                                pass
            else:
                error_msg = result.stderr if result.stderr else "Ping failed"
        except Exception as e:
            error_msg = str(e)

        # If we couldn't extract the time, calculate it from our timing
        if response_time == 0.0:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms

        return {
            "success": success,
            "response_time": response_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "error": error_msg
        }

    def ping_once(self) -> Dict[str, Union[bool, float, str]]:
        """
        Perform a single ping and return the result.

        Returns:
            Dictionary with ping results
        """
        # If packet size is specified, use system ping
        if self.packet_size is not None:
            return self.system_ping()

        start_time = time.time()
        success = False
        error_msg = ""

        try:
            if self.is_url:
                if self.protocol == "http" or self.protocol == "https":
                    conn_class = http.client.HTTPSConnection if self.protocol == "https" else http.client.HTTPConnection
                    conn = conn_class(self.host, timeout=self.timeout)
                    conn.request("HEAD", self.path)
                    response = conn.getresponse()
                    conn.close()
                    success = 200 <= response.status < 400
                    if not success:
                        error_msg = f"HTTP status: {response.status}"
                else:
                    error_msg = f"Unsupported protocol: {self.protocol}"
            else:
                # Simple socket ping for IP addresses
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(self.timeout)
                    sock.connect((self.host, 80))  # Default to port 80
                    success = True
        except Exception as e:
            error_msg = str(e)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms

        return {
            "success": success,
            "response_time": response_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "error": error_msg
        }

    def start(self, duration: Optional[int] = None) -> None:
        """
        Start pinging the target at the specified interval.

        Args:
            duration: Optional duration in seconds to run the pinger
        """
        self.colored_print(f"Starting pinger for {self.target}", "green")
        self.colored_print(f"Interval: {self.interval}s, Timeout: {self.timeout}s", "cyan")

        if self.packet_size:
            self.colored_print(f"Packet size: {self.packet_size} bytes", "cyan")

        if self.success_cmd:
            self.colored_print(f"Success command: {self.success_cmd}", "cyan")

        if self.failure_cmd:
            self.colored_print(f"Failure command: {self.failure_cmd}", "cyan")

        if self.success_script:
            self.colored_print(f"Success script: {self.success_script}", "cyan")

        if self.failure_script:
            self.colored_print(f"Failure script: {self.failure_script}", "cyan")

        self.colored_print("Press Ctrl+C to stop\n", "yellow")

        start_time = time.time()

        try:
            while True:
                result = self.ping_once()
                self.total_pings += 1

                if result["success"]:
                    self.successful_pings += 1
                    self.consecutive_failures = 0
                    self.response_times.append(result["response_time"])
                    status = "✓"
                    status_color = "green"

                    # Execute success commands/scripts if configured
                    if self.success_cmd:
                        cmd_output = self.execute_shell_command(self.success_cmd)
                        if self.verbose:
                            self.colored_print(f"Success command output: {cmd_output}", "blue")

                    if self.success_script:
                        script_output = self.execute_shell_script(self.success_script)
                        if self.verbose:
                            self.colored_print(f"Success script output: {script_output}", "blue")
                else:
                    self.consecutive_failures += 1
                    status = "✗"
                    status_color = "red"

                    # Execute failure commands/scripts if configured
                    if self.failure_cmd:
                        cmd_output = self.execute_shell_command(self.failure_cmd)
                        if self.verbose:
                            self.colored_print(f"Failure command output: {cmd_output}", "yellow")

                    if self.failure_script:
                        script_output = self.execute_shell_script(self.failure_script)
                        if self.verbose:
                            self.colored_print(f"Failure script output: {script_output}", "yellow")

                # Print result
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                if self.verbose or not result["success"]:
                    self.colored_print(f"[{timestamp}] {status} {self.target} - ", status_color, end="")
                    if result["success"]:
                        self.colored_print(f"{result['response_time']:.2f}ms", "green")
                    else:
                        self.colored_print(f"Failed: {result['error']}", "red")

                # Check for alert condition
                if self.consecutive_failures >= self.max_failures:
                    self.colored_print(f"\n⚠️  ALERT: {self.target} has failed {self.consecutive_failures} times in a row!", "red")
                    self.colored_print(f"Last error: {result['error']}\n", "red")

                # Check if we've reached the duration limit
                if duration and (time.time() - start_time) >= duration:
                    break

                # Wait for the next interval
                time.sleep(self.interval)

        except KeyboardInterrupt:
            self.colored_print("\nPinger stopped by user", "yellow")
        finally:
            self._print_summary()

    def _print_summary(self) -> None:
        """Print a summary of the pinging session."""
        success_rate = (self.successful_pings / self.total_pings * 100) if self.total_pings > 0 else 0
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        self.colored_print("\n--- Pinger Summary ---", "cyan")
        self.colored_print(f"Target: {self.target}", "white")
        self.colored_print(f"Total pings: {self.total_pings}", "white")

        if success_rate > 80:
            color = "green"
        elif success_rate > 50:
            color = "yellow"
        else:
            color = "red"

        self.colored_print(f"Successful: {self.successful_pings} ({success_rate:.1f}%)", color)
        self.colored_print(f"Failed: {self.total_pings - self.successful_pings}",
                          "red" if self.total_pings - self.successful_pings > 0 else "green")
        self.colored_print(f"Average response time: {avg_response:.2f}ms", "cyan")

        if self.response_times:
            min_time = min(self.response_times)
            max_time = max(self.response_times)
            self.colored_print(f"Min response time: {min_time:.2f}ms", "green")
            self.colored_print(f"Max response time: {max_time:.2f}ms",
                              "yellow" if max_time > 500 else "green")


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if platform.system().lower() == "windows" else 'clear')


def print_colored(text, color='reset'):
    """Print colored text to the terminal."""
    colors = {
        'red': '\033[31;1m',
        'green': '\033[32;1m',
        'yellow': '\033[33;1m',
        'blue': '\033[34;1m',
        'purple': '\033[35;1m',
        'cyan': '\033[36;1m',
        'white': '\033[37;1m',
        'reset': '\033[0m'
    }

    if color in colors:
        print(f"{colors[color]}{text}{colors['reset']}")
    else:
        print(text)


def show_menu():
    """Display the main menu and return the user's choice."""
    clear_screen()
    print_colored("=" * 60, "cyan")
    print_colored("                ENHANCED PINGER TOOL", "green")
    print_colored("=" * 60, "cyan")
    print_colored("1. Standard Ping (TCP/Socket)", "white")
    print_colored("2. HTTP/HTTPS Ping", "white")
    print_colored("3. System Ping with Custom Packet Size", "white")
    print_colored("4. YouTube Speed Test", "yellow")
    print_colored("5. Google DNS Speed Test", "yellow")
    print_colored("6. Custom Target with Shell Command", "purple")
    print_colored("7. Run Existing Shell Script", "purple")
    print_colored("8. Advanced Options", "red")
    print_colored("0. Exit", "red")
    print_colored("=" * 60, "cyan")

    try:
        choice = input("Enter your choice (0-8): ")
        return choice
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


def youtube_speed_test():
    """Run a speed test to YouTube servers."""
    clear_screen()
    print_colored("YouTube Speed Test", "green")
    print_colored("1. YouTube Server 1 (74.125.24.91)", "white")
    print_colored("2. YouTube Server 2 (172.217.194.113)", "white")
    print_colored("0. Back to main menu", "red")

    try:
        choice = input("Select a server (0-2): ")

        if choice == "1":
            return Pinger(
                target="74.125.24.91",
                interval=1.0,
                packet_size=9000,
                verbose=True
            )
        elif choice == "2":
            return Pinger(
                target="172.217.194.113",
                interval=1.0,
                packet_size=9000,
                verbose=True
            )
        else:
            return None
    except KeyboardInterrupt:
        return None


def google_dns_speed_test():
    """Run a speed test to Google DNS servers."""
    clear_screen()
    print_colored("Google DNS Speed Test", "green")
    print_colored("1. Standard Speed (Packet Size: 1000)", "white")
    print_colored("2. High Speed (Packet Size: 3000)", "white")
    print_colored("3. Maximum Speed (Packet Size: 9000)", "yellow")
    print_colored("0. Back to main menu", "red")

    try:
        choice = input("Select speed option (0-3): ")

        packet_sizes = {
            "1": 1000,
            "2": 3000,
            "3": 9000
        }

        if choice in packet_sizes:
            return Pinger(
                target="8.8.8.8",
                interval=1.0,
                packet_size=packet_sizes[choice],
                verbose=True
            )
        else:
            return None
    except KeyboardInterrupt:
        return None


def custom_target_with_command():
    """Configure a custom target with shell commands."""
    clear_screen()
    print_colored("Custom Target with Shell Commands", "green")

    try:
        target = input("Enter target host or URL: ")
        if not target:
            return None

        interval = input("Enter interval in seconds (default: 5): ")
        interval = float(interval) if interval else 5.0

        packet_size = input("Enter packet size (leave empty for default): ")
        packet_size = int(packet_size) if packet_size else None

        success_cmd = input("Enter command to run on successful ping (leave empty for none): ")
        success_cmd = success_cmd if success_cmd else None

        failure_cmd = input("Enter command to run on failed ping (leave empty for none): ")
        failure_cmd = failure_cmd if failure_cmd else None

        return Pinger(
            target=target,
            interval=interval,
            packet_size=packet_size,
            success_cmd=success_cmd,
            failure_cmd=failure_cmd,
            verbose=True
        )
    except KeyboardInterrupt:
        return None
    except ValueError as e:
        print_colored(f"Error: {e}", "red")
        input("Press Enter to continue...")
        return None


def run_shell_script():
    """Run an existing shell script."""
    clear_screen()
    print_colored("Run Existing Shell Script", "green")
    print_colored("Available scripts:", "cyan")

    # List available shell scripts
    scripts = [f for f in os.listdir() if f.endswith('.sh')]

    if not scripts:
        print_colored("No shell scripts found in the current directory.", "red")
        input("Press Enter to continue...")
        return None

    for i, script in enumerate(scripts, 1):
        print_colored(f"{i}. {script}", "white")

    print_colored("0. Back to main menu", "red")

    try:
        choice = input(f"Select a script (0-{len(scripts)}): ")

        if choice == "0" or not choice:
            return None

        try:
            script_index = int(choice) - 1
            if 0 <= script_index < len(scripts):
                script_path = scripts[script_index]

                # Execute the script directly
                subprocess.run(["bash", script_path], check=False)
                input("Press Enter to continue...")
                return None
            else:
                print_colored("Invalid selection.", "red")
                input("Press Enter to continue...")
                return None
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")
            input("Press Enter to continue...")
            return None
    except KeyboardInterrupt:
        return None


def advanced_options():
    """Configure advanced pinger options."""
    clear_screen()
    print_colored("Advanced Pinger Options", "red")

    try:
        target = input("Enter target host or URL: ")
        if not target:
            return None

        interval = input("Enter interval in seconds (default: 5): ")
        interval = float(interval) if interval else 5.0

        timeout = input("Enter timeout in seconds (default: 2): ")
        timeout = float(timeout) if timeout else 2.0

        max_failures = input("Enter max failures before alert (default: 3): ")
        max_failures = int(max_failures) if max_failures else 3

        packet_size = input("Enter packet size (leave empty for default): ")
        packet_size = int(packet_size) if packet_size else None

        success_script = input("Enter path to script to run on success (leave empty for none): ")
        success_script = success_script if success_script and os.path.exists(success_script) else None

        failure_script = input("Enter path to script to run on failure (leave empty for none): ")
        failure_script = failure_script if failure_script and os.path.exists(failure_script) else None

        duration = input("Enter duration in seconds (leave empty for indefinite): ")
        duration = int(duration) if duration else None

        return Pinger(
            target=target,
            interval=interval,
            timeout=timeout,
            max_failures=max_failures,
            packet_size=packet_size,
            success_script=success_script,
            failure_script=failure_script,
            verbose=True
        ), duration
    except KeyboardInterrupt:
        return None, None
    except ValueError as e:
        print_colored(f"Error: {e}", "red")
        input("Press Enter to continue...")
        return None, None


def parse_command_line():
    """Parse command line arguments and return a configured Pinger."""
    parser = argparse.ArgumentParser(description="Enhanced Pinger - Monitor connections and execute shell commands")
    parser.add_argument("target", nargs="?", help="Host or URL to ping")
    parser.add_argument("-i", "--interval", type=float, default=5.0, help="Interval between pings in seconds (default: 5)")
    parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout for each ping in seconds (default: 2)")
    parser.add_argument("-d", "--duration", type=int, help="Duration to run in seconds (default: indefinitely)")
    parser.add_argument("-f", "--max-failures", type=int, default=3, help="Number of consecutive failures before alerting (default: 3)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print all ping results, not just failures")
    parser.add_argument("-p", "--packet-size", type=int, help="Size of ping packets in bytes")
    parser.add_argument("-s", "--success-cmd", help="Shell command to execute on successful ping")
    parser.add_argument("-F", "--failure-cmd", help="Shell command to execute on failed ping")
    parser.add_argument("-S", "--success-script", help="Shell script to execute on successful ping")
    parser.add_argument("-X", "--failure-script", help="Shell script to execute on failed ping")
    parser.add_argument("-m", "--menu", action="store_true", help="Show interactive menu")

    args = parser.parse_args()

    # If menu flag is set or no target is provided, return None to show the menu
    if args.menu or not args.target:
        return None, None

    pinger = Pinger(
        target=args.target,
        interval=args.interval,
        timeout=args.timeout,
        max_failures=args.max_failures,
        verbose=args.verbose,
        packet_size=args.packet_size,
        success_cmd=args.success_cmd,
        failure_cmd=args.failure_cmd,
        success_script=args.success_script,
        failure_script=args.failure_script
    )

    return pinger, args.duration


def main():
    """Main function to run the pinger."""
    # Try to parse command line arguments first
    pinger, duration = parse_command_line()

    # If no pinger was created from command line args, show the menu
    if not pinger:
        while True:
            choice = show_menu()

            if choice == "0":
                print_colored("Goodbye!", "green")
                break
            elif choice == "1":
                # Standard Ping
                target = input("Enter target host or IP: ")
                if target:
                    pinger = Pinger(target=target, verbose=True)
                    pinger.start()
            elif choice == "2":
                # HTTP/HTTPS Ping
                target = input("Enter URL (including http:// or https://): ")
                if target:
                    pinger = Pinger(target=target, verbose=True)
                    pinger.start()
            elif choice == "3":
                # System Ping with Custom Packet Size
                target = input("Enter target host or IP: ")
                if target:
                    size = input("Enter packet size in bytes (default: 56): ")
                    size = int(size) if size else 56
                    pinger = Pinger(target=target, packet_size=size, verbose=True)
                    pinger.start()
            elif choice == "4":
                # YouTube Speed Test
                pinger = youtube_speed_test()
                if pinger:
                    pinger.start()
            elif choice == "5":
                # Google DNS Speed Test
                pinger = google_dns_speed_test()
                if pinger:
                    pinger.start()
            elif choice == "6":
                # Custom Target with Shell Command
                pinger = custom_target_with_command()
                if pinger:
                    pinger.start()
            elif choice == "7":
                # Run Existing Shell Script
                run_shell_script()
            elif choice == "8":
                # Advanced Options
                pinger, duration = advanced_options()
                if pinger:
                    pinger.start(duration=duration)
            else:
                print_colored("Invalid choice. Please try again.", "red")
                time.sleep(1)
    else:
        # Run the pinger configured from command line args
        pinger.start(duration=duration)


if __name__ == "__main__":
    main()