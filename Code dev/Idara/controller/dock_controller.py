from PyQt6.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class DockController(QDockWidget):
    def __init__(self, navigation_callback):
        super().__init__("Menu")
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetMovable |
                QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )

        #Travar Menu na esquerda
        #self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        
        self.buttons = {}

        container = QWidget()
        layout = QVBoxLayout()

        # Botões de navegação
        self.buttons["dashboard"] = QPushButton("Dashboard")
        self.buttons["members"] = QPushButton("Membros")
        self.buttons["projects"] = QPushButton("Projetos")
        self.buttons["services"] = QPushButton("Serviços")
        self.buttons["perfil_membro"] = QPushButton("Perfil Membro")

        for key, btn in self.buttons.items():
            layout.addWidget(btn)
            btn.clicked.connect(lambda _, k=key: navigation_callback(k))

        container.setLayout(layout)
        self.setWidget(container)
        container.setStyleSheet("""
            background-color: #1F4E79;  /* Azul institucional */
        """)

        for key, btn in self.buttons.items():
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1F4E79;
                    color: white;
                    border: none;
                    padding: 10px;
                    text-align: left;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #163A5F;
                }
            """)
        

    def highlight(self, active_key):
        for key, btn in self.buttons.items():
            if key == active_key:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0D2E4E;
                        color: white;
                        font-weight: bold;
                        border-left: 4px solid #00AEEF;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1F4E79;
                        color: white;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #163A5F;
                    }
                """)