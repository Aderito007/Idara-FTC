from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QMenuBar, QHBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Idara - Gestão Institucional")
        self.setGeometry(100, 100, 1200, 700)

        # Menubar
        menubar = self.menuBar()
        menubar.addMenu("Arquivo")
        menubar.addMenu("Editar")
        menubar.addMenu("Ajuda")

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Menu lateral
        sidebar = QVBoxLayout()
        self.btn_rh = QPushButton("RH")
        self.btn_proj = QPushButton("Projetos")
        self.btn_rel = QPushButton("Relatórios")
        sidebar.addWidget(self.btn_rh)
        sidebar.addWidget(self.btn_proj)
        sidebar.addWidget(self.btn_rel)

        # Área de módulos
        self.stack = QStackedWidget()
        main_layout.addLayout(sidebar)
        main_layout.addWidget(self.stack)
        