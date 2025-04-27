#!/usr/bin/env python3
"""
Enhanced SpeedUp Tool - A network speed optimization and testing tool

This script provides a modern, efficient interface for:
1. Testing and optimizing network connections
2. Running speed tests to various servers
3. Integrating with the enhanced pinger tool
4. Providing a user-friendly interface
"""

import argparse
import os
import platform
import subprocess
import sys
import time
from typing import Dict, List, Optional, Union

# Import the Pinger class from pinger.py
try:
    from pinger import Pinger, clear_screen, print_colored
except ImportError:
    print("Error: pinger.py not found in the current directory.")
    print("Please make sure pinger.py is in the same directory as this script.")
    sys.exit(1)


class SpeedUp:
    """Main class for the SpeedUp tool."""

    def __init__(self):
        """Initialize the SpeedUp tool."""
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
        
        # Define speed test targets
        self.targets = {
            'google_dns': '8.8.8.8',
            'cloudflare_dns': '1.1.1.1',
            'google_browser': '216.239.38.120',
            'youtube_1': '74.125.24.91',
            'youtube_2': '172.217.194.113'
        }
        
        # Define packet sizes for different speed levels
        self.packet_sizes = {
            'low': 1000,
            'medium': 3000,
            'high': 9000
        }

    def show_loading_animation(self):
        """Show a loading animation."""
        clear_screen()
        print_colored("Loading...", "green")
        
        for i in range(0, 101, 20):
            clear_screen()
            if i < 50:
                print_colored(f"Loading {i}%", "red")
            elif i < 80:
                print_colored(f"Loading {i}%", "yellow")
            else:
                print_colored(f"Loading {i}%", "green")
            
            # Adjust sleep time to make loading faster
            time.sleep(0.5)
    
    def show_header(self):
        """Show the tool header."""
        clear_screen()
        
        # Check if figlet is installed
        try:
            subprocess.run(["figlet", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            has_figlet = True
        except FileNotFoundError:
            has_figlet = False
        
        if has_figlet:
            subprocess.run(["figlet", "SpeedUp"], check=False)
            subprocess.run(["figlet", "Tool"], check=False)
        else:
            print_colored("==========================", "red")
            print_colored("      SPEEDUP TOOL        ", "green")
            print_colored("==========================", "red")
        
        print_colored("Network Speed Optimization", "cyan")
        print_colored("==========================", "red")
        print()
    
    def show_menu(self):
        """Show the main menu and get user choice."""
        self.show_header()
        
        print_colored("Choose an option:", "green")
        print()
        print_colored("SPEED TESTS", "yellow")
        print_colored("1. Speed Test v1 (Medium Speed)", "cyan")
        print_colored("2. Speed Test v2 (Maximum Speed)", "green")
        print_colored("3. Full Speed Test Suite", "yellow")
        print_colored("4. Secret Codes", "white")
        print()
        print_colored("SPECIALIZED TESTS", "yellow")
        print_colored("5. Browser Speed Test", "red")
        print_colored("6. YouTube Speed Test", "red")
        print_colored("7. Custom Speed Test", "purple")
        print()
        print_colored("TOOLS", "yellow")
        print_colored("8. Network Information", "blue")
        print_colored("9. Advanced Pinger Options", "blue")
        print_colored("0. Exit", "red")
        print()
        
        try:
            choice = input("Enter your choice (0-9): ")
            return choice
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    
    def run_speed_test(self, target: str, packet_size: int, duration: int = 30):
        """Run a speed test using the Pinger class."""
        clear_screen()
        print_colored(f"Running speed test to {target} with packet size {packet_size}...", "green")
        print_colored("Press Ctrl+C to stop the test early", "yellow")
        print()
        
        # Create and run a Pinger instance
        pinger = Pinger(
            target=target,
            interval=1.0,  # 1 second interval for more responsive tests
            packet_size=packet_size,
            verbose=True
        )
        
        pinger.start(duration=duration)
    
    def run_secret_codes(self):
        """Run the secret codes menu."""
        clear_screen()
        
        # Check if figlet is installed
        try:
            subprocess.run(["figlet", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            has_figlet = True
        except FileNotFoundError:
            has_figlet = False
        
        if has_figlet:
            subprocess.run(["figlet", "Secret"], check=False)
            subprocess.run(["figlet", "Codes"], check=False)
        else:
            print_colored("==========================", "red")
            print_colored("     SECRET CODES         ", "red")
            print_colored("==========================", "red")
        
        try:
            code = input("Enter code: ")
            
            if code == "READIP":
                clear_screen()
                print_colored("Network Interfaces:", "green")
                
                # Use ipconfig on Windows, ifconfig on others
                if platform.system().lower() == "windows":
                    subprocess.run(["ipconfig"], check=False)
                else:
                    subprocess.run(["ifconfig"], check=False)
                
                input("\nPress Enter to continue...")
            
            elif code == "1IP":
                self.run_speed_test(self.targets['cloudflare_dns'], self.packet_sizes['high'])
            
            elif code == "1IP2":
                self.run_speed_test(self.targets['cloudflare_dns'], self.packet_sizes['low'])
            
            elif code == "SUS":
                clear_screen()
                
                if has_figlet:
                    subprocess.run(["figlet", "AMOGUS!"], check=False)
                else:
                    print_colored("AMOGUS!", "red")
                
                print_colored("Attention Everyone!", "red")
                time.sleep(1)
                print_colored("He is SUS!!!!", "red")
                time.sleep(2)
                
                input("\nPress Enter to continue...")
            
            else:
                print_colored(f"Unknown code: {code}", "red")
                time.sleep(2)
        
        except KeyboardInterrupt:
            pass
    
    def run_youtube_speed_test(self):
        """Run YouTube speed test menu."""
        clear_screen()
        print_colored("YouTube Speed Test", "red")
        print_colored("1. YouTube Server 1 (74.125.24.91)", "white")
        print_colored("2. YouTube Server 2 (172.217.194.113)", "white")
        print_colored("0. Back to main menu", "red")
        
        try:
            choice = input("Select a server (0-2): ")
            
            if choice == "1":
                self.run_speed_test(self.targets['youtube_1'], self.packet_sizes['high'])
            elif choice == "2":
                self.run_speed_test(self.targets['youtube_2'], self.packet_sizes['high'])
        
        except KeyboardInterrupt:
            pass
    
    def run_custom_speed_test(self):
        """Run a custom speed test."""
        clear_screen()
        print_colored("Custom Speed Test", "purple")
        
        try:
            target = input("Enter target host or IP: ")
            if not target:
                return
            
            print_colored("\nSelect packet size:", "cyan")
            print_colored("1. Low (1000 bytes)", "white")
            print_colored("2. Medium (3000 bytes)", "white")
            print_colored("3. High (9000 bytes)", "yellow")
            print_colored("4. Custom size", "red")
            
            size_choice = input("Select packet size (1-4): ")
            
            if size_choice == "1":
                packet_size = self.packet_sizes['low']
            elif size_choice == "2":
                packet_size = self.packet_sizes['medium']
            elif size_choice == "3":
                packet_size = self.packet_sizes['high']
            elif size_choice == "4":
                custom_size = input("Enter custom packet size in bytes: ")
                packet_size = int(custom_size) if custom_size else 1000
            else:
                packet_size = self.packet_sizes['medium']
            
            duration = input("Enter test duration in seconds (default: 30): ")
            duration = int(duration) if duration else 30
            
            self.run_speed_test(target, packet_size, duration)
        
        except (KeyboardInterrupt, ValueError) as e:
            if isinstance(e, ValueError):
                print_colored(f"Error: {e}", "red")
                input("Press Enter to continue...")
    
    def show_network_info(self):
        """Show network information."""
        clear_screen()
        print_colored("Network Information", "blue")
        
        # Get IP configuration
        print_colored("\nIP Configuration:", "green")
        if platform.system().lower() == "windows":
            subprocess.run(["ipconfig"], check=False)
        else:
            subprocess.run(["ifconfig"], check=False)
        
        # Get routing table
        print_colored("\nRouting Table:", "green")
        if platform.system().lower() == "windows":
            subprocess.run(["route", "print"], check=False)
        else:
            subprocess.run(["route", "-n"], check=False)
        
        # Get DNS information
        print_colored("\nDNS Information:", "green")
        if platform.system().lower() == "windows":
            subprocess.run(["ipconfig", "/displaydns"], check=False)
        else:
            if os.path.exists("/etc/resolv.conf"):
                print_colored("DNS Servers:", "cyan")
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if "nameserver" in line:
                            print(line.strip())
        
        input("\nPress Enter to continue...")
    
    def run_full_speed_suite(self):
        """Run a full suite of speed tests."""
        clear_screen()
        print_colored("Full Speed Test Suite", "yellow")
        print_colored("This will run speed tests to multiple targets with different packet sizes.", "cyan")
        print_colored("The tests will take several minutes to complete.", "red")
        print()
        
        confirm = input("Do you want to continue? (y/n): ")
        if confirm.lower() != "y":
            return
        
        # Define test configurations
        tests = [
            {"name": "Google DNS (Low Speed)", "target": self.targets['google_dns'], "size": self.packet_sizes['low'], "duration": 10},
            {"name": "Google DNS (Medium Speed)", "target": self.targets['google_dns'], "size": self.packet_sizes['medium'], "duration": 10},
            {"name": "Google DNS (High Speed)", "target": self.targets['google_dns'], "size": self.packet_sizes['high'], "duration": 10},
            {"name": "Cloudflare DNS (Medium Speed)", "target": self.targets['cloudflare_dns'], "size": self.packet_sizes['medium'], "duration": 10},
            {"name": "YouTube (High Speed)", "target": self.targets['youtube_1'], "size": self.packet_sizes['high'], "duration": 10}
        ]
        
        # Run each test
        for i, test in enumerate(tests, 1):
            clear_screen()
            print_colored(f"Test {i} of {len(tests)}: {test['name']}", "green")
            print_colored(f"Target: {test['target']}", "cyan")
            print_colored(f"Packet Size: {test['size']} bytes", "cyan")
            print_colored(f"Duration: {test['duration']} seconds", "cyan")
            print()
            
            try:
                self.run_speed_test(test['target'], test['size'], test['duration'])
                
                if i < len(tests):
                    print_colored("\nNext test starting in 5 seconds...", "yellow")
                    time.sleep(5)
            
            except KeyboardInterrupt:
                print_colored("\nTest suite interrupted.", "red")
                input("Press Enter to continue...")
                return
        
        print_colored("\nAll tests completed!", "green")
        input("Press Enter to continue...")
    
    def run(self):
        """Run the main application loop."""
        # Show loading animation
        self.show_loading_animation()
        
        while True:
            choice = self.show_menu()
            
            if choice == "0":
                clear_screen()
                print_colored("Thank you for using the SpeedUp Tool!", "green")
                print_colored("Goodbye!", "blue")
                break
            
            elif choice == "1":
                # Speed Test v1 (Medium)
                self.run_speed_test(self.targets['google_dns'], self.packet_sizes['medium'])
            
            elif choice == "2":
                # Speed Test v2 (Maximum)
                self.run_speed_test(self.targets['google_dns'], self.packet_sizes['high'])
            
            elif choice == "3":
                # Full Speed Test Suite
                self.run_full_speed_suite()
            
            elif choice == "4":
                # Secret Codes
                self.run_secret_codes()
            
            elif choice == "5":
                # Browser Speed Test
                self.run_speed_test(self.targets['google_browser'], self.packet_sizes['high'])
            
            elif choice == "6":
                # YouTube Speed Test
                self.run_youtube_speed_test()
            
            elif choice == "7":
                # Custom Speed Test
                self.run_custom_speed_test()
            
            elif choice == "8":
                # Network Information
                self.show_network_info()
            
            elif choice == "9":
                # Advanced Pinger Options
                # Import and use the advanced_options function from pinger.py
                try:
                    from pinger import advanced_options
                    pinger, duration = advanced_options()
                    if pinger:
                        pinger.start(duration=duration)
                except (ImportError, AttributeError):
                    print_colored("Error: Could not access advanced options from pinger.py", "red")
                    input("Press Enter to continue...")
            
            else:
                print_colored("Invalid choice. Please try again.", "red")
                time.sleep(1)


def main():
    """Parse command line arguments and run the application."""
    parser = argparse.ArgumentParser(description="Enhanced SpeedUp Tool - Network speed optimization and testing")
    parser.add_argument("-q", "--quick", action="store_true", help="Skip the loading animation")
    parser.add_argument("-t", "--target", help="Specify a target for quick speed test")
    parser.add_argument("-s", "--size", type=int, choices=[1000, 3000, 9000], help="Specify packet size (1000, 3000, or 9000)")
    parser.add_argument("-d", "--duration", type=int, default=30, help="Test duration in seconds (default: 30)")
    
    args = parser.parse_args()
    
    speedup = SpeedUp()
    
    # If target is specified, run a quick test
    if args.target:
        packet_size = args.size if args.size else 3000
        speedup.run_speed_test(args.target, packet_size, args.duration)
        return
    
    # Otherwise, run the full application
    if not args.quick:
        speedup.show_loading_animation()
    
    speedup.run()


if __name__ == "__main__":
    main()
