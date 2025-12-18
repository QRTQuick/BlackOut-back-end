import sys
import os
import requests
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QPushButton, QLabel, 
                               QFileDialog, QComboBox, QTextEdit, QProgressBar,
                               QListWidget, QMessageBox, QGroupBox)
from PySide6.QtCore import QThread, QSignal, Qt
from PySide6.QtGui import QPixmap, QFont

class ConversionWorker(QThread):
    progress = QSignal(str)
    finished = QSignal(str, bool)
    
    def __init__(self, file_path, target_format):
        super().__init__()
        self.file_path = file_path
        self.target_format = target_format
        self.api_url = "http://127.0.0.1:8000"
        self.api_key = "blackout-secret-key"
    
    def run(self):
        try:
            self.progress.emit("Uploading file...")
            
            # Upload file for conversion
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                headers = {'X-API-Key': self.api_key}
                params = {'target_format': self.target_format}
                
                response = requests.post(
                    f"{self.api_url}/api/convert",
                    files=files,
                    headers=headers,
                    params=params
                )
            
            if response.status_code == 200:
                task_id = response.json()['task_id']
                self.progress.emit(f"Conversion started. Task ID: {task_id}")
                
                # Wait for conversion to complete
                import time
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    status_response = requests.get(f"{self.api_url}/api/status/{task_id}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        self.progress.emit(f"Status: {status_data['status']}")
                        
                        if status_data['status'] == 'ready':
                            self.finished.emit(task_id, True)
                            return
                        elif status_data['status'] == 'expired':
                            self.finished.emit("File expired", False)
                            return
                
                self.finished.emit("Conversion timeout", False)
            else:
                self.finished.emit(f"Upload failed: {response.text}", False)
                
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}", False)

class NodeBlackTester(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NodeBlack Backend Tester")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Title
        title = QLabel("NodeBlack API Tester")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Connection test
        self.setup_connection_test(layout)
        
        # File conversion section
        self.setup_conversion_section(layout)
        
        # Files list section
        self.setup_files_section(layout)
        
        # Log section
        self.setup_log_section(layout)
        
        # Test connection on startup
        self.test_connection()
    
    def setup_connection_test(self, layout):
        group = QGroupBox("Connection Test")
        group_layout = QHBoxLayout(group)
        
        self.connection_status = QLabel("Testing...")
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        
        group_layout.addWidget(QLabel("Status:"))
        group_layout.addWidget(self.connection_status)
        group_layout.addWidget(self.test_btn)
        
        layout.addWidget(group)
    
    def setup_conversion_section(self, layout):
        group = QGroupBox("File Conversion")
        group_layout = QVBoxLayout(group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.select_btn = QPushButton("Select File")
        self.select_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_btn)
        group_layout.addLayout(file_layout)
        
        # Format selection
        format_layout = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpg", "jpeg", "webp", "docx"])
        
        format_layout.addWidget(QLabel("Target Format:"))
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        group_layout.addLayout(format_layout)
        
        # Convert button and progress
        self.convert_btn = QPushButton("Convert File")
        self.convert_btn.clicked.connect(self.convert_file)
        self.convert_btn.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        group_layout.addWidget(self.convert_btn)
        group_layout.addWidget(self.progress_bar)
        
        layout.addWidget(group)
    
    def setup_files_section(self, layout):
        group = QGroupBox("Converted Files")
        group_layout = QVBoxLayout(group)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Files")
        self.refresh_btn.clicked.connect(self.refresh_files)
        refresh_layout.addWidget(self.refresh_btn)
        refresh_layout.addStretch()
        group_layout.addLayout(refresh_layout)
        
        # Files list
        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self.download_file)
        group_layout.addWidget(self.files_list)
        
        # Download button
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.clicked.connect(self.download_selected)
        group_layout.addWidget(self.download_btn)
        
        layout.addWidget(group)
    
    def setup_log_section(self, layout):
        group = QGroupBox("Log")
        group_layout = QVBoxLayout(group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        group_layout.addWidget(self.log_text)
        
        layout.addWidget(group)
    
    def log(self, message):
        self.log_text.append(f"[{self.get_timestamp()}] {message}")
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def test_connection(self):
        try:
            response = requests.get("http://127.0.0.1:8000/api/test", timeout=5)
            if response.status_code == 200:
                self.connection_status.setText("✅ Connected")
                self.connection_status.setStyleSheet("color: green")
                self.log("Connection successful")
                self.refresh_files()
            else:
                self.connection_status.setText("❌ Error")
                self.connection_status.setStyleSheet("color: red")
                self.log(f"Connection failed: {response.status_code}")
        except Exception as e:
            self.connection_status.setText("❌ Failed")
            self.connection_status.setStyleSheet("color: red")
            self.log(f"Connection error: {str(e)}")
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select File", 
            "", 
            "Images (*.png *.jpg *.jpeg *.webp);;Documents (*.pdf *.txt);;All Files (*)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.convert_btn.setEnabled(True)
            self.log(f"Selected file: {os.path.basename(file_path)}")
    
    def convert_file(self):
        if not hasattr(self, 'selected_file'):
            return
        
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        target_format = self.format_combo.currentText()
        self.log(f"Starting conversion to {target_format}")
        
        self.worker = ConversionWorker(self.selected_file, target_format)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()
    
    def conversion_finished(self, result, success):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.log(f"✅ Conversion completed! Task ID: {result}")
            self.refresh_files()
            QMessageBox.information(self, "Success", f"File converted successfully!\nTask ID: {result}")
        else:
            self.log(f"❌ Conversion failed: {result}")
            QMessageBox.warning(self, "Error", f"Conversion failed:\n{result}")
    
    def refresh_files(self):
        try:
            response = requests.get("http://127.0.0.1:8000/api/files")
            if response.status_code == 200:
                data = response.json()
                self.files_list.clear()
                
                for file_info in data['files']:
                    status_icon = "✅" if file_info['status'] == 'available' and file_info['file_exists'] else "❌"
                    item_text = f"{status_icon} {file_info['task_id'][:8]}... ({file_info['status']})"
                    
                    item = self.files_list.addItem(item_text)
                    # Store full info in item data
                    self.files_list.item(self.files_list.count()-1).setData(Qt.UserRole, file_info)
                
                self.log(f"Refreshed files list: {data['total']} files")
            else:
                self.log(f"Failed to refresh files: {response.status_code}")
        except Exception as e:
            self.log(f"Error refreshing files: {str(e)}")
    
    def download_selected(self):
        current_item = self.files_list.currentItem()
        if current_item:
            self.download_file(current_item)
    
    def download_file(self, item):
        file_info = item.data(Qt.UserRole)
        if not file_info or file_info['status'] != 'available' or not file_info['file_exists']:
            QMessageBox.warning(self, "Error", "File is not available for download")
            return
        
        # Ask where to save
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted File",
            f"converted_{file_info['task_id'][:8]}.{os.path.splitext(file_info['file_path'])[1][1:]}",
            "All Files (*)"
        )
        
        if save_path:
            try:
                response = requests.get(f"http://127.0.0.1:8000/api/download/{file_info['task_id']}")
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    self.log(f"✅ Downloaded: {os.path.basename(save_path)}")
                    QMessageBox.information(self, "Success", f"File downloaded to:\n{save_path}")
                else:
                    self.log(f"❌ Download failed: {response.status_code}")
                    QMessageBox.warning(self, "Error", f"Download failed: {response.text}")
            except Exception as e:
                self.log(f"❌ Download error: {str(e)}")
                QMessageBox.warning(self, "Error", f"Download error:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NodeBlackTester()
    window.show()
    sys.exit(app.exec())