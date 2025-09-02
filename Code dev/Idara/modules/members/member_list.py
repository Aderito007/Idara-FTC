from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QPushButton, QMenu
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from modules.members.member_controller import MemberController
from modules.members.member_profile_form import MemberProfileForm
from modules.members.member_profile import MemberProfile


class MemberList(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.controller = MemberController(db)
        self.setWindowTitle("📋 Lista de Membros")
        self.resize(600, 400)
        self.init_ui()
        self.perfil_windows = {}  # Dict para perfis abertos por membro_id
        self.form_windows = {}    # Dict para forms abertos por membro_id

    def init_ui(self):
        layout = QVBoxLayout(self)

        botao_atualizar = QPushButton("🔄 Atualizar lista")
        botao_atualizar.clicked.connect(self.carregar_membros)
        layout.addWidget(botao_atualizar)

        self.setup_tree()
        layout.addWidget(self.tree)

        self.carregar_membros()

    def setup_tree(self):
        self.tree = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nome", "Cargo", "Email", "Telefone"])
        self.tree.setModel(self.model)
        self.tree.setRootIsDecorated(False)
        self.tree.doubleClicked.connect(self.abrir_perfil_membro)

    def abrir_perfil_membro(self, index):
        membro_id = self.obter_id_selecionado()
        if membro_id:
            if membro_id in self.perfil_windows:
                # Se já existe, traz para frente
                self.perfil_windows[membro_id].raise_()
                self.perfil_windows[membro_id].activateWindow()
            else:
                perfil = MemberProfile(membro_id, self.db, parent_list=self)
                perfil.show()
                self.perfil_windows[membro_id] = perfil
                perfil.destroyed.connect(lambda: self.perfil_windows.pop(membro_id, None))

    def carregar_membros(self):
        self.model.removeRows(0, self.model.rowCount())

        membros = self.controller.listar_membros()
        if not membros:
            vazio = QStandardItem("Nenhum membro encontrado")
            vazio.setEditable(False)
            self.model.appendRow([vazio] + [QStandardItem() for _ in range(3)])
            return

        for membro in membros:
            linha = [
                QStandardItem(membro.get("nome", "")),
                QStandardItem(membro.get("cargo", "")),
                QStandardItem(membro.get("email", "")),
                QStandardItem(membro.get("telefone", ""))
            ]
            for item in linha:
                item.setEditable(False)
            self.model.appendRow(linha)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        ver_acao = menu.addAction("Ver Perfil")
        adicionar_acao = menu.addAction("Adicionar Dados")
        excluir_acao = menu.addAction("Excluir Membro")

        acao = menu.exec(event.globalPos())
        membro_id = self.obter_id_selecionado()
        if not membro_id:
            return

        if acao == ver_acao:
            if membro_id in self.perfil_windows:
                self.perfil_windows[membro_id].raise_()
                self.perfil_windows[membro_id].activateWindow()
            else:
                perfil = MemberProfile(membro_id, self.db, parent_list=self)
                perfil.show()
                self.perfil_windows[membro_id] = perfil
                perfil.destroyed.connect(lambda: self.perfil_windows.pop(membro_id, None))
        elif acao == adicionar_acao:
            if membro_id in self.form_windows:
                self.form_windows[membro_id].raise_()
                self.form_windows[membro_id].activateWindow()
            else:
                form = MemberProfileForm(membro_id, self.db)
                form.show()
                self.form_windows[membro_id] = form
                form.destroyed.connect(lambda: self.form_windows.pop(membro_id, None))
        elif acao == excluir_acao:
            from PyQt6.QtWidgets import QMessageBox
            confirm = QMessageBox.question(self, "Excluir Membro", "Tem certeza que deseja excluir este membro?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.controller.excluir_membro(membro_id)
                self.carregar_membros()
                QMessageBox.information(self, "Excluído", "Membro excluído com sucesso.")

    def obter_id_selecionado(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            return None

        nome_item = self.model.item(index.row(), 0)
        if not nome_item:
            return None

        nome = nome_item.text()
        membro = self.controller.buscar_por_nome(nome)
        return membro.get("id") if membro else None
