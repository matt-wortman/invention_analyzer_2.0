#!/usr/bin/env python3
"""
Simple Qt GUI test for WSL
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WSL Qt Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add components
        label = QLabel("Qt GUI working in WSL!")
        label.setStyleSheet("font-size: 16px; padding: 20px;")
        
        button = QPushButton("Click Me!")
        button.clicked.connect(self.on_button_click)
        
        layout.addWidget(label)
        layout.addWidget(button)
        
        central_widget.setLayout(layout)
        
    def on_button_click(self):
        print("Button clicked - Qt is working!")

def main():
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())