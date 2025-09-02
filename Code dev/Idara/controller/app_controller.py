from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMenuBar, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from controller.dock_controller import DockController
from modules.dashboard.dashboard_view import DashboardView
from modules.members.member_panel import MemberPanel
from modules.projects.project_list import ProjectList
from modules.services.service_list import ServiceList
from modules.services.service_panel import ServicePanel
from state.state_manager import StateManager
from core.database import DBManager


class AppController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Idara - HR&P Management System")
        self.setGeometry(150, 50, 1000, 668)

        self.state = StateManager()
        self.db = DBManager()

        # Menubar institucional
        self._setup_menubar()

        # Área central
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Módulos
        self.modules = {
            "dashboard": DashboardView(),
            "members": MemberPanel(self.db),
            "projects": ProjectList(self.db),
            "services": ServicePanel(self.db)
        }

        for widget in self.modules.values():
            self.stack.addWidget(widget)

        # Dock lateral
        self.dock = DockController(self.navigate_to)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        # Inicializa com Dashboard
        self.navigate_to("dashboard")

        # Conectar sinais para atualização automática dos combos de serviços
        member_form = self.modules["members"].formulario
        project_list = self.modules["projects"]
        service_list = self.modules["services"]
        service_list.set_signals(member_form, project_list)

    def _setup_menubar(self):
        menubar = QMenuBar()
        menu_arquivo = menubar.addMenu("File")
        acao_sair = QAction("Exit", self)
        acao_sair.triggered.connect(self.confirmar_saida)
        menu_arquivo.addAction(acao_sair)

        menubar.addMenu("Edit")
        menubar.addMenu("Settings")
        menubar.addMenu("Help")
        self.setMenuBar(menubar)


    def navigate_to(self, module_name):
        if module_name not in self.modules:
            QMessageBox.warning(self, "Erro", f"Módulo '{module_name}' não encontrado.")
            return

        current_key = self.state.get_module()
        if current_key and current_key in self.modules:
            current_view = self.modules[current_key]
            if hasattr(current_view, "get_state"):
                self.state.save_state(current_key, current_view.get_state())

        self.state.set_module(module_name)
        new_view = self.modules[module_name]
        if hasattr(new_view, "set_state"):
            new_view.set_state(self.state.get_state(module_name))

        self.stack.setCurrentWidget(new_view)
        self.dock.highlight(module_name)

    def confirmar_saida(self):
        resposta = QMessageBox.question(
            self,
            "Shut Down - Idara",
            "Do you really want to exit the system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self.shutdown()

    def shutdown(self):
        current_key = self.state.get_module()
        if current_key and current_key in self.modules:
            current_view = self.modules[current_key]
            if hasattr(current_view, "get_state"):
                self.state.save_state(current_key, current_view.get_state())

        if hasattr(self, "db") and self.db:
            try:
                self.db.close()
            except Exception as e:
                print(f"[Idara] Erro ao fechar DB: {e}")

        QMessageBox.information(
            self,
            "Idara Encerrado",
            "Sistema encerrado com sucesso. Até breve!",
            QMessageBox.StandardButton.Ok
        )
        self.close()
