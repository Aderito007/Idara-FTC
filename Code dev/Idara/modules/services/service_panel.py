# service_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from modules.services.service_list import ServiceList
from modules.services.service_accounting import ServiceAccounting
# from .service_team import ServiceTeam
# from .service_logistics import ServiceLogistics


class ServicePanel(QWidget):
    def set_signals(self, member_form=None, project_list=None):
        # Repasse para a aba Recursos Humanos (ServiceList)
        if hasattr(self, 'rh_tab') and hasattr(self.rh_tab, 'set_signals'):
            self.rh_tab.set_signals(member_form=member_form, project_list=project_list)
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.tabs = QTabWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

        # Aba Recursos Humanos
        self.rh_tab = ServiceList(db)
        self.tabs.addTab(self.rh_tab, "Recursos Humanos")

        # Outras abas (exemplo, crie os arquivos e classes correspondentes)
        self.cont_tab = ServiceAccounting(db)
        self.tabs.addTab(self.cont_tab, "Contabilidade")
        # self.team_tab = ServiceTeam(db)
        # self.tabs.addTab(self.team_tab, "Gestão de Equipas")
        # self.log_tab = ServiceLogistics(db)
        # self.tabs.addTab(self.log_tab, "Logística")