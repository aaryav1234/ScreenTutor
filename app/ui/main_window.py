import sys
import io
import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame,
    QComboBox,
    QListWidget,
    QStackedWidget,
    QSplitter,
    QGraphicsDropShadowEffect,
    QSizeGrip
)
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QImage, QFont, QCursor

from app.managers.screen_capture import capture_screen
from app.backend.ocr.ocr_engine import extract_text
from app.backend.ai.ai_client import ask_solution, ask_hint, generate_practice_questions
from app.backend.memory.question_memory import QuestionMemory
from app.backend.memory.history_manager import HistoryManager

# --- ULTRA-PREMIUM THEMES (CUSTOM PALETTE) ---
# Dark Mode: 08090A (BG), F4F7F5 (Text), A7A2A9 (Accent)
DARK_THEME = """
QWidget#MainWindow { 
    background-color: #08090A; 
    border-radius: 24px; 
    border: 1px solid #A7A2A9;
}
QLabel { color: #F4F7F5; font-family: 'Bungee', -apple-system, sans-serif; font-size: 13px; }
QLabel#titleLabel { font-family: 'Bungee'; font-size: 28px; font-weight: 900; color: #F4F7F5; letter-spacing: -1px; }
QLabel#statusLabel { font-family: 'Bungee'; color: #A7A2A9; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }

QTextEdit { 
    background-color: #08090A; 
    border: 2px solid #A7A2A9; 
    border-radius: 18px; 
    color: #F4F7F5; 
    padding: 18px; 
    font-family: 'Bungee';
    font-size: 14px;
    line-height: 1.6;
}

QListWidget { background-color: transparent; border: none; color: #F4F7F5; }
QListWidget::item { padding: 12px; border-radius: 14px; margin-bottom: 6px; background-color: #08090A; border: 1px solid #A7A2A9; }
QListWidget::item:selected { background-color: #A7A2A9; color: #08090A; font-weight: 800; }

QPushButton { font-family: 'Bungee'; height: 48px; border-radius: 14px; font-weight: 800; font-size: 13px; border: none; color: #F4F7F5; background-color: #A7A2A9; }
QPushButton#ctrlBtn { background: transparent; color: #A7A2A9; font-size: 22px; }
QPushButton#solveBtn { background-color: #A7A2A9; color: #08090A; }
QPushButton#hintBtn { background-color: transparent; border: 1px solid #A7A2A9; color: #F4F7F5; }
QPushButton#practiceBtn { background-color: transparent; border: 1px solid #A7A2A9; color: #F4F7F5; }
QPushButton#exportBtn { background-color: #A7A2A9; color: #08090A; }

QPushButton#themeBtn, QPushButton#toggleBtn { background: transparent; color: #F4F7F5; border-radius: 12px; border: 1px solid #A7A2A9; }
QPushButton#switchBtn { background: transparent; color: #A7A2A9; text-decoration: underline; font-weight: bold; }
"""

# Light Mode: D7D5D8 (BG), D0DCD4 (Secondary?), F4F5F6 (Highlight?)
LIGHT_THEME = """
QWidget#MainWindow { 
    background-color: #F4F5F6; 
    border-radius: 24px; 
    border: 2px solid #D7D5D8;
}
QLabel { color: #555555; font-family: 'Bungee', -apple-system, sans-serif; font-size: 13px; }
QLabel#titleLabel { font-family: 'Bungee'; font-size: 28px; font-weight: 900; color: #333333; letter-spacing: -1px; }
QLabel#statusLabel { font-family: 'Bungee'; color: #888888; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }

QTextEdit { 
    background-color: #FFFFFF; 
    border: 2px solid #D7D5D8; 
    border-radius: 18px; 
    color: #333333; 
    padding: 18px; 
    font-family: 'Bungee';
    font-size: 14px;
}

QListWidget { background-color: transparent; border: none; color: #333333; }
QListWidget::item { padding: 12px; border-radius: 14px; margin-bottom: 6px; background-color: #D0DCD4; }
QListWidget::item:selected { background-color: #D7D5D8; color: #333333; font-weight: 800; }

QPushButton { font-family: 'Bungee'; height: 48px; border-radius: 14px; font-weight: 800; font-size: 13px; color: #333333; border: none; background-color: #D7D5D8; }
QPushButton#solveBtn { background-color: #D7D5D8; }
QPushButton#hintBtn { background-color: #D0DCD4; }
QPushButton#themeBtn, QPushButton#toggleBtn { background: white; color: #333333; border: 2px solid #D7D5D8; border-radius: 12px; }
QPushButton#switchBtn { background: transparent; color: #888888; text-decoration: underline; font-weight: bold; }
"""

class SnippingWidget(QWidget):
    snippet_captured = pyqtSignal(tuple)

    def __init__(self, background_pixmap):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setCursor(Qt.CrossCursor)
        self.background_pixmap = background_pixmap
        screen_geo = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geo)
        self.start_pos = None
        self.end_pos = None

    def mousePressEvent(self, event):
        self.start_pos = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.start_pos and self.end_pos:
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())
            print(f"DEBUG: Snipping finished. Region: ({x1},{y1}) to ({x2},{y2})")
            if x2 - x1 > 5 and y2 - y1 > 5:
                print("DEBUG: Emitting snippet_captured signal")
                self.snippet_captured.emit((x1, y1, x2, y2))
            else:
                print("DEBUG: Selection too small, ignoring.")
        self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw the actual screen contents first
        painter.drawPixmap(self.rect(), self.background_pixmap)
        
        # Draw a semi-transparent black overlay to 'dim' the screen
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        
        if self.start_pos and self.end_pos:
            selection_rect = QRect(self.start_pos, self.end_pos)
            
            # Clear the area within the selection rect so it looks 'highlighted'
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawRect(selection_rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # Draw a bright indigo border around the selection
            painter.setPen(QPen(QColor(99, 102, 241), 3)) 
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection_rect)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("ScreenTutor")
        self.setMinimumSize(600, 600)
        self.resize(850, 750)
        
        self.is_dark = True
        self.setStyleSheet(DARK_THEME)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.memory = QuestionMemory()
        self.history = HistoryManager()
        self.last_question = None
        self.current_mode = None
        
        self.setup_ui()

    def setup_ui(self):
        # Master layout for the top-level window
        self.master_layout = QVBoxLayout(self)
        # Invisible 10px margin around the app for easy resizing
        self.master_layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setObjectName("MainWindow")
        self.master_layout.addWidget(self.container)
        
        main_layout = QHBoxLayout(self.container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # --- LEFT SIDEBAR (Collapsible) ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(350)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 15, 0)
        
        side_title = QLabel("PAST QUERIES")
        side_title.setObjectName("statusLabel")
        sidebar_layout.addWidget(side_title)
        
        self.history_list = QListWidget()
        self.history_list.setWordWrap(True) # Enable multi-line text
        self.history_list.setTextElideMode(Qt.ElideNone) # Don't cut off with ...
        self.history_list.itemClicked.connect(self.load_from_history)
        self.history_list.setCursor(Qt.PointingHandCursor)
        sidebar_layout.addWidget(self.history_list)
        
        for q in self.history.get_all_questions()[-15:]:
            self.history_list.addItem(q) # Show full question
            
        main_layout.addWidget(self.sidebar)

        # --- RIGHT CONTENT ---
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Custom Header
        header = QHBoxLayout()
        
        # Sidebar Toggle
        self.toggle_btn = QPushButton("≡")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedSize(35, 35)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        header.addWidget(self.toggle_btn)

        title_vbox = QVBoxLayout()
        title = QLabel("ScreenTutor")
        title.setObjectName("titleLabel")
        title_vbox.addWidget(title)
        
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setObjectName("statusLabel")
        title_vbox.addWidget(self.status_label)
        header.addLayout(title_vbox)
        
        header.addStretch()
        
        # Theme Switch
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.setFixedSize(35, 35)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_btn)

        # Controls
        controls = QHBoxLayout()
        controls.setSpacing(5)
        min_btn = QPushButton("−")
        min_btn.setObjectName("ctrlBtn")
        min_btn.setFixedSize(30, 30)
        min_btn.clicked.connect(self.showMinimized)
        close_btn = QPushButton("×")
        close_btn.setObjectName("ctrlBtn")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        controls.addWidget(min_btn)
        controls.addWidget(close_btn)
        header.addLayout(controls)
        layout.addLayout(header)

        # Output Area
        self.output_box = QTextEdit()
        self.output_box.setPlaceholderText("Capture a question to begin...")
        self.output_box.setReadOnly(False) # Now editable as requested
        layout.addWidget(self.output_box)

        # Buttons
        btn_grid = QVBoxLayout()
        btn_grid.setSpacing(10)
        
        row1 = QHBoxLayout()
        self.solve_btn = QPushButton("GET FULL SOLUTION")
        self.solve_btn.setObjectName("solveBtn")
        self.solve_btn.clicked.connect(lambda: self.start_capture("solve"))
        
        self.hint_btn = QPushButton("GET STEP HINT")
        self.hint_btn.setObjectName("hintBtn")
        self.hint_btn.clicked.connect(lambda: self.start_capture("hint"))
        
        row1.addWidget(self.solve_btn)
        row1.addWidget(self.hint_btn)
        btn_grid.addLayout(row1)

        row2 = QHBoxLayout()
        self.practice_btn = QPushButton("GENERATE PRACTICE")
        self.practice_btn.setObjectName("practiceBtn")
        self.practice_btn.clicked.connect(self.handle_generate_practice)
        
        self.export_btn = QPushButton("EXPORT PDF/TXT")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.clicked.connect(self.handle_export)
        self.export_btn.setEnabled(False)
        
        row2.addWidget(self.practice_btn)
        row2.addWidget(self.export_btn)
        btn_grid.addLayout(row2)
        
        layout.addLayout(btn_grid)

        # DESCRIPTIVE SWITCH
        self.switch_btn = QPushButton("")
        self.switch_btn.setObjectName("switchBtn")
        self.switch_btn.setVisible(False)
        self.switch_btn.clicked.connect(self.handle_switch)
        layout.addWidget(self.switch_btn)

        # Resize Grip
        resize_layout = QHBoxLayout()
        resize_layout.addStretch()
        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setStyleSheet("background: transparent;")
        resize_layout.addWidget(self.sizegrip)
        layout.addLayout(resize_layout)

        main_layout.addWidget(content_widget)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setText("≡")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("←")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.setStyleSheet(DARK_THEME if self.is_dark else LIGHT_THEME)
        self.theme_btn.setText("🌞" if self.is_dark else "🌙")

    def load_from_history(self, item):
        q = item.text()
        if q:
            self.output_box.setText(q)
            self.output_box.setReadOnly(False)
            self.last_question = q
            self.status_label.setText("DATA RETRIEVED")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            # Check for resize
            self.resizing = self._get_resize_edge(event.pos())
            if not self.resizing:
                self.dragging = True

    def mouseMoveEvent(self, event):
        edge = self._get_resize_edge(event.pos())
        if not event.buttons() & Qt.LeftButton:
            # Change cursor based on edge
            if edge == "left" or edge == "right": self.setCursor(Qt.SizeHorCursor)
            elif edge == "top" or edge == "bottom": self.setCursor(Qt.SizeVerCursor)
            elif edge in ["topleft", "bottomright"]: self.setCursor(Qt.SizeFDiagCursor)
            elif edge in ["topright", "bottomleft"]: self.setCursor(Qt.SizeBDiagCursor)
            else: self.setCursor(Qt.ArrowCursor)
            return

        delta = event.globalPos() - self.old_pos
        if hasattr(self, "resizing") and self.resizing:
            geo = self.geometry()
            if "left" in self.resizing:
                geo.setLeft(geo.left() + delta.x())
            if "right" in self.resizing:
                geo.setRight(geo.right() + delta.x())
            if "top" in self.resizing:
                geo.setTop(geo.top() + delta.y())
            if "bottom" in self.resizing:
                geo.setBottom(geo.bottom() + delta.y())
            
            if geo.width() >= self.minimumWidth() and geo.height() >= self.minimumHeight():
                self.setGeometry(geo)
                self.old_pos = event.globalPos()
        elif hasattr(self, "dragging") and self.dragging:
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.resizing = None
        self.dragging = False

    def _get_resize_edge(self, pos):
        b = 15 # border width for resizing (includes the invisible master_layout margin)
        edge = ""
        if pos.x() < b: edge += "left"
        elif pos.x() > self.width() - b: edge += "right"
        if pos.y() < b: edge += "top"
        elif pos.y() > self.height() - b: edge += "bottom"
        return edge if edge else None

    def handle_generate_practice(self):
        history_list = self.history.get_all_questions()
        if not history_list:
            self.output_box.setText("Please capture questions first to build your profile.")
            return
        self.status_label.setText("GENERATING INTELLIGENT SET...")
        self.output_box.setText("Syncing with AI...")
        
        QTimer.singleShot(100, self._async_gen_practice)

    def _async_gen_practice(self):
        try:
            questions = generate_practice_questions(self.history.get_all_questions())
            self.output_box.setReadOnly(False)
            self.output_box.setText(questions)
            self.last_practice_set = questions
            self.export_btn.setEnabled(True)
            self.status_label.setText("GEN COMPLETE")
        except Exception as e:
            self.output_box.setText(f"Process Error: {e}")

    def handle_export(self):
        if hasattr(self, "last_practice_set"):
            path = os.path.join(os.path.expanduser("~/Desktop"), "ScreenTutor_Material.txt")
            with open(path, "w") as f: f.write(self.last_practice_set)
            self.status_label.setText(f"EXPORTED TO DESKTOP")

    def start_capture(self, mode):
        self.setWindowOpacity(0.0)
        QApplication.processEvents()
        QTimer.singleShot(250, lambda: self._do_capture(mode))

    def _do_capture(self, mode):
        print(f"DEBUG: Starting capture for mode: {mode}")
        # Capture the screen as a PIL image
        self.pil_img = capture_screen()
        print(f"DEBUG: PIL Image captured: {self.pil_img.size}")
        self.setWindowOpacity(1.0)
        
        # Convert PIL image to QPixmap for the snipper
        buffer = io.BytesIO()
        self.pil_img.save(buffer, format="PNG")
        q_img = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(q_img)
        
        self.snipper = SnippingWidget(pixmap)
        # Connect the signal correctly with debug prints
        print(f"DEBUG: Showing snipper for mode: {mode}")
        self.snipper.snippet_captured.connect(lambda bbox: self.process_capture(bbox, mode, self.pil_img))
        self.snipper.show()

    def process_capture(self, bbox, mode, full_img):
        try:
            print(f"DEBUG: Processing capture. BBox: {bbox}")
            self.status_label.setText("EXTRACTING TEXT...")
            self.output_box.setText("Reading selection...")
            QApplication.processEvents() # Force UI update
            
            # Determine effective DPR
            screen_geo = QApplication.primaryScreen().geometry()
            img_w, img_h = full_img.size
            dpr_x = img_w / screen_geo.width()
            dpr_y = img_h / screen_geo.height()
            print(f"DEBUG: Screen geo: {screen_geo.width()}x{screen_geo.height()}, PIL size: {img_w}x{img_h}, DPR: {dpr_x},{dpr_y}")
            
            x1, y1, x2, y2 = bbox
            crop = full_img.crop((
                int(x1 * dpr_x), 
                int(y1 * dpr_y), 
                int(x2 * dpr_x), 
                int(y2 * dpr_y)
            ))
            
            # Save for debugging to a reliable location
            if getattr(sys, 'frozen', False):
                base_dir = os.path.expanduser("~/Library/Application Support/ScreenTutor")
            else:
                # Use project root during development
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            data_dir = os.path.join(base_dir, "Data")
            os.makedirs(data_dir, exist_ok=True)
            debug_path = os.path.join(data_dir, "last_crop.png")
            
            crop.save(debug_path)
            print(f"DEBUG: Saved crop to {debug_path}")
            
            text = extract_text(crop).strip()
            print(f"DEBUG: OCR result: '{text[:50]}...'")
            
            if text:
                self.output_box.setReadOnly(False)
                self.output_box.setText(text)
                self.status_label.setText("TEXT VALIDATED")
                self.last_question = text
                self.history.save_question(text, mode)
                self.history_list.addItem(text)
                self.get_ai_response(text, mode)
            else:
                self.output_box.setText("Scanner failed to detect characters. Try selecting a larger/clearer area.")
                self.status_label.setText("SCAN FAILED")
                print("DEBUG: No text detected by OCR.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.output_box.setText(f"Capture Error: {e}")
            self.status_label.setText("ERROR")

    def get_ai_response(self, question, mode):
        self.current_mode = mode
        context_q = question
        
        self.status_label.setText(f"PROCESSING {mode.upper()}...")
        self.switch_btn.setText("TRY HINT" if mode == "solve" else "TRY FULL SOLUTION")
        self.switch_btn.setVisible(True)
        
        # Show "Thinking" state in the output box
        self.output_box.setText(f"QUESTION:\n{question}\n\n---\n\nAI IS THINKING...")
        
        # Small delay for UI feel
        QTimer.singleShot(100, lambda: self._async_ai_call(context_q, mode))

    def _async_ai_call(self, context_q, mode):
        try:
            ans = ask_solution(context_q) if mode == "solve" else ask_hint(context_q)
            formatted_text = f"QUESTION:\n{context_q}\n\n---\n\n{mode.upper()}:\n{ans}"
            self.output_box.setText(formatted_text)
            self.status_label.setText("PROCESS COMPLETE")
        except Exception as e:
            self.output_box.setText(f"AI Failure: {e}")

    def handle_switch(self):
        if self.last_question:
            new_mode = "solve" if self.current_mode == "hint" else "hint"
            self.get_ai_response(self.last_question, new_mode)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
