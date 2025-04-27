#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
                           QPushButton, QComboBox, QCheckBox, QTextEdit, QSystemTrayIcon,
                           QMenu, QTabWidget, QGroupBox, QFormLayout, QMenuBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QFont
import threading
from pinger import Pinger, print_colored
import os

class PingerWorker(QThread):
    output_signal = pyqtSignal(str, str)  # message, color
    finished_signal = pyqtSignal()

    def __init__(self, pinger):
        super().__init__()
        self.pinger = pinger
        self.is_running = True

    def run(self):
        try:
            self.output_signal.emit(f"Starting pinger for {self.pinger.target}...", "blue")

            while self.is_running:
                result = self.pinger.ping_once()
                if result["success"]:
                    self.output_signal.emit(
                        f"Response from {self.pinger.target}: time={result['response_time']:.2f}ms",
                        "green"
                    )

                    # Execute success command if configured
                    if self.pinger.success_cmd:
                        try:
                            import subprocess
                            cmd_result = subprocess.run(
                                self.pinger.success_cmd,
                                shell=True,
                                check=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            if cmd_result.stdout.strip():
                                self.output_signal.emit(f"Command output: {cmd_result.stdout.strip()}", "blue")
                            if cmd_result.stderr.strip():
                                self.output_signal.emit(f"Command error: {cmd_result.stderr.strip()}", "red")
                        except Exception as cmd_err:
                            self.output_signal.emit(f"Error executing command: {str(cmd_err)}", "red")

                    # Execute success script if configured
                    if self.pinger.success_script and os.path.exists(self.pinger.success_script):
                        try:
                            script_output = self.pinger.execute_shell_script(self.pinger.success_script)
                            if script_output.strip():
                                self.output_signal.emit(f"Script output: {script_output.strip()}", "blue")
                        except Exception as script_err:
                            self.output_signal.emit(f"Error executing script: {str(script_err)}", "red")
                else:
                    self.output_signal.emit(
                        f"Failed to ping {self.pinger.target}: {result['error']}",
                        "red"
                    )

                    # Execute failure command if configured
                    if self.pinger.failure_cmd:
                        try:
                            import subprocess
                            cmd_result = subprocess.run(
                                self.pinger.failure_cmd,
                                shell=True,
                                check=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            if cmd_result.stdout.strip():
                                self.output_signal.emit(f"Command output: {cmd_result.stdout.strip()}", "blue")
                            if cmd_result.stderr.strip():
                                self.output_signal.emit(f"Command error: {cmd_result.stderr.strip()}", "red")
                        except Exception as cmd_err:
                            self.output_signal.emit(f"Error executing command: {str(cmd_err)}", "red")

                    # Execute failure script if configured
                    if self.pinger.failure_script and os.path.exists(self.pinger.failure_script):
                        try:
                            script_output = self.pinger.execute_shell_script(self.pinger.failure_script)
                            if script_output.strip():
                                self.output_signal.emit(f"Script output: {script_output.strip()}", "blue")
                        except Exception as script_err:
                            self.output_signal.emit(f"Error executing script: {str(script_err)}", "red")

                # Wait for the next interval
                QThread.msleep(int(self.pinger.interval * 1000))
        except Exception as e:
            self.output_signal.emit(f"Error in pinger thread: {str(e)}", "red")
        finally:
            self.output_signal.emit("Pinger stopped", "blue")
            self.finished_signal.emit()

    def stop(self):
        self.is_running = False

class ModernPingerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Pinger")
        self.setMinimumSize(800, 600)
        self.pinger_worker = None

        # Initialize UI
        self.init_ui()
        self.setup_tray_icon()

        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget {
                background-color: white;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:disabled {
                background-color: #CCE4F7;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Basic Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        # Target Group
        target_group = QGroupBox("Target Configuration")
        target_layout = QFormLayout()

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter host/URL")
        target_layout.addRow("Target:", self.target_input)

        self.ping_type = QComboBox()
        self.ping_type.addItems([
            "1. Standard Ping (TCP/Socket)",
            "2. HTTP/HTTPS Ping",
            "3. System Ping with Custom Packet Size",
            "4. YouTube Speed Test",
            "5. Google DNS Speed Test",
            "6. Custom Target with Shell Command",
            "7. Run Existing Shell Script",
            "8. Advanced Options"
        ])
        target_layout.addRow("Ping Type:", self.ping_type)

        # Connect ping type change to update UI
        self.ping_type.currentIndexChanged.connect(self.update_ui_for_ping_type)

        target_group.setLayout(target_layout)
        basic_layout.addWidget(target_group)

        # Options Group
        options_group = QGroupBox("Ping Options")
        options_layout = QFormLayout()

        self.interval_input = QDoubleSpinBox()
        self.interval_input.setValue(5.0)
        self.interval_input.setRange(0.1, 60.0)
        options_layout.addRow("Interval (s):", self.interval_input)

        self.timeout_input = QDoubleSpinBox()
        self.timeout_input.setValue(2.0)
        self.timeout_input.setRange(0.1, 30.0)
        options_layout.addRow("Timeout (s):", self.timeout_input)

        self.max_failures_input = QSpinBox()
        self.max_failures_input.setValue(3)
        self.max_failures_input.setRange(1, 100)
        options_layout.addRow("Max Failures:", self.max_failures_input)

        self.packet_size_input = QSpinBox()
        self.packet_size_input.setValue(64)
        self.packet_size_input.setRange(32, 65500)
        options_layout.addRow("Packet Size:", self.packet_size_input)

        self.verbose_checkbox = QCheckBox("Verbose Output")
        self.verbose_checkbox.setChecked(True)
        options_layout.addRow("", self.verbose_checkbox)

        options_group.setLayout(options_layout)
        basic_layout.addWidget(options_group)

        # Control Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_pinger)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_pinger)
        self.stop_button.setEnabled(False)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        basic_layout.addLayout(button_layout)

        # Output Area
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        basic_layout.addWidget(self.output_text)

        tab_widget.addTab(basic_tab, "Basic")

        # Advanced Tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Advanced Options
        advanced_group = QGroupBox("Advanced Configuration")
        advanced_form = QFormLayout()

        self.dns_server_input = QLineEdit()
        self.dns_server_input.setPlaceholderText("Custom DNS Server")
        advanced_form.addRow("DNS Server:", self.dns_server_input)

        self.custom_command_input = QLineEdit()
        self.custom_command_input.setPlaceholderText("Custom Shell Command")
        advanced_form.addRow("Custom Command:", self.custom_command_input)

        advanced_group.setLayout(advanced_form)
        advanced_layout.addWidget(advanced_group)

        tab_widget.addTab(advanced_tab, "Advanced")

        # Scripts Tab
        scripts_tab = QWidget()
        scripts_layout = QVBoxLayout(scripts_tab)

        # Scripts List
        scripts_group = QGroupBox("Available Shell Scripts")
        scripts_list_layout = QVBoxLayout()

        self.scripts_list = QTextEdit()
        self.scripts_list.setReadOnly(True)
        scripts_list_layout.addWidget(self.scripts_list)

        # Refresh and Run buttons
        scripts_buttons_layout = QHBoxLayout()
        self.refresh_scripts_button = QPushButton("Refresh Scripts")
        self.refresh_scripts_button.clicked.connect(self.refresh_scripts_list)
        self.run_script_button = QPushButton("Run Selected Script")
        self.run_script_button.clicked.connect(self.run_selected_script)

        scripts_buttons_layout.addWidget(self.refresh_scripts_button)
        scripts_buttons_layout.addWidget(self.run_script_button)

        scripts_list_layout.addLayout(scripts_buttons_layout)
        scripts_group.setLayout(scripts_list_layout)
        scripts_layout.addWidget(scripts_group)

        tab_widget.addTab(scripts_tab, "Shell Scripts")

        # Create menu bar
        self.create_menu_bar()

        # Initialize scripts list
        self.refresh_scripts_list()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save Output", self)
        save_action.triggered.connect(self.save_output)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools Menu
        tools_menu = menubar.addMenu("Tools")

        clear_action = QAction("Clear Output", self)
        clear_action.triggered.connect(self.output_text.clear)
        tools_menu.addAction(clear_action)

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("pinger_icon.png"))

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Enhanced Pinger",
                "Application minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()
        else:
            self.quit_application()

    def quit_application(self):
        self.stop_pinger()
        QApplication.quit()

    # Make this method callable from other threads via signals
    from PyQt6.QtCore import pyqtSlot

    @pyqtSlot(str, str)
    def update_output(self, message, color="black"):
        """Update the output text area with colored text"""
        self.output_text.append(f'<span style="color: {color};">{message}</span>')
        # Auto-scroll to the bottom
        self.output_text.verticalScrollBar().setValue(self.output_text.verticalScrollBar().maximum())

    def start_pinger(self):
        ping_type_index = self.ping_type.currentIndex()

        # Handle Run Existing Shell Script option separately
        if ping_type_index == 6:  # Run Existing Shell Script
            self.run_selected_script()
            return

        # For other ping types, validate target
        if not self.target_input.text() and ping_type_index not in [3, 4]:  # Not YouTube or Google DNS test
            self.update_output("Error: Please enter a target host or URL", "red")
            return

        try:
            # Configure pinger based on selected ping type
            target = self.target_input.text()
            packet_size = None
            success_cmd = None
            failure_cmd = None

            if ping_type_index == 0:  # Standard Ping (TCP/Socket)
                # Use default socket ping
                pass
            elif ping_type_index == 1:  # HTTP/HTTPS Ping
                # Ensure URL has protocol
                if not target.startswith(('http://', 'https://')):
                    target = 'https://' + target
            elif ping_type_index == 2:  # System Ping with Custom Packet Size
                packet_size = self.packet_size_input.value()
            elif ping_type_index == 3:  # YouTube Speed Test
                target = "https://www.youtube.com"
            elif ping_type_index == 4:  # Google DNS Speed Test
                target = "8.8.8.8"
            elif ping_type_index == 5:  # Custom Target with Shell Command
                if self.custom_command_input.text():
                    success_cmd = self.custom_command_input.text()
                    failure_cmd = self.custom_command_input.text()

            # Create the pinger with appropriate configuration
            self.pinger = Pinger(
                target=target,
                interval=self.interval_input.value(),
                timeout=self.timeout_input.value(),
                max_failures=self.max_failures_input.value(),
                verbose=self.verbose_checkbox.isChecked(),
                packet_size=packet_size,
                success_cmd=success_cmd,
                failure_cmd=failure_cmd
            )

            # Create and start the worker thread
            self.pinger_worker = PingerWorker(self.pinger)
            self.pinger_worker.output_signal.connect(self.update_output)
            self.pinger_worker.finished_signal.connect(self.on_pinger_finished)
            self.pinger_worker.start()

            # Update UI
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.update_output(f"Started pinging {target}", "blue")

        except ValueError as e:
            self.update_output(f"Error: {str(e)}", "red")
        except Exception as e:
            self.update_output(f"Unexpected error: {str(e)}", "red")

    def stop_pinger(self):
        if self.pinger_worker and self.pinger_worker.isRunning():
            self.pinger_worker.stop()
            self.pinger_worker.wait()  # Wait for the thread to finish
            self.on_pinger_finished()

    def on_pinger_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def save_output(self):
        # Add save output functionality here
        pass

    def update_ui_for_ping_type(self):
        """Update UI elements based on selected ping type"""
        ping_type_index = self.ping_type.currentIndex()

        # Show/hide fields based on ping type
        if ping_type_index == 0:  # Standard Ping
            self.target_input.setPlaceholderText("Enter host or IP address")
            self.packet_size_input.setEnabled(False)
            self.custom_command_input.setEnabled(False)
        elif ping_type_index == 1:  # HTTP/HTTPS Ping
            self.target_input.setPlaceholderText("Enter URL (including http:// or https://)")
            self.packet_size_input.setEnabled(False)
            self.custom_command_input.setEnabled(False)
        elif ping_type_index == 2:  # System Ping with Custom Packet Size
            self.target_input.setPlaceholderText("Enter host or IP address")
            self.packet_size_input.setEnabled(True)
            self.custom_command_input.setEnabled(False)
        elif ping_type_index == 3:  # YouTube Speed Test
            self.target_input.setText("https://www.youtube.com")
            self.target_input.setEnabled(False)
            self.packet_size_input.setEnabled(False)
            self.custom_command_input.setEnabled(False)
        elif ping_type_index == 4:  # Google DNS Speed Test
            self.target_input.setText("8.8.8.8")
            self.target_input.setEnabled(False)
            self.packet_size_input.setEnabled(False)
            self.custom_command_input.setEnabled(False)
        elif ping_type_index == 5:  # Custom Target with Shell Command
            self.target_input.setPlaceholderText("Enter host or IP address")
            self.packet_size_input.setEnabled(False)
            self.custom_command_input.setEnabled(True)
        elif ping_type_index == 6:  # Run Existing Shell Script
            self.target_input.setEnabled(False)
            self.packet_size_input.setEnabled(False)
            self.custom_command_input.setEnabled(False)
            # Switch to the Shell Scripts tab
            for i in range(self.centralWidget().layout().itemAt(0).widget().count()):
                if self.centralWidget().layout().itemAt(0).widget().tabText(i) == "Shell Scripts":
                    self.centralWidget().layout().itemAt(0).widget().setCurrentIndex(i)
                    break
        elif ping_type_index == 7:  # Advanced Options
            self.target_input.setPlaceholderText("Enter host, IP, or URL")
            self.packet_size_input.setEnabled(True)
            self.custom_command_input.setEnabled(True)
            # Switch to the Advanced tab
            for i in range(self.centralWidget().layout().itemAt(0).widget().count()):
                if self.centralWidget().layout().itemAt(0).widget().tabText(i) == "Advanced":
                    self.centralWidget().layout().itemAt(0).widget().setCurrentIndex(i)
                    break

        # Re-enable target input if it was disabled
        if ping_type_index not in [3, 4, 6]:
            self.target_input.setEnabled(True)

    def refresh_scripts_list(self):
        """Find and display available shell scripts"""
        self.scripts_list.clear()

        # Find shell scripts in the current directory and examples folder
        script_paths = []
        try:
            # Look for .sh files in current directory
            for file in os.listdir('.'):
                if file.endswith('.sh'):
                    script_paths.append(os.path.join('.', file))

            # Look for .sh files in examples directory if it exists
            examples_dir = os.path.join('.', 'examples')
            if os.path.exists(examples_dir) and os.path.isdir(examples_dir):
                for file in os.listdir(examples_dir):
                    if file.endswith('.sh'):
                        script_paths.append(os.path.join(examples_dir, file))
        except Exception as e:
            self.update_output(f"Error finding scripts: {str(e)}", "red")

        # Display found scripts
        if script_paths:
            self.scripts_list.append("<b>Available Shell Scripts:</b>")
            for i, script in enumerate(script_paths, 1):
                self.scripts_list.append(f"{i}. <a href='{script}'>{os.path.basename(script)}</a> ({script})")

            # Store scripts for later use
            self.available_scripts = script_paths
        else:
            self.scripts_list.append("<b>No shell scripts found.</b>")
            self.scripts_list.append("Shell scripts should have .sh extension and be located in:")
            self.scripts_list.append("- Current directory")
            self.scripts_list.append("- 'examples' subdirectory")
            self.available_scripts = []

    def run_selected_script(self):
        """Run the selected shell script"""
        if not hasattr(self, 'available_scripts') or not self.available_scripts:
            self.update_output("No scripts available to run", "red")
            return

        # Simple dialog to select a script
        from PyQt6.QtWidgets import QInputDialog
        script_names = [os.path.basename(script) for script in self.available_scripts]
        script_name, ok = QInputDialog.getItem(
            self, "Select Script", "Choose a script to run:", script_names, 0, False
        )

        if ok and script_name:
            script_index = script_names.index(script_name)
            script_path = self.available_scripts[script_index]

            try:
                # Make script executable
                os.chmod(script_path, 0o755)

                # Run the script
                import subprocess
                self.update_output(f"Running script: {script_path}", "blue")

                # Create a thread to run the script
                def run_script():
                    try:
                        result = subprocess.run(
                            f"bash {script_path}",
                            shell=True,
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        # Use update_output instead of output_signal
                        # We need to use a signal-safe method to update from another thread
                        from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
                        if result.stdout:
                            QMetaObject.invokeMethod(self, "update_output",
                                                   Qt.ConnectionType.QueuedConnection,
                                                   Q_ARG(str, f"Script output:\n{result.stdout}"),
                                                   Q_ARG(str, "blue"))
                        if result.stderr:
                            QMetaObject.invokeMethod(self, "update_output",
                                                   Qt.ConnectionType.QueuedConnection,
                                                   Q_ARG(str, f"Script errors:\n{result.stderr}"),
                                                   Q_ARG(str, "red"))
                        QMetaObject.invokeMethod(self, "update_output",
                                               Qt.ConnectionType.QueuedConnection,
                                               Q_ARG(str, f"Script completed with return code: {result.returncode}"),
                                               Q_ARG(str, "green" if result.returncode == 0 else "red"))
                    except subprocess.CalledProcessError as e:
                        QMetaObject.invokeMethod(self, "update_output",
                                               Qt.ConnectionType.QueuedConnection,
                                               Q_ARG(str, f"Script execution failed: {e.stderr}"),
                                               Q_ARG(str, "red"))
                    except Exception as e:
                        QMetaObject.invokeMethod(self, "update_output",
                                               Qt.ConnectionType.QueuedConnection,
                                               Q_ARG(str, f"Error running script: {str(e)}"),
                                               Q_ARG(str, "red"))

                # Start the thread
                script_thread = threading.Thread(target=run_script)
                script_thread.daemon = True
                script_thread.start()

            except Exception as e:
                self.update_output(f"Error running script: {str(e)}", "red")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look across platforms
    window = ModernPingerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


