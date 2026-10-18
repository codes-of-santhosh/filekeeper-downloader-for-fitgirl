import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QLabel, QTableView, QHeaderView,
    QFileDialog, QSpinBox, QComboBox, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .file_table_model import FileTableModel
from .workers import PasteWorker, ResolverWorker, PollerWorker
from ..downloader import Downloader
from ..settings import AppSettings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileKeeper Batch Downloader for FitGirl")
        self.resize(850, 620)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.settings = AppSettings()
        self.downloader = Downloader()
        
        self.setup_ui()
        self.load_settings()
        
        try:
            self.downloader.start_aria2()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
        self.active_downloads = {} # gid -> row index
        
        self.poller = PollerWorker(self.downloader, self.active_downloads)
        self.poller.stats_updated_signal.connect(self.on_poll_updates)
        self.poller.start()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        row1 = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste FitGirl URL here...")
        self.btn_fetch = QPushButton("Fetch Links")
        self.btn_fetch.clicked.connect(self.on_fetch_clicked)
        self.lbl_status = QLabel("Ready")
        row1.addWidget(self.url_input)
        row1.addWidget(self.btn_fetch)
        row1.addWidget(self.lbl_status)
        layout.addLayout(row1)
        
        row_sel = QHBoxLayout()
        self.btn_sel_all = QPushButton("Select All")
        self.btn_desel_all = QPushButton("Deselect All")
        self.btn_inv_sel = QPushButton("Invert Selection")
        self.model = FileTableModel()
        self.btn_sel_all.clicked.connect(lambda: self.model.set_all_checked(True))
        self.btn_desel_all.clicked.connect(lambda: self.model.set_all_checked(False))
        self.btn_inv_sel.clicked.connect(self.model.invert_selection)
        row_sel.addWidget(self.btn_sel_all)
        row_sel.addWidget(self.btn_desel_all)
        row_sel.addWidget(self.btn_inv_sel)
        row_sel.addStretch()
        layout.addLayout(row_sel)
        
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        row3 = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.on_browse)
        self.spin_concurrent = QSpinBox()
        self.spin_concurrent.setRange(1, 10)
        self.spin_concurrent.setPrefix("Concurrent: ")
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["Unlimited", "1 MB/s", "5 MB/s", "10 MB/s"])
        row3.addWidget(QLabel("Download Folder:"))
        row3.addWidget(self.dir_input)
        row3.addWidget(self.btn_browse)
        row3.addWidget(self.spin_concurrent)
        row3.addWidget(self.combo_speed)
        layout.addLayout(row3)
        
        row4 = QHBoxLayout()
        self.btn_start = QPushButton("Start Download")
        self.btn_start.clicked.connect(self.on_start_download)
        self.btn_pause = QPushButton("Pause All")
        self.btn_pause.clicked.connect(self.downloader.pause_all)
        self.btn_resume = QPushButton("Resume All")
        self.btn_resume.clicked.connect(self.downloader.resume_all)
        self.btn_cancel = QPushButton("Cancel All")
        self.btn_cancel.clicked.connect(self.downloader.cancel_all)
        row4.addWidget(self.btn_start)
        row4.addWidget(self.btn_pause)
        row4.addWidget(self.btn_resume)
        row4.addWidget(self.btn_cancel)
        layout.addLayout(row4)
        
        self.global_progress = QProgressBar()
        self.lbl_global_stats = QLabel("0/0 files | 0 B/s | ETA: --")
        layout.addWidget(self.global_progress)
        layout.addWidget(self.lbl_global_stats)
        
    def load_settings(self):
        self.url_input.setText(self.settings.get_last_paste_url())
        self.dir_input.setText(self.settings.get_download_dir())
        self.spin_concurrent.setValue(self.settings.get_max_concurrent())
        self.combo_speed.setCurrentIndex(self.settings.get_speed_limit_index())
        
    def save_settings(self):
        self.settings.set_last_paste_url(self.url_input.text())
        self.settings.set_download_dir(self.dir_input.text())
        self.settings.set_max_concurrent(self.spin_concurrent.value())
        self.settings.set_speed_limit_index(self.combo_speed.currentIndex())
        
    def on_browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.dir_input.text())
        if directory:
            self.dir_input.setText(directory)
            
    def set_gui_enabled(self, enabled: bool):
        self.url_input.setEnabled(enabled)
        self.btn_fetch.setEnabled(enabled)
        self.btn_start.setEnabled(enabled)
        
    def on_fetch_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            return
            
        self.save_settings()
        self.set_gui_enabled(False)
        self.lbl_status.setText("Fetching paste...")
        
        self.paste_worker = PasteWorker(url)
        self.paste_worker.finished_signal.connect(self.on_paste_fetched)
        self.paste_worker.error_signal.connect(self.on_paste_error)
        self.paste_worker.start()
        
    def on_paste_error(self, error):
        self.lbl_status.setText(f"Error: {error}")
        self.set_gui_enabled(True)
        
    def on_paste_fetched(self, links):
        self.lbl_status.setText(f"Found {len(links)} FileKeeper links. Resolving...")
        self.model.set_files([]) # clear table
        
        self.resolver_worker = ResolverWorker(links)
        self.resolver_worker.progress_signal.connect(self.on_resolve_progress)
        self.resolver_worker.file_resolved_signal.connect(self.on_file_resolved)
        self.resolver_worker.finished_signal.connect(self.on_resolve_finished)
        self.resolver_worker.error_signal.connect(self.on_resolve_error)
        self.resolver_worker.start()
        
    def on_resolve_progress(self, i, total, url):
        self.lbl_status.setText(f"Resolving {i+1}/{total}...")
        
    def on_file_resolved(self, res_file):
        files = self.model.files.copy()
        files.append(res_file)
        self.model.set_files(files)
        
    def on_resolve_finished(self, resolved_files):
        self.lbl_status.setText(f"Resolved {len(resolved_files)} files ready for download.")
        self.set_gui_enabled(True)
        
    def on_resolve_error(self, error):
        self.lbl_status.setText(f"Resolver Error: {error}")
        self.set_gui_enabled(True)
        
    def on_start_download(self):
        out_dir = self.dir_input.text()
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Invalid directory: {e}")
                return
                
        self.save_settings()
        
        speed_map = {0: 0, 1: 1048576, 2: 5242880, 3: 10485760}
        speed_limit = speed_map.get(self.combo_speed.currentIndex(), 0)
        self.downloader.set_global_options(self.spin_concurrent.value(), speed_limit)
        
        selected = self.model.get_selected_files()
        for row, f in selected:
            if f.direct_url and f.status != "Complete":
                try:
                    gid = self.downloader.add_download(f.direct_url, out_dir, f.filename, referer=f.original_url)
                    f.gid = gid
                    self.active_downloads[gid] = row
                    self.model.update_file_progress(row, "Starting...", 0)
                except Exception as e:
                    self.model.update_file_progress(row, f"Error: {e}", 0)
                    
    def on_poll_updates(self, updates):
        total_speed = 0
        completed_files = 0
        
        for gid, stat in updates.items():
            row = self.active_downloads.get(gid)
            if row is None:
                continue
                
            total_speed += stat["speed"]
            if stat["total"] > 0:
                pct = (stat["completed"] / stat["total"]) * 100
            else:
                pct = 0.0
                
            display_status = stat["status"].capitalize()
            self.model.update_file_progress(row, display_status, pct)
            
            if self.model.files[row].size == "Unknown" and stat["total"] > 0:
                self.model.files[row].size = f"{stat['total']/1048576:.2f} MB"
                
            if stat["status"] == "complete":
                completed_files += 1
            elif stat["status"] == "error":
                import requests
                import re
                f = self.model.files[row]
                match = re.search(r'filekeeper\.[a-z]+/(?P<id>[^/]+)/', f.original_url)
                if match:
                    try:
                        resp = requests.post(f.original_url, data={'op': 'download2', 'id': match.group('id'), 'down_direct': '1'}, 
                                             headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=False, timeout=10)
                        if resp.status_code in [301, 302, 303]:
                            new_direct = resp.headers.get('Location')
                            try: self.downloader.aria2.remove([self.downloader.aria2.get_download(gid)])
                            except: pass
                            new_gid = self.downloader.add_download(new_direct, self.dir_input.text(), f.filename, referer=f.original_url)
                            f.gid = new_gid
                            f.direct_url = new_direct
                            self.active_downloads[new_gid] = row
                            del self.active_downloads[gid]
                            self.model.update_file_progress(row, "Auto-resuming...", pct)
                        else:
                            del self.active_downloads[gid]
                            self.model.update_file_progress(row, "Failed (Max Retries)", pct)
                    except:
                        del self.active_downloads[gid]
                        self.model.update_file_progress(row, "Failed (Network Error)", pct)
                    
        if self.active_downloads:
            self.lbl_global_stats.setText(f"{completed_files}/{len(self.active_downloads)} | {total_speed/1048576:.2f} MB/s")

    def closeEvent(self, event):
        self.poller.stop()
        self.poller.wait()
        event.accept()
