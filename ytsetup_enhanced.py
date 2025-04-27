#!/usr/bin/env python3
"""
Enhanced YouTube Setup Tool - A tool for optimizing YouTube connections

This script provides a modern, efficient interface for:
1. Testing and optimizing connections to YouTube servers
2. Measuring performance to different YouTube CDN endpoints
3. Integrating with the enhanced pinger tool
4. Providing detailed analytics on YouTube connectivity
"""

import argparse
import json
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


class YouTubeSetup:
    """Main class for the YouTube Setup tool."""

    def __init__(self):
        """Initialize the YouTube Setup tool."""
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
        
        # Define YouTube server endpoints
        self.youtube_servers = {
            'main': {
                'name': 'YouTube Main',
                'ip': '74.125.24.91',
                'description': 'Primary YouTube server'
            },
            'alternative': {
                'name': 'YouTube Alternative',
                'ip': '172.217.194.113',
                'description': 'Alternative YouTube server'
            },
            'upload': {
                'name': 'YouTube Upload',
                'ip': '142.250.190.78',
                'description': 'YouTube upload server'
            },
            'streaming': {
                'name': 'YouTube Streaming',
                'ip': '216.58.210.46',
                'description': 'YouTube streaming server'
            }
        }
        
        # Define packet sizes for different quality levels
        self.packet_sizes = {
            'standard': 1000,
            'hd': 3000,
            'ultra_hd': 9000
        }
        
        # Define video quality settings
        self.video_quality = {
            'low': {
                'name': '360p',
                'bandwidth': '0.5-1 Mbps',
                'packet_size': self.packet_sizes['standard']
            },
            'medium': {
                'name': '720p',
                'bandwidth': '2.5-4 Mbps',
                'packet_size': self.packet_sizes['standard']
            },
            'high': {
                'name': '1080p',
                'bandwidth': '5-8 Mbps',
                'packet_size': self.packet_sizes['hd']
            },
            'ultra': {
                'name': '4K',
                'bandwidth': '20+ Mbps',
                'packet_size': self.packet_sizes['ultra_hd']
            }
        }

    def show_loading_animation(self):
        """Show a loading animation."""
        clear_screen()
        print_colored("Loading YouTube Setup...", "red")
        
        for i in range(0, 101, 20):
            clear_screen()
            if i < 50:
                print_colored(f"Loading {i}%", "red")
            elif i < 80:
                print_colored(f"Loading {i}%", "yellow")
            else:
                print_colored(f"Loading {i}%", "green")
            
            # Adjust sleep time to make loading faster
            time.sleep(0.3)
    
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
            subprocess.run(["figlet", "YouTube"], check=False)
            subprocess.run(["figlet", "Setup"], check=False)
        else:
            print_colored("==========================", "red")
            print_colored("    YOUTUBE SETUP TOOL    ", "red")
            print_colored("==========================", "red")
        
        print_colored("Optimize Your YouTube Experience", "cyan")
        print_colored("==========================", "red")
        print()
    
    def show_menu(self):
        """Show the main menu and get user choice."""
        self.show_header()
        
        print_colored("Choose a YouTube server to test:", "green")
        print()
        print_colored("SERVER OPTIONS", "yellow")
        print_colored("1. YouTube Main Server (74.125.24.91)", "white")
        print_colored("2. YouTube Alternative Server (172.217.194.113)", "white")
        print_colored("3. YouTube Upload Server (142.250.190.78)", "cyan")
        print_colored("4. YouTube Streaming Server (216.58.210.46)", "cyan")
        print()
        print_colored("QUALITY OPTIONS", "yellow")
        print_colored("5. Test All Servers (Quick)", "green")
        print_colored("6. Full YouTube Network Analysis", "red")
        print_colored("7. Video Quality Optimizer", "purple")
        print()
        print_colored("TOOLS", "yellow")
        print_colored("8. YouTube DNS Lookup", "blue")
        print_colored("9. Save Results to File", "blue")
        print_colored("0. Exit", "red")
        print()
        
        try:
            choice = input("Enter your choice (0-9): ")
            return choice
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
    
    def run_server_test(self, server_key: str, packet_size: int = None, duration: int = 30):
        """Run a test to a specific YouTube server."""
        if server_key not in self.youtube_servers:
            print_colored(f"Error: Unknown server key: {server_key}", "red")
            return
        
        server = self.youtube_servers[server_key]
        if packet_size is None:
            packet_size = self.packet_sizes['ultra_hd']  # Default to highest quality
        
        clear_screen()
        print_colored(f"Testing connection to {server['name']} ({server['ip']})", "green")
        print_colored(f"Description: {server['description']}", "cyan")
        print_colored(f"Packet size: {packet_size} bytes", "cyan")
        print_colored("Press Ctrl+C to stop the test early", "yellow")
        print()
        
        # Create and run a Pinger instance
        pinger = Pinger(
            target=server['ip'],
            interval=1.0,  # 1 second interval for more responsive tests
            packet_size=packet_size,
            verbose=True
        )
        
        pinger.start(duration=duration)
        
        return pinger
    
    def test_all_servers(self, quick: bool = True):
        """Test all YouTube servers."""
        clear_screen()
        print_colored("Testing All YouTube Servers", "green")
        print_colored("This will test connectivity to multiple YouTube servers.", "cyan")
        print()
        
        # Define test duration based on quick mode
        duration = 10 if quick else 30
        packet_size = self.packet_sizes['hd']  # Use HD quality for tests
        
        results = {}
        
        for key, server in self.youtube_servers.items():
            clear_screen()
            print_colored(f"Testing {server['name']} ({server['ip']})", "green")
            print_colored(f"Description: {server['description']}", "cyan")
            print_colored(f"Test duration: {duration} seconds", "yellow")
            print()
            
            try:
                # Create a Pinger instance
                pinger = Pinger(
                    target=server['ip'],
                    interval=1.0,
                    packet_size=packet_size,
                    verbose=True
                )
                
                # Start the pinger and capture results
                pinger.start(duration=duration)
                
                # Store results
                results[key] = {
                    'server': server['name'],
                    'ip': server['ip'],
                    'avg_response': sum(pinger.response_times) / len(pinger.response_times) if pinger.response_times else 0,
                    'min_response': min(pinger.response_times) if pinger.response_times else 0,
                    'max_response': max(pinger.response_times) if pinger.response_times else 0,
                    'success_rate': (pinger.successful_pings / pinger.total_pings * 100) if pinger.total_pings > 0 else 0
                }
                
                if not quick:
                    print_colored("\nTest completed. Moving to next server in 3 seconds...", "yellow")
                    time.sleep(3)
            
            except KeyboardInterrupt:
                print_colored("\nTest interrupted. Moving to next server...", "red")
                time.sleep(1)
        
        # Show summary of results
        self.show_test_summary(results)
    
    def show_test_summary(self, results: Dict):
        """Show a summary of test results."""
        clear_screen()
        print_colored("YouTube Server Test Results", "green")
        print_colored("============================", "cyan")
        print()
        
        # Find the best server based on response time
        best_server = min(results.items(), key=lambda x: x[1]['avg_response']) if results else None
        
        for key, result in results.items():
            server_name = result['server']
            is_best = (best_server and best_server[0] == key)
            
            if is_best:
                print_colored(f"★ {server_name} ({result['ip']}) - RECOMMENDED", "green")
            else:
                print_colored(f"{server_name} ({result['ip']})", "white")
            
            print_colored(f"  Average Response: {result['avg_response']:.2f}ms", 
                         "green" if result['avg_response'] < 100 else "yellow")
            print_colored(f"  Min/Max Response: {result['min_response']:.2f}ms / {result['max_response']:.2f}ms", "cyan")
            print_colored(f"  Success Rate: {result['success_rate']:.1f}%", 
                         "green" if result['success_rate'] > 95 else "red")
            print()
        
        if best_server:
            print_colored(f"Recommendation: Use {best_server[1]['server']} for the best YouTube experience", "green")
            print_colored(f"Average response time: {best_server[1]['avg_response']:.2f}ms", "green")
        
        input("\nPress Enter to continue...")
    
    def run_video_quality_optimizer(self):
        """Run the video quality optimizer."""
        clear_screen()
        print_colored("YouTube Video Quality Optimizer", "purple")
        print_colored("This tool will help determine the best video quality for your connection.", "cyan")
        print()
        
        # Ask which server to test
        print_colored("Select a YouTube server to test:", "green")
        for i, (key, server) in enumerate(self.youtube_servers.items(), 1):
            print_colored(f"{i}. {server['name']} ({server['ip']})", "white")
        
        try:
            server_choice = input("\nEnter server number (1-4, default: 1): ")
            server_index = int(server_choice) - 1 if server_choice else 0
            
            if server_index < 0 or server_index >= len(self.youtube_servers):
                server_index = 0
            
            server_key = list(self.youtube_servers.keys())[server_index]
            server = self.youtube_servers[server_key]
            
            # Test each quality level
            results = {}
            
            for quality_key, quality in self.video_quality.items():
                clear_screen()
                print_colored(f"Testing for {quality['name']} quality ({quality['bandwidth']})", "green")
                print_colored(f"Server: {server['name']} ({server['ip']})", "cyan")
                print_colored(f"Packet size: {quality['packet_size']} bytes", "cyan")
                print_colored("Test duration: 10 seconds", "yellow")
                print()
                
                # Create a Pinger instance
                pinger = Pinger(
                    target=server['ip'],
                    interval=1.0,
                    packet_size=quality['packet_size'],
                    verbose=True
                )
                
                # Start the pinger
                pinger.start(duration=10)
                
                # Store results
                avg_response = sum(pinger.response_times) / len(pinger.response_times) if pinger.response_times else 0
                success_rate = (pinger.successful_pings / pinger.total_pings * 100) if pinger.total_pings > 0 else 0
                
                results[quality_key] = {
                    'quality': quality['name'],
                    'bandwidth': quality['bandwidth'],
                    'avg_response': avg_response,
                    'success_rate': success_rate,
                    'viable': success_rate > 95 and avg_response < 200  # Criteria for viable quality
                }
                
                print_colored("\nTest completed. Moving to next quality level...", "yellow")
                time.sleep(2)
            
            # Show quality recommendations
            self.show_quality_recommendations(results, server)
            
        except (ValueError, KeyboardInterrupt):
            print_colored("\nOptimization interrupted.", "red")
            time.sleep(1)
    
    def show_quality_recommendations(self, results: Dict, server: Dict):
        """Show video quality recommendations based on test results."""
        clear_screen()
        print_colored("YouTube Video Quality Recommendations", "purple")
        print_colored(f"Server: {server['name']} ({server['ip']})", "cyan")
        print_colored("====================================", "cyan")
        print()
        
        # Find the highest viable quality
        best_quality = None
        for quality_key in ['ultra', 'high', 'medium', 'low']:
            if quality_key in results and results[quality_key]['viable']:
                best_quality = quality_key
                break
        
        for quality_key, result in results.items():
            is_recommended = (quality_key == best_quality)
            quality_name = result['quality']
            
            if is_recommended:
                print_colored(f"★ {quality_name} ({result['bandwidth']}) - RECOMMENDED", "green")
            else:
                viable_text = "VIABLE" if result['viable'] else "NOT RECOMMENDED"
                color = "white" if result['viable'] else "red"
                print_colored(f"{quality_name} ({result['bandwidth']}) - {viable_text}", color)
            
            print_colored(f"  Average Response: {result['avg_response']:.2f}ms", 
                         "green" if result['avg_response'] < 100 else "yellow")
            print_colored(f"  Success Rate: {result['success_rate']:.1f}%", 
                         "green" if result['success_rate'] > 95 else "red")
            print()
        
        if best_quality:
            quality = self.video_quality[best_quality]
            print_colored(f"Recommendation: Set YouTube quality to {quality['name']}", "green")
            print_colored(f"This requires approximately {quality['bandwidth']} of bandwidth", "green")
        else:
            print_colored("Your connection may not be stable enough for YouTube streaming.", "red")
            print_colored("Try connecting to a different network or contact your ISP.", "yellow")
        
        input("\nPress Enter to continue...")
    
    def run_youtube_dns_lookup(self):
        """Run DNS lookup for YouTube domains."""
        clear_screen()
        print_colored("YouTube DNS Lookup", "blue")
        print_colored("This tool will look up DNS information for YouTube domains.", "cyan")
        print()
        
        youtube_domains = [
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
            "ytimg.com",
            "yt3.ggpht.com",
            "googlevideo.com"
        ]
        
        for domain in youtube_domains:
            print_colored(f"Looking up {domain}...", "yellow")
            
            try:
                # Use nslookup on Windows, dig on others
                if platform.system().lower() == "windows":
                    result = subprocess.run(["nslookup", domain], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, 
                                          text=True, 
                                          check=False)
                    output = result.stdout
                else:
                    result = subprocess.run(["dig", domain], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE, 
                                          text=True, 
                                          check=False)
                    output = result.stdout
                
                print_colored(f"Results for {domain}:", "green")
                print(output)
                print()
            
            except Exception as e:
                print_colored(f"Error looking up {domain}: {e}", "red")
            
            print_colored("-----------------------------------", "cyan")
        
        input("\nPress Enter to continue...")
    
    def save_results_to_file(self):
        """Save test results to a file."""
        clear_screen()
        print_colored("Save YouTube Test Results", "blue")
        print_colored("This will run tests and save the results to a file.", "cyan")
        print()
        
        filename = input("Enter filename to save results (default: youtube_results.txt): ")
        filename = filename if filename else "youtube_results.txt"
        
        print_colored("\nRunning tests for all servers...", "yellow")
        
        # Run quick tests on all servers
        results = {}
        
        for key, server in self.youtube_servers.items():
            print_colored(f"Testing {server['name']}...", "green")
            
            try:
                # Create a Pinger instance
                pinger = Pinger(
                    target=server['ip'],
                    interval=1.0,
                    packet_size=self.packet_sizes['hd'],
                    verbose=False  # Don't show verbose output
                )
                
                # Start the pinger
                pinger.start(duration=5)
                
                # Store results
                results[key] = {
                    'server': server['name'],
                    'ip': server['ip'],
                    'avg_response': sum(pinger.response_times) / len(pinger.response_times) if pinger.response_times else 0,
                    'min_response': min(pinger.response_times) if pinger.response_times else 0,
                    'max_response': max(pinger.response_times) if pinger.response_times else 0,
                    'success_rate': (pinger.successful_pings / pinger.total_pings * 100) if pinger.total_pings > 0 else 0,
                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                }
            
            except KeyboardInterrupt:
                print_colored("\nTest interrupted.", "red")
                break
        
        # Save results to file
        try:
            with open(filename, 'w') as f:
                f.write("YouTube Server Test Results\n")
                f.write("==========================\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for key, result in results.items():
                    f.write(f"Server: {result['server']} ({result['ip']})\n")
                    f.write(f"Average Response: {result['avg_response']:.2f}ms\n")
                    f.write(f"Min/Max Response: {result['min_response']:.2f}ms / {result['max_response']:.2f}ms\n")
                    f.write(f"Success Rate: {result['success_rate']:.1f}%\n")
                    f.write("\n")
                
                # Find the best server
                best_server = min(results.items(), key=lambda x: x[1]['avg_response']) if results else None
                
                if best_server:
                    f.write(f"Recommendation: Use {best_server[1]['server']} for the best YouTube experience\n")
                    f.write(f"Average response time: {best_server[1]['avg_response']:.2f}ms\n")
            
            print_colored(f"\nResults saved to {filename}", "green")
        
        except Exception as e:
            print_colored(f"\nError saving results: {e}", "red")
        
        input("\nPress Enter to continue...")
    
    def run_full_network_analysis(self):
        """Run a full YouTube network analysis."""
        clear_screen()
        print_colored("Full YouTube Network Analysis", "red")
        print_colored("This will run comprehensive tests on your YouTube connectivity.", "cyan")
        print_colored("The analysis will take several minutes to complete.", "yellow")
        print()
        
        confirm = input("Do you want to continue? (y/n): ")
        if confirm.lower() != "y":
            return
        
        # Step 1: Test all servers with different packet sizes
        results = {}
        
        for key, server in self.youtube_servers.items():
            server_results = {}
            
            for quality_name, packet_size in self.packet_sizes.items():
                clear_screen()
                print_colored("Full YouTube Network Analysis", "red")
                print_colored(f"Testing {server['name']} with {quality_name} quality", "green")
                print_colored(f"Packet size: {packet_size} bytes", "cyan")
                print()
                
                try:
                    # Create a Pinger instance
                    pinger = Pinger(
                        target=server['ip'],
                        interval=1.0,
                        packet_size=packet_size,
                        verbose=True
                    )
                    
                    # Start the pinger
                    pinger.start(duration=10)
                    
                    # Store results
                    server_results[quality_name] = {
                        'avg_response': sum(pinger.response_times) / len(pinger.response_times) if pinger.response_times else 0,
                        'min_response': min(pinger.response_times) if pinger.response_times else 0,
                        'max_response': max(pinger.response_times) if pinger.response_times else 0,
                        'success_rate': (pinger.successful_pings / pinger.total_pings * 100) if pinger.total_pings > 0 else 0
                    }
                
                except KeyboardInterrupt:
                    print_colored("\nTest interrupted.", "red")
                    break
            
            results[key] = {
                'server': server['name'],
                'ip': server['ip'],
                'tests': server_results
            }
        
        # Step 2: Show comprehensive results
        self.show_comprehensive_results(results)
    
    def show_comprehensive_results(self, results: Dict):
        """Show comprehensive test results."""
        clear_screen()
        print_colored("YouTube Network Analysis Results", "red")
        print_colored("================================", "cyan")
        print()
        
        # Calculate overall scores for each server
        server_scores = {}
        
        for key, result in results.items():
            server = result['server']
            tests = result['tests']
            
            if not tests:
                continue
            
            # Calculate average response time across all tests
            avg_responses = [test['avg_response'] for test in tests.values()]
            overall_avg = sum(avg_responses) / len(avg_responses) if avg_responses else 0
            
            # Calculate average success rate across all tests
            success_rates = [test['success_rate'] for test in tests.values()]
            overall_success = sum(success_rates) / len(success_rates) if success_rates else 0
            
            # Calculate a score (lower is better)
            score = overall_avg * (100 / max(overall_success, 1))
            
            server_scores[key] = {
                'server': server,
                'score': score,
                'avg_response': overall_avg,
                'success_rate': overall_success
            }
        
        # Sort servers by score
        sorted_servers = sorted(server_scores.items(), key=lambda x: x[1]['score'])
        
        # Show results for each server
        for i, (key, score) in enumerate(sorted_servers, 1):
            result = results[key]
            
            print_colored(f"{i}. {result['server']} ({result['ip']})", "green" if i == 1 else "white")
            print_colored(f"   Overall Score: {score['score']:.2f} (lower is better)", "cyan")
            print_colored(f"   Average Response: {score['avg_response']:.2f}ms", "cyan")
            print_colored(f"   Success Rate: {score['success_rate']:.1f}%", "cyan")
            
            print_colored("\n   Quality Tests:", "yellow")
            for quality_name, test in result['tests'].items():
                print_colored(f"   - {quality_name.upper()}: {test['avg_response']:.2f}ms, {test['success_rate']:.1f}% success", 
                             "green" if test['success_rate'] > 95 else "red")
            
            print()
        
        if sorted_servers:
            best_server = sorted_servers[0][1]
            print_colored(f"Recommendation: Use {best_server['server']} for the best YouTube experience", "green")
            print_colored(f"This server had the best combination of response time and reliability.", "green")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the main application loop."""
        # Show loading animation
        self.show_loading_animation()
        
        while True:
            choice = self.show_menu()
            
            if choice == "0":
                clear_screen()
                print_colored("Thank you for using the YouTube Setup Tool!", "red")
                print_colored("Goodbye!", "blue")
                break
            
            elif choice == "1":
                # YouTube Main Server
                self.run_server_test('main')
            
            elif choice == "2":
                # YouTube Alternative Server
                self.run_server_test('alternative')
            
            elif choice == "3":
                # YouTube Upload Server
                self.run_server_test('upload')
            
            elif choice == "4":
                # YouTube Streaming Server
                self.run_server_test('streaming')
            
            elif choice == "5":
                # Test All Servers (Quick)
                self.test_all_servers(quick=True)
            
            elif choice == "6":
                # Full YouTube Network Analysis
                self.run_full_network_analysis()
            
            elif choice == "7":
                # Video Quality Optimizer
                self.run_video_quality_optimizer()
            
            elif choice == "8":
                # YouTube DNS Lookup
                self.run_youtube_dns_lookup()
            
            elif choice == "9":
                # Save Results to File
                self.save_results_to_file()
            
            else:
                print_colored("Invalid choice. Please try again.", "red")
                time.sleep(1)


def main():
    """Parse command line arguments and run the application."""
    parser = argparse.ArgumentParser(description="Enhanced YouTube Setup Tool - Optimize your YouTube experience")
    parser.add_argument("-q", "--quick", action="store_true", help="Skip the loading animation")
    parser.add_argument("-s", "--server", choices=['main', 'alternative', 'upload', 'streaming'], 
                       help="Specify a server to test")
    parser.add_argument("-p", "--packet-size", type=int, choices=[1000, 3000, 9000], 
                       help="Specify packet size (1000, 3000, or 9000)")
    parser.add_argument("-d", "--duration", type=int, default=30, 
                       help="Test duration in seconds (default: 30)")
    parser.add_argument("-a", "--all", action="store_true", 
                       help="Test all servers and show results")
    parser.add_argument("-o", "--optimize", action="store_true", 
                       help="Run the video quality optimizer")
    
    args = parser.parse_args()
    
    ytsetup = YouTubeSetup()
    
    # Handle command line options
    if args.server:
        packet_size = args.packet_size if args.packet_size else ytsetup.packet_sizes['ultra_hd']
        ytsetup.run_server_test(args.server, packet_size, args.duration)
        return
    
    if args.all:
        ytsetup.test_all_servers(quick=True)
        return
    
    if args.optimize:
        ytsetup.run_video_quality_optimizer()
        return
    
    # Otherwise, run the full application
    if not args.quick:
        ytsetup.show_loading_animation()
    
    ytsetup.run()


if __name__ == "__main__":
    main()
