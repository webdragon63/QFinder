import sys
import requests
import time
from urllib.parse import urlparse, parse_qs, urljoin
from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QListWidget, QListWidgetItem, QAbstractItemView, QSplitter, QDialog, QDialogButtonBox, QComboBox
)
from PyQt5.QtGui import QFont, QGuiApplication, QColor, QPixmap

class CrawlWorker(QObject):
    result_signal = pyqtSignal(str)
    query_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    done_signal = pyqtSignal()

    def __init__(self, start_url, max_depth=2, speed_delay=0.0):
        super().__init__()
        self.start_url = start_url
        self.max_depth = max_depth
        self._abort = False
        self.speed_delay = speed_delay

    def run(self):
        visited = set()
        to_visit = [(self.start_url, 0)]
        total = 1

        while to_visit and not self._abort:
            url, depth = to_visit.pop(0)
            if url in visited or depth > self.max_depth:
                continue
            visited.add(url)
            try:
                resp = requests.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
                self.progress_signal.emit(len(visited), total)
            except Exception as e:
                self.result_signal.emit(f"<span style='color:#ff266e;'>[ERROR] {url}: {e}</span>")
                continue

            for a in soup.find_all("a", href=True):
                if self._abort:
                    self.done_signal.emit()
                    return
                link = a['href']
                full_url = urljoin(url, link)
                parsed = urlparse(full_url)
                queries = parse_qs(parsed.query)
                if queries and full_url not in visited:
                    self.result_signal.emit(
                        f"<span style='color:#26ff84;'>[QUERY]</span> "
                        f"<span style='color:#26ffe6;'>{full_url}</span>"
                    )
                    self.query_signal.emit(full_url)
                if parsed.netloc == urlparse(self.start_url).netloc and full_url not in visited:
                    to_visit.append((full_url, depth + 1))
                    total += 1
                time.sleep(self.speed_delay)

            for form in soup.find_all("form"):
                if self._abort:
                    self.done_signal.emit()
                    return
                action = form.get("action", "")
                method = form.get("method", "get").upper()
                form_url = urljoin(url, action)
                inputs = [i.get("name") for i in form.find_all("input") if i.get("name")]
                if inputs:
                    self.result_signal.emit(
                        f"<span style='color:#ff266e;'>[FORM]</span> "
                        f"<span style='color:#26ffe6;'>{method} {form_url}</span> "
                        f"<span style='color:#26ff84;'>params: {', '.join(inputs)}</span>"
                    )
                time.sleep(self.speed_delay)
        self.done_signal.emit()

    def abort(self):
        self._abort = True

    def set_speed(self, speed_delay):
        self.speed_delay = speed_delay

class PopupCopied(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Copied")
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setStyleSheet("""
            QDialog {
                background-color: #242733;
                border: 2px solid #26ffe6;
                border-radius: 12px;
            }
            QLabel#mainText {
                color: #44ffd7;
                font-size: 18px;
                font-family: 'Fira Mono';
            }
            QPushButton {
                background-color: #26ffe6;
                color: #222a35;
                font-family: 'Fira Mono';
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QLabel#urlText {
                color: #26ffe6;
                font-size: 17px;
                font-family: 'Fira Mono';
            }
            QDialogButtonBox {
                background: transparent;
            }
        """)
        layout = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#242733"))
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(32, 32)
        layout.addWidget(icon_label)
        text_layout = QVBoxLayout()
        main_label = QLabel("Copied to clipboard:")
        main_label.setObjectName("mainText")
        url_label = QLabel(text)
        url_label.setObjectName("urlText")
        text_layout.addWidget(main_label)
        text_layout.addWidget(url_label)
        layout.addLayout(text_layout)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.button(QDialogButtonBox.Ok).setText("🦾 OK")
        btn_box.accepted.connect(self.accept)
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(layout)
        dialog_layout.addWidget(btn_box)
        self.setLayout(dialog_layout)
        self.setFixedWidth(440)

class PopupWarning(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Warning")
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setStyleSheet("""
            QDialog {
                background-color: #242733;
                border: 2px solid #ff266e;
                border-radius: 12px;
            }
            QLabel#mainText {
                color: #ff266e;
                font-size: 18px;
                font-family: 'Fira Mono';
            }
            QPushButton {
                background-color: #ff266e;
                color: #222a35;
                font-family: 'Fira Mono';
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QLabel#messageText {
                color: #ffd6e0;
                font-size: 17px;
                font-family: 'Fira Mono';
            }
            QDialogButtonBox {
                background: transparent;
            }
        """)
        layout = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#242733"))
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(32, 32)
        layout.addWidget(icon_label)
        text_layout = QVBoxLayout()
        main_label = QLabel("Warning:")
        main_label.setObjectName("mainText")
        msg_label = QLabel(message)
        msg_label.setObjectName("messageText")
        text_layout.addWidget(main_label)
        text_layout.addWidget(msg_label)
        layout.addLayout(text_layout)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.button(QDialogButtonBox.Ok).setText("🦾 OK")
        btn_box.accepted.connect(self.accept)
        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(layout)
        dialog_layout.addWidget(btn_box)
        self.setLayout(dialog_layout)
        self.setFixedWidth(440)

class QFinder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QFinder(The Query Finder)")
        self.setGeometry(100, 100, 1300, 800)
        self.initUI()
        self.worker_thread = None
        self.worker = None

    def initUI(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #070a13; }
            QLabel { color: #26ffe6; font-size: 18px; font-family: 'Fira Mono'; }
            QLineEdit, QTextEdit {
                background-color: #0d1e28; color: #26ffe6; border: 2px solid #07c6ff;
                font-family: 'Fira Mono'; font-size: 16px;
            }
            QPushButton {
                background-color: #07c6ff; color: #222a35; border-radius: 8px;
                font-family: 'Fira Mono'; font-weight: bold; padding: 8px 20px;
            }
            QProgressBar {
                background-color: #222a35; border: 2px solid #26ffe6; color: #ffffff;
                font-family: 'Fira Mono'; font-size: 14px; text-align: center;
            }
            QListWidget {
                background-color: #0d1e28; color: #26ffe6; border: 2px solid #07c6ff;
                font-family: 'Fira Mono'; font-size: 14px;
            }
            QComboBox {
                background-color: #222a35;
                color: #26ffe6;
                border: 2px solid #26ffe6;
                font-family: 'Fira Mono';
                font-size: 16px;
                border-radius: 6px;
                padding: 4px 12px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter website URL (e.g. https://example.com)")
        url_layout.addWidget(QLabel("Website URL:"))
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)

        control_layout = QHBoxLayout()
        self.enumerate_btn = QPushButton("Start")
        self.enumerate_btn.clicked.connect(self.start_crawling)
        control_layout.addWidget(self.enumerate_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_crawling)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)

        control_layout.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Fast", "Normal", "Slow"])
        
        self.speed_combo.setStyleSheet("""
            QComboBox {
                background-color: #222a35;
                color: #26ffe6;
                border: 2px solid #26ffe6;
                font-family: 'Fira Mono';
                font-size: 16px;
                border-radius: 6px;
                padding: 4px 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2f42;
                color: #ffffff;
                selection-background-color: #26ff84; 
                selection-color: #222a35;
                font-family: 'Fira Mono';
                font-size: 16px;
            }
        """)

        
        self.speed_combo.setCurrentIndex(1)
        self.speed_combo.currentIndexChanged.connect(self.change_speed)
        control_layout.addWidget(self.speed_combo)
        main_layout.addLayout(control_layout)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)

        self.splitter = QSplitter(Qt.Horizontal)
        left_layout = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_layout.addWidget(QLabel("Query URLs & Forms:"))
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        left_layout.addWidget(self.result_box)
        self.splitter.addWidget(left_widget)

        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setMinimumWidth(320)
        right_layout.addWidget(QLabel("Found Queries:"))
        self.query_list = QListWidget()
        self.query_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.query_list.itemDoubleClicked.connect(self.copy_query_to_clipboard)
        right_layout.addWidget(self.query_list)
        self.splitter.addWidget(right_widget)

        self.splitter.setSizes([700, 700])
        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)

    def get_speed_delay(self):
        speed_map = {
            "Fast": 0.01,
            "Normal": 0.1,
            "Slow": 0.5
        }
        return speed_map[self.speed_combo.currentText()]

    def start_crawling(self):
        url = self.url_input.text().strip()
        if not url.startswith("http"):
            popup = PopupWarning("Please enter a valid URL.", parent=self)
            popup.exec_()
            return

        if self.worker_thread and self.worker_thread.isRunning():
            self.worker.abort()
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.result_box.clear()
        self.query_list.clear()
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.enumerate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        speed_delay = self.get_speed_delay()
        self.worker_thread = QThread()
        self.worker = CrawlWorker(url, max_depth=2, speed_delay=speed_delay)
        self.worker.moveToThread(self.worker_thread)
        self.worker.result_signal.connect(self.append_result)
        self.worker.query_signal.connect(self.add_query_item)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.done_signal.connect(self.crawl_done)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def stop_crawling(self):
        if self.worker and self.worker_thread and self.worker_thread.isRunning():
            self.worker.abort()
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.progress.setVisible(False)
        self.enumerate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.append_result("<span style='color:#ff266e;'>[STOPPED]</span>")

    def append_result(self, html):
        self.result_box.insertHtml(html + "<br>")
        self.result_box.moveCursor(self.result_box.textCursor().End)

    def add_query_item(self, url):
        item = QListWidgetItem(url)
        self.query_list.addItem(item)

    def update_progress(self, current, total):
        self.progress.setMaximum(total)
        self.progress.setValue(current)

    def crawl_done(self):
        self.progress.setVisible(False)
        self.enumerate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.append_result("<span style='color:#26ffe6;'>[DONE]</span>")

    def change_speed(self):
        if self.worker:
            self.worker.set_speed(self.get_speed_delay())

    def copy_query_to_clipboard(self, item):
        QGuiApplication.clipboard().setText(item.text())
        popup = PopupCopied(item.text(), parent=self)
        popup.exec_()

    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker.abort()
            self.worker_thread.quit()
            self.worker_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QFinder()
    window.show()
    sys.exit(app.exec_())
