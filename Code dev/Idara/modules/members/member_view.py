from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QScrollArea, QGroupBox, QHBoxLayout, QTreeView, QMessageBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QDate, pyqtSignal
from modules.members.member_controller import MemberController
from modules.members.member_list import MemberList
from core.validators import campo_obrigatorio, email_valido, telefone_valido
from modules.members.combo_data_manager import (
    load_items, load_cargos, add_cargo, remove_cargo, load_items)
from modules.members.combo_data_manager import load_all, save_all


class MemberForm(QWidget):
    membro_salvo = pyqtSignal()
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.controller = MemberController(db)
        self.setWindowTitle("🧾 Cadastro de Membro")
        self.setMinimumSize(800, 500)
        self.membro_id = None
        self.init_ui()

    def init_ui(self):
        self.layout_principal = QHBoxLayout(self)

        # 🔹 Formulário com scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.layout_formulario = QVBoxLayout(self.container)

        # 📋 Dados Pessoais
        self.grupo_pessoal = QGroupBox("📋 Dados Pessoais")
        form_pessoal = QFormLayout()
        self.nome_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefone_input = QLineEdit()
        form_pessoal.addRow("Nome:", self.nome_input)
        form_pessoal.addRow("Email:", self.email_input)
        form_pessoal.addRow("Telefone:", self.telefone_input)
        self.grupo_pessoal.setLayout(form_pessoal)

        # 🏢 Departamento e Cargo
        self.grupo_cargo = QGroupBox("🏢 Departamento e Cargo")
        form_cargo = QFormLayout()

        # Departamento
        self.departamento_input = QComboBox()
        self.departamento_input.setEditable(True)
        self.departamento_input.addItems(load_items("departamentos"))
        self.departamento_input.currentTextChanged.connect(self.atualizar_cargos_por_departamento)
        # Departamento
        depto_vbox = QVBoxLayout()
        depto_vbox.addWidget(self.departamento_input)
        depto_btns_hbox = QHBoxLayout()
        btn_add_depto = QPushButton("➕ add")
        btn_add_depto.setFixedSize(64, 24)
        btn_add_depto.setToolTip("Adicionar novo departamento")
        btn_add_depto.clicked.connect(self.adicionar_departamento)
        depto_btns_hbox.addWidget(btn_add_depto)
        btn_rem_depto = QPushButton("🗑 del")
        btn_rem_depto.setFixedSize(64, 24)
        btn_rem_depto.setToolTip("Remover departamento selecionado")
        btn_rem_depto.clicked.connect(self.remover_departamento)
        depto_btns_hbox.addWidget(btn_rem_depto)
        depto_btns_hbox.addStretch()
        depto_vbox.addLayout(depto_btns_hbox)
        form_cargo.addRow("Departamento:", depto_vbox)

        # Cargo
        self.cargo_input = QComboBox()
        self.cargo_input.setEditable(True)
        departamento_inicial = self.departamento_input.currentText() or self.departamento_input.itemText(0)
        self.cargo_input.addItems(load_cargos(departamento_inicial))
        cargo_vbox = QVBoxLayout()
        cargo_vbox.addWidget(self.cargo_input)
        cargo_btns_hbox = QHBoxLayout()
        btn_add_cargo = QPushButton("➕ add")
        btn_add_cargo.setFixedSize(64, 24)
        btn_add_cargo.setToolTip("Adicionar novo cargo")
        btn_add_cargo.clicked.connect(self.adicionar_cargo)
        cargo_btns_hbox.addWidget(btn_add_cargo)
        btn_rem_cargo = QPushButton("🗑 del")
        btn_rem_cargo.setFixedSize(64, 24)
        btn_rem_cargo.setToolTip("Remover cargo selecionado")
        btn_rem_cargo.clicked.connect(self.remover_cargo)
        cargo_btns_hbox.addWidget(btn_rem_cargo)
        cargo_btns_hbox.addStretch()
        cargo_vbox.addLayout(cargo_btns_hbox)
        form_cargo.addRow("Cargo:", cargo_vbox)
        self.grupo_cargo.setLayout(form_cargo)
    
        # 📅 Dados de Entrada
        grupo_entrada = QGroupBox("📅 Dados de Entrada")
        form_entrada = QFormLayout()
        self.data_input = QDateEdit()
        self.data_input.setDate(QDate.currentDate())
        self.data_input.setCalendarPopup(True)
        form_entrada.addRow("Data de entrada:", self.data_input)
        grupo_entrada.setLayout(form_entrada)

        # 🔘 Botões organizados horizontalmente
        botao_salvar = QPushButton("💾 Salvar")
        botao_salvar.clicked.connect(self.salvar_membro)
        botao_salvar.setMinimumWidth(120)

        botao_clear = QPushButton("🧹 Limpar")
        botao_clear.clicked.connect(self.limpar_formulario)
        botao_clear.setMinimumWidth(120)

        botao_visualizar = QPushButton("📋 Visualizar Membros")
        botao_visualizar.clicked.connect(self.abrir_lista_membros)
        botao_visualizar.setMinimumWidth(160)

        hbox_botoes = QHBoxLayout()
        hbox_botoes.addWidget(botao_salvar)
        hbox_botoes.addWidget(botao_clear)
        hbox_botoes.addWidget(botao_visualizar)
        hbox_botoes.addStretch()

        self.layout_formulario.addWidget(self.grupo_pessoal)
        self.layout_formulario.addWidget(self.grupo_cargo)
        self.layout_formulario.addWidget(grupo_entrada)
        self.layout_formulario.addLayout(hbox_botoes)

        self.scroll.setWidget(self.container)
        self.layout_principal.addWidget(self.scroll)

        # 🧑‍🤝‍🧑 Lista de membros recentes
        self.tree = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nome", "Cargo"])
        self.tree.setModel(self.model)
        self.tree.setRootIsDecorated(False)
        self.tree.setMaximumWidth(300)
        self.tree.clicked.connect(self.editar_membro)
        self.layout_principal.addWidget(self.tree)

        self.atualizar_lista()

    def salvar_membro(self):
        dados = {
            "nome": self.nome_input.text().strip(),
            "email": self.email_input.text().strip(),
            "telefone": self.telefone_input.text().strip(),
            "cargo": self.cargo_input.currentText().strip(),
            "departamento": self.departamento_input.currentText(),
            "data_entrada": self.data_input.date().toString("yyyy-MM-dd")
        }

        erros = []
        for campo in ["nome", "email", "cargo"]:
            erro = campo_obrigatorio(dados[campo], campo)
            if erro:
                erros.append(erro)

        email_erro = email_valido(dados["email"])
        if email_erro:
            erros.append(email_erro)

        telefone_erro = telefone_valido(dados["telefone"])
        if telefone_erro:
            erros.append(telefone_erro)

        if erros:
            QMessageBox.warning(self, "Validação", "\n".join(erros))
            return

        try:
            if self.membro_id:
                dados["id"] = self.membro_id
                self.controller.atualizar_membro(dados)
                QMessageBox.information(self, "Atualizado", "Dados do membro atualizados com sucesso.")
            else:
                self.controller.cadastrar_membro(dados)
                QMessageBox.information(self, "Cadastrado", "Novo membro registrado com sucesso.")

            self.limpar_formulario()
            self.atualizar_lista()
            self.membro_salvo.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", str(e))


    def atualizar_lista(self):
        self.model.removeRows(0, self.model.rowCount())
        membros = self.controller.listar_membros()
        recentes = sorted(membros, key=lambda m: m.get("data_entrada", ""), reverse=True)[:12]

        for membro in reversed(recentes):
            linha = [
                QStandardItem(membro.get("nome", "")),
                QStandardItem(membro.get("cargo", ""))
            ]
            for item in linha:
                item.setEditable(False)
            self.model.appendRow(linha)

    def editar_membro(self, index):
        nome_item = self.model.item(index.row(), 0)
        if not nome_item:
            return
        nome = nome_item.text()
        membro = self.controller.buscar_por_nome(nome)
        if membro:
            self.membro_id = membro.get("id")  # ✅ Armazena ID
            self.nome_input.setText(membro.get("nome", ""))
            self.email_input.setText(membro.get("email", ""))
            self.telefone_input.setText(membro.get("telefone", ""))
            self.cargo_input.setCurrentText(membro.get("cargo", ""))
            self.departamento_input.setCurrentText(membro.get("departamento", "RH"))
            self.data_input.setDate(QDate.fromString(membro.get("data_entrada", ""), "yyyy-MM-dd"))

    def abrir_lista_membros(self):
        self.lista_window = MemberList(self.db)
        self.lista_window.show()

    def limpar_formulario(self):
        self.membro_id = None
        self.nome_input.clear()
        self.email_input.clear()
        self.telefone_input.clear()
        self.cargo_input.clear()
        self.departamento_input.setCurrentIndex(0)
        self.data_input.setDate(QDate.currentDate())


    def adicionar_departamento(self):
        novo = self.departamento_input.currentText().strip()
        if not novo:
            QMessageBox.warning(self, "Atenção", "Digite o nome do departamento para adicionar.")
            return
        data = load_all()
        departamentos = data.get("departamentos", [])
        if novo not in departamentos:
            departamentos.append(novo)
            data["departamentos"] = departamentos
            # Cria lista de cargos vazia para o novo departamento
            if "cargos" not in data:
                data["cargos"] = {}
            data["cargos"][novo] = []
            save_all(data)
            self.departamento_input.addItem(novo)
            self.departamento_input.setCurrentText(novo)
            self.atualizar_cargos_por_departamento()
        else:
            QMessageBox.information(self, "Info", "Este departamento já existe na lista.")

    def remover_departamento(self):
        valor = self.departamento_input.currentText().strip()
        idx = self.departamento_input.currentIndex()
        if idx >= 0 and valor:
            data = load_all()
            departamentos = data.get("departamentos", [])
            if valor in departamentos:
                departamentos.remove(valor)
                data["departamentos"] = departamentos
                # Remove cargos associados
                if "cargos" in data and valor in data["cargos"]:
                    del data["cargos"][valor]
                save_all(data)
                self.departamento_input.removeItem(idx)
                self.atualizar_cargos_por_departamento()
                QMessageBox.information(self, "Removido", f"Departamento '{valor}' e seus cargos foram removidos.")
            else:
                QMessageBox.warning(self, "Atenção", "Este departamento não pode ser removido ou não existe.")
        else:
            QMessageBox.warning(self, "Atenção", "Selecione um departamento para remover.")

    def atualizar_cargos_por_departamento(self):
            departamento = self.departamento_input.currentText().strip()
            self.cargo_input.clear()
            self.cargo_input.addItems(load_cargos(departamento))

    def adicionar_cargo(self):
        departamento = self.departamento_input.currentText().strip()
        novo = self.cargo_input.currentText().strip()
        if not novo:
            QMessageBox.warning(self, "Atenção", "Digite o nome do cargo para adicionar.")
            return
        if add_cargo(departamento, novo):
            self.cargo_input.addItem(novo)
            self.cargo_input.setCurrentText(novo)
        else:
            QMessageBox.information(self, "Info", "Este cargo já existe na lista deste departamento.")

    def remover_cargo(self):
        departamento = self.departamento_input.currentText().strip()
        valor = self.cargo_input.currentText().strip()
        idx = self.cargo_input.currentIndex()
        if idx >= 0 and valor:
            if remove_cargo(departamento, valor):
                self.cargo_input.removeItem(idx)
                QMessageBox.information(self, "Removido", f"Cargo '{valor}' removido do departamento '{departamento}'.")
            else:
                QMessageBox.warning(self, "Atenção", "Este cargo não pode ser removido ou não existe neste departamento.")
        else:
            QMessageBox.warning(self, "Atenção", "Selecione um cargo para remover.")

