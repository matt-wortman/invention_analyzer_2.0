# Academic Publication Search Tool - Enhanced GUI Application
# 
# IMPROVEMENTS IN THIS VERSION:
# - Larger fonts and widget sizes for better readability
# - API key editing functionality in Settings tab
# - Fixed database refresh error (NoneType handling)
# - Better error handling and user feedback
# - Enhanced Settings tab with form layout and scrolling
# - Password fields with show/hide functionality
# - Direct .env file editing capabilities
#
# KNOWN ISSUES TO FIX:
# - Anthropic API selection doesn't work (still uses OpenAI)
# - Should display full database by default instead of empty view
# - Need to add NCBI API key input field
# - Need PubMed Central full text capability

import sys
import os
import threading
from typing import Optional
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton, 
    QTextEdit, QTableWidget, QTableWidgetItem, QProgressBar, QGroupBox,
    QComboBox, QFileDialog, QMessageBox, QSplitter, QHeaderView,
    QFormLayout, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

try:
    from . import config
    from . import batch_processor
    from . import ai_analyzer
    from . import simple_database
    from . import main as cli_main
except ImportError:
    import config
    import batch_processor
    import ai_analyzer
    import simple_database
    import main as cli_main


class WorkerThread(QThread):
    """Worker thread for background operations"""
    progress_update = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, operation_type, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs
        
    def run(self):
        try:
            if self.operation_type == "fetch":
                self.run_fetch_operation()
            elif self.operation_type == "analyze":
                self.run_analyze_operation()
            elif self.operation_type == "export":
                self.run_export_operation()
        except Exception as e:
            self.error.emit(str(e))
    
    def run_fetch_operation(self):
        search_term = self.kwargs.get('search_term', config.SEARCH_TERM_AFFILIATION)
        num_papers = self.kwargs.get('num_papers', config.DEFAULT_MAX_PAPERS_TO_PROCESS)
        year_filter = self.kwargs.get('year_filter', None)
        analyze_with_ai = self.kwargs.get('analyze_with_ai', True)
        
        # Modify search term if year filter is provided
        final_search_term = search_term
        if year_filter and year_filter > 0:
            current_year = datetime.now().year
            start_year = current_year - year_filter + 1
            date_query_part = f" AND (({start_year}[Publication Date] : {current_year}[Publication Date]))"
            final_search_term = f"({search_term}){date_query_part}"
            self.progress_update.emit(f"Applying year filter: searching from {start_year} to {current_year}")
        
        self.progress_update.emit(f"Starting batch processing for: {final_search_term}")
        
        # Batch process papers
        batch_results = batch_processor.process_batch(
            search_term=final_search_term,
            max_papers_to_process=num_papers
        )
        
        self.progress_update.emit(f"Batch processing completed. New papers: {batch_results.get('processed_newly', 0)}")
        
        # AI Analysis if enabled
        if analyze_with_ai and ai_analyzer.llm_client:
            self.progress_update.emit("Starting AI analysis...")
            papers_to_analyze = simple_database.get_all_papers()
            analyzed_count = 0
            
            for paper in papers_to_analyze:
                if paper.get("ai_is_invention_candidate") is None:
                    self.progress_update.emit(f"Analyzing PMID: {paper['pmid']}")
                    
                    if not paper['abstract'] or paper['abstract'] == "N/A":
                        simple_database.update_paper_ai_analysis(
                            pmid=paper['pmid'],
                            ai_is_invention_candidate=False,
                            ai_confidence=0.0,
                            ai_reasoning="Abstract missing or N/A."
                        )
                        continue
                    
                    ai_result = ai_analyzer.analyze_abstract_with_llm(paper['abstract'])
                    if ai_result:
                        simple_database.update_paper_ai_analysis(
                            pmid=paper['pmid'],
                            ai_is_invention_candidate=ai_result.get('is_potential_invention'),
                            ai_confidence=ai_result.get('confidence_score'),
                            ai_reasoning=ai_result.get('reasoning')
                        )
                        analyzed_count += 1
            
            self.progress_update.emit(f"AI analysis completed. Papers analyzed: {analyzed_count}")
        
        self.finished.emit({"operation": "fetch", "results": batch_results})
    
    def run_analyze_operation(self):
        if not ai_analyzer.llm_client:
            self.error.emit("AI Provider not configured. Check API key settings.")
            return
        
        papers_to_analyze = simple_database.get_all_papers()
        analyzed_count = 0
        
        for paper in papers_to_analyze:
            if paper.get("ai_is_invention_candidate") is None:
                self.progress_update.emit(f"Analyzing PMID: {paper['pmid']}")
                
                if not paper['abstract'] or paper['abstract'] == "N/A":
                    simple_database.update_paper_ai_analysis(
                        pmid=paper['pmid'],
                        ai_is_invention_candidate=False,
                        ai_confidence=0.0,
                        ai_reasoning="Abstract missing or N/A."
                    )
                    continue
                
                ai_result = ai_analyzer.analyze_abstract_with_llm(paper['abstract'])
                if ai_result:
                    simple_database.update_paper_ai_analysis(
                        pmid=paper['pmid'],
                        ai_is_invention_candidate=ai_result.get('is_potential_invention'),
                        ai_confidence=ai_result.get('confidence_score'),
                        ai_reasoning=ai_result.get('reasoning')
                    )
                    analyzed_count += 1
        
        self.progress_update.emit(f"Analysis completed. Papers analyzed: {analyzed_count}")
        self.finished.emit({"operation": "analyze", "analyzed_count": analyzed_count})
    
    def run_export_operation(self):
        filename = self.kwargs.get('filename', config.CSV_EXPORT_FILENAME)
        self.progress_update.emit(f"Exporting to {filename}...")
        
        cli_main.export_flagged_papers_to_csv(filename)
        
        self.progress_update.emit(f"Export completed: {filename}")
        self.finished.emit({"operation": "export", "filename": filename})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic Publication Search Tool")
        self.setGeometry(100, 100, 1400, 1000)  # Larger window
        
        # Set larger default font
        font = QFont()
        font.setPointSize(11)  # Larger font size
        self.setFont(font)
        QApplication.instance().setFont(font)
        
        # Initialize database
        simple_database.initialize_database()
        
        # Setup UI
        self.setup_ui()
        
        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_database_view)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        # Load initial data
        self.refresh_database_view()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.setup_search_tab()
        self.setup_analysis_tab()
        self.setup_results_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_search_tab(self):
        """Setup the search and fetch tab"""
        search_widget = QWidget()
        layout = QVBoxLayout(search_widget)
        
        # Search parameters group
        search_group = QGroupBox("Search Parameters")
        search_layout = QVBoxLayout(search_group)
        
        # Search term
        search_term_layout = QHBoxLayout()
        search_term_layout.addWidget(QLabel("Search Term:"))
        self.search_term_input = QLineEdit(config.SEARCH_TERM_AFFILIATION)
        self.search_term_input.setMinimumHeight(30)  # Larger input field
        search_term_layout.addWidget(self.search_term_input)
        search_layout.addLayout(search_term_layout)
        
        # Number of papers
        num_papers_layout = QHBoxLayout()
        num_papers_layout.addWidget(QLabel("Number of Papers:"))
        self.num_papers_input = QSpinBox()
        self.num_papers_input.setRange(1, 1000)
        self.num_papers_input.setValue(config.DEFAULT_MAX_PAPERS_TO_PROCESS)
        self.num_papers_input.setMinimumHeight(30)  # Larger spinbox
        self.num_papers_input.setMinimumWidth(100)
        num_papers_layout.addWidget(self.num_papers_input)
        num_papers_layout.addStretch()
        search_layout.addLayout(num_papers_layout)
        
        # Year filter
        year_filter_layout = QHBoxLayout()
        year_filter_layout.addWidget(QLabel("Filter by Years:"))
        self.year_filter_input = QSpinBox()
        self.year_filter_input.setRange(0, 50)
        self.year_filter_input.setValue(0)
        self.year_filter_input.setSpecialValueText("All Years")
        self.year_filter_input.setMinimumHeight(30)  # Larger spinbox
        self.year_filter_input.setMinimumWidth(100)
        year_filter_layout.addWidget(self.year_filter_input)
        year_filter_layout.addStretch()
        search_layout.addLayout(year_filter_layout)
        
        # AI analysis option
        self.ai_analysis_checkbox = QCheckBox("Enable AI Analysis")
        self.ai_analysis_checkbox.setChecked(True)
        search_layout.addWidget(self.ai_analysis_checkbox)
        
        layout.addWidget(search_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("Fetch Papers")
        self.fetch_button.setMinimumHeight(40)  # Larger button
        self.fetch_button.setMinimumWidth(120)
        self.fetch_button.clicked.connect(self.start_fetch_operation)
        button_layout.addWidget(self.fetch_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Progress output
        self.fetch_output = QTextEdit()
        self.fetch_output.setReadOnly(True)
        self.fetch_output.setMinimumHeight(200)  # Larger text area
        layout.addWidget(self.fetch_output)
        
        self.tab_widget.addTab(search_widget, "Search & Fetch")
    
    def setup_analysis_tab(self):
        """Setup the AI analysis tab"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Analysis controls
        controls_group = QGroupBox("AI Analysis Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # AI provider status
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("AI Provider:"))
        self.provider_label = QLabel(config.LLM_PROVIDER.upper())
        provider_layout.addWidget(self.provider_label)
        self.provider_status = QLabel("●")
        if ai_analyzer.llm_client:
            self.provider_status.setStyleSheet("color: green")
            self.provider_status.setText("● Connected")
        else:
            self.provider_status.setStyleSheet("color: red")
            self.provider_status.setText("● Not Connected")
        provider_layout.addWidget(self.provider_status)
        provider_layout.addStretch()
        controls_layout.addLayout(provider_layout)
        
        # Analysis button
        self.analyze_button = QPushButton("Analyze All Unanalyzed Papers")
        self.analyze_button.setMinimumHeight(40)  # Larger button
        self.analyze_button.setMinimumWidth(200)
        self.analyze_button.clicked.connect(self.start_analyze_operation)
        controls_layout.addWidget(self.analyze_button)
        
        layout.addWidget(controls_group)
        
        # Analysis output
        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setMinimumHeight(200)  # Larger text area
        layout.addWidget(self.analysis_output)
        
        self.tab_widget.addTab(analysis_widget, "AI Analysis")
    
    def setup_results_tab(self):
        """Setup the results and database viewer tab"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.clicked.connect(self.refresh_database_view)
        controls_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton("Export Flagged Papers")
        self.export_button.setMinimumHeight(35)
        self.export_button.clicked.connect(self.export_papers)
        controls_layout.addWidget(self.export_button)
        
        self.view_all_checkbox = QCheckBox("View All Papers")
        self.view_all_checkbox.stateChanged.connect(self.refresh_database_view)
        controls_layout.addWidget(self.view_all_checkbox)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setMinimumHeight(400)  # Larger table
        # Set larger row height
        self.results_table.verticalHeader().setDefaultSectionSize(30)
        layout.addWidget(self.results_table)
        
        # Summary
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)
        
        self.tab_widget.addTab(results_widget, "Results")
    
    def setup_settings_tab(self):
        """Setup the settings tab"""
        settings_widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidget(settings_widget)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(settings_widget)
        
        # API Settings
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout(api_group)  # Use form layout for better organization
        
        # LLM Provider
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["openai", "anthropic"])
        self.llm_provider_combo.setCurrentText(config.LLM_PROVIDER)
        self.llm_provider_combo.setMinimumHeight(30)
        api_layout.addRow("LLM Provider:", self.llm_provider_combo)
        
        # OpenAI API Key
        openai_key_layout = QHBoxLayout()
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.Password)
        self.openai_key_input.setMinimumHeight(30)
        self.openai_key_input.setPlaceholderText("Enter OpenAI API Key")
        if config.OPENAI_API_KEY:
            self.openai_key_input.setText(config.OPENAI_API_KEY)
        openai_key_layout.addWidget(self.openai_key_input)
        
        openai_save_btn = QPushButton("Save")
        openai_save_btn.setMinimumHeight(30)
        openai_save_btn.clicked.connect(lambda: self.save_api_key('openai', self.openai_key_input.text()))
        openai_key_layout.addWidget(openai_save_btn)
        
        openai_toggle_btn = QPushButton("Show/Hide")
        openai_toggle_btn.setMinimumHeight(30)
        openai_toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(self.openai_key_input))
        openai_key_layout.addWidget(openai_toggle_btn)
        
        openai_widget = QWidget()
        openai_widget.setLayout(openai_key_layout)
        api_layout.addRow("OpenAI API Key:", openai_widget)
        
        # Anthropic API Key
        anthropic_key_layout = QHBoxLayout()
        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setEchoMode(QLineEdit.Password)
        self.anthropic_key_input.setMinimumHeight(30)
        self.anthropic_key_input.setPlaceholderText("Enter Anthropic API Key")
        if config.ANTHROPIC_API_KEY:
            self.anthropic_key_input.setText(config.ANTHROPIC_API_KEY)
        anthropic_key_layout.addWidget(self.anthropic_key_input)
        
        anthropic_save_btn = QPushButton("Save")
        anthropic_save_btn.setMinimumHeight(30)
        anthropic_save_btn.clicked.connect(lambda: self.save_api_key('anthropic', self.anthropic_key_input.text()))
        anthropic_key_layout.addWidget(anthropic_save_btn)
        
        anthropic_toggle_btn = QPushButton("Show/Hide")
        anthropic_toggle_btn.setMinimumHeight(30)
        anthropic_toggle_btn.clicked.connect(lambda: self.toggle_password_visibility(self.anthropic_key_input))
        anthropic_key_layout.addWidget(anthropic_toggle_btn)
        
        anthropic_widget = QWidget()
        anthropic_widget.setLayout(anthropic_key_layout)
        api_layout.addRow("Anthropic API Key:", anthropic_widget)
        
        # NCBI Settings
        self.ncbi_email_input = QLineEdit(config.NCBI_EMAIL or "")
        self.ncbi_email_input.setMinimumHeight(30)
        ncbi_save_btn = QPushButton("Save")
        ncbi_save_btn.setMinimumHeight(30)
        ncbi_save_btn.clicked.connect(lambda: self.save_ncbi_email(self.ncbi_email_input.text()))
        
        ncbi_layout = QHBoxLayout()
        ncbi_layout.addWidget(self.ncbi_email_input)
        ncbi_layout.addWidget(ncbi_save_btn)
        ncbi_widget = QWidget()
        ncbi_widget.setLayout(ncbi_layout)
        api_layout.addRow("NCBI Email:", ncbi_widget)
        
        layout.addWidget(api_group)
        
        # Database info
        db_group = QGroupBox("Database Information")
        db_layout = QFormLayout(db_group)
        
        db_path_label = QLabel(simple_database.DATABASE_PATH)
        db_path_label.setWordWrap(True)
        db_layout.addRow("Database Path:", db_path_label)
        
        layout.addWidget(db_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(scroll, "Settings")
    
    def start_fetch_operation(self):
        """Start the fetch operation in a background thread"""
        self.fetch_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.fetch_output.clear()
        
        # Get parameters
        search_term = self.search_term_input.text()
        num_papers = self.num_papers_input.value()
        year_filter = self.year_filter_input.value() if self.year_filter_input.value() > 0 else None
        analyze_with_ai = self.ai_analysis_checkbox.isChecked()
        
        # Start worker thread
        self.worker = WorkerThread(
            "fetch",
            search_term=search_term,
            num_papers=num_papers,
            year_filter=year_filter,
            analyze_with_ai=analyze_with_ai
        )
        self.worker.progress_update.connect(self.update_fetch_progress)
        self.worker.finished.connect(self.fetch_finished)
        self.worker.error.connect(self.operation_error)
        self.worker.start()
    
    def start_analyze_operation(self):
        """Start the analyze operation in a background thread"""
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.analysis_output.clear()
        
        self.worker = WorkerThread("analyze")
        self.worker.progress_update.connect(self.update_analysis_progress)
        self.worker.finished.connect(self.analyze_finished)
        self.worker.error.connect(self.operation_error)
        self.worker.start()
    
    def export_papers(self):
        """Export flagged papers to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Flagged Papers", 
            config.CSV_EXPORT_FILENAME, 
            "CSV Files (*.csv)"
        )
        
        if filename:
            self.progress_bar.setVisible(True)
            self.worker = WorkerThread("export", filename=filename)
            self.worker.progress_update.connect(self.update_status)
            self.worker.finished.connect(self.export_finished)
            self.worker.error.connect(self.operation_error)
            self.worker.start()
    
    def update_fetch_progress(self, message):
        """Update fetch progress display"""
        self.fetch_output.append(message)
        self.status_bar.showMessage(message)
    
    def update_analysis_progress(self, message):
        """Update analysis progress display"""
        self.analysis_output.append(message)
        self.status_bar.showMessage(message)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.showMessage(message)
    
    def fetch_finished(self, results):
        """Handle fetch operation completion"""
        self.fetch_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Fetch operation completed")
        self.refresh_database_view()
    
    def analyze_finished(self, results):
        """Handle analysis operation completion"""
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Analysis operation completed")
        self.refresh_database_view()
    
    def export_finished(self, results):
        """Handle export operation completion"""
        self.progress_bar.setVisible(False)
        filename = results.get('filename', 'export.csv')
        self.status_bar.showMessage(f"Export completed: {filename}")
        QMessageBox.information(self, "Export Complete", f"Papers exported to: {filename}")
    
    def operation_error(self, error_message):
        """Handle operation errors"""
        self.fetch_button.setEnabled(True)
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Operation failed")
        QMessageBox.critical(self, "Operation Error", error_message)
    
    def refresh_database_view(self):
        """Refresh the database view table"""
        try:
            papers = simple_database.get_all_papers()
            
            # Check if papers is None or empty
            if papers is None:
                papers = []
            
            # Filter papers if not viewing all
            if not self.view_all_checkbox.isChecked():
                papers = [p for p in papers if p and p.get('ai_is_invention_candidate') is True]
            
            # Setup table
            columns = ['PMID', 'Title', 'Authors', 'Publication Date', 'AI Flag', 'AI Confidence', 'AI Reasoning']
            self.results_table.setColumnCount(len(columns))
            self.results_table.setHorizontalHeaderLabels(columns)
            
            if papers and len(papers) > 0:
                self.results_table.setRowCount(len(papers))
                
                for row, paper in enumerate(papers):
                    if paper is None:
                        continue
                        
                    self.results_table.setItem(row, 0, QTableWidgetItem(str(paper.get('pmid', ''))))
                    
                    title = paper.get('title', '') or ''
                    title_display = title[:100] + '...' if len(title) > 100 else title
                    self.results_table.setItem(row, 1, QTableWidgetItem(title_display))
                    
                    authors = paper.get('authors', '') or ''
                    authors_display = authors[:50] + '...' if len(authors) > 50 else authors
                    self.results_table.setItem(row, 2, QTableWidgetItem(authors_display))
                    
                    self.results_table.setItem(row, 3, QTableWidgetItem(paper.get('publication_date', '') or ''))
                    
                    ai_flag = paper.get('ai_is_invention_candidate')
                    if ai_flag is True:
                        self.results_table.setItem(row, 4, QTableWidgetItem('✓ Yes'))
                    elif ai_flag is False:
                        self.results_table.setItem(row, 4, QTableWidgetItem('✗ No'))
                    else:
                        self.results_table.setItem(row, 4, QTableWidgetItem('- Not Analyzed'))
                    
                    confidence = paper.get('ai_confidence', 0) or 0
                    confidence_text = f"{confidence:.2f}" if confidence else ''
                    self.results_table.setItem(row, 5, QTableWidgetItem(confidence_text))
                    
                    reasoning = paper.get('ai_reasoning', '') or ''
                    reasoning_display = reasoning[:100] + '...' if len(reasoning) > 100 else reasoning
                    self.results_table.setItem(row, 6, QTableWidgetItem(reasoning_display))
                
                # Resize columns
                self.results_table.horizontalHeader().setStretchLastSection(True)
                self.results_table.resizeColumnsToContents()
            else:
                self.results_table.setRowCount(0)
            
            # Update summary - get fresh data
            all_papers = simple_database.get_all_papers() or []
            total_papers = len(all_papers)
            flagged_papers = len([p for p in all_papers if p and p.get('ai_is_invention_candidate') is True])
            analyzed_papers = len([p for p in all_papers if p and p.get('ai_is_invention_candidate') is not None])
            
            self.summary_label.setText(f"Total Papers: {total_papers} | Analyzed: {analyzed_papers} | Flagged as Inventions: {flagged_papers}")
            
        except Exception as e:
            print(f"Error refreshing database view: {e}")
            # Set empty table on error
            self.results_table.setRowCount(0)
            self.summary_label.setText("Error loading data from database")
    
    def toggle_password_visibility(self, line_edit):
        """Toggle password visibility for API key fields"""
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.Password)
    
    def save_api_key(self, provider, api_key):
        """Save API key to .env file"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            
            # Read existing .env file
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add the API key
            key_name = f"{provider.upper()}_API_KEY"
            key_line = f'{key_name}="{api_key}"\n'
            
            # Find and replace existing key or add new one
            found = False
            for i, line in enumerate(env_lines):
                if line.startswith(f'{key_name}='):
                    env_lines[i] = key_line
                    found = True
                    break
            
            if not found:
                env_lines.append(key_line)
            
            # Write back to file
            with open(env_path, 'w') as f:
                f.writelines(env_lines)
            
            QMessageBox.information(self, "Success", f"{provider.upper()} API key saved successfully! Please restart the application for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API key: {str(e)}")
    
    def save_ncbi_email(self, email):
        """Save NCBI email to .env file"""
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            
            # Read existing .env file
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add the email
            key_line = f'NCBI_EMAIL="{email}"\n'
            
            # Find and replace existing email or add new one
            found = False
            for i, line in enumerate(env_lines):
                if line.startswith('NCBI_EMAIL='):
                    env_lines[i] = key_line
                    found = True
                    break
            
            if not found:
                env_lines.append(key_line)
            
            # Write back to file
            with open(env_path, 'w') as f:
                f.writelines(env_lines)
            
            QMessageBox.information(self, "Success", "NCBI email saved successfully! Please restart the application for changes to take effect.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save NCBI email: {str(e)}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Academic Publication Search Tool")
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()