from PyQt6.QtWidgets import QWidget, QHBoxLayout
from modules.members.member_view import MemberForm
from modules.members.member_list import MemberList

class MemberPanel(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.formulario = MemberForm(self.db)
        #self.lista = MemberList(self.db)

        # 🔗 Conecta o sinal de cadastro à atualização da lista
        #self.formulario.membro_salvo.connect(self.lista.carregar_membros)

        layout.addWidget(self.formulario)
        #layout.addWidget(self.lista)
