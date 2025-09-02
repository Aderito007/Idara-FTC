from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class RelatoriosForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Módulo Relatórios"))
        self.setLayout(layout)