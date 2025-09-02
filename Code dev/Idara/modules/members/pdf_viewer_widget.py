from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtCore import Qt, QPointF

class PdfViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_doc = QPdfDocument(self)
        self.pdf_view = QPdfView(self)
        self.current_mode = 'width'  # 'width' ou 'page'
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.btn_fit_width = QPushButton("Largura")
        self.btn_fit_page = QPushButton("Página")
        toolbar.addWidget(self.btn_fit_width)
        toolbar.addWidget(self.btn_fit_page)
        layout.addLayout(toolbar)
        self.pdf_view.setDocument(self.pdf_doc)
        self.pdf_view.setMinimumHeight(300)
        # Exibir todas as páginas em modo contínuo (rolagem vertical)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        layout.addWidget(self.pdf_view)
        self.setLayout(layout)
        self.btn_fit_width.clicked.connect(self.set_width_mode)
        self.btn_fit_page.clicked.connect(self.set_page_mode)
        self.pdf_view.mouseDoubleClickEvent = self.toggle_mode

    def set_width_mode(self):
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.current_mode = 'width'

    def set_page_mode(self):
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.current_mode = 'page'

    def toggle_mode(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_mode == 'width':
                self.set_page_mode()
            else:
                self.set_width_mode()

    def load_pdf(self, arquivo):
        self.pdf_doc.load(arquivo)
        self.set_width_mode()
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
