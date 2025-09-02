from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox, QFormLayout, QTextEdit, QDateEdit, QTableWidget, QTableWidgetItem, QCheckBox, QDialog, QListWidget, QInputDialog, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QTextCursor
import json
from modules.services.service_repository import ServiceRepository
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QKeyEvent

class DescricaoTextEdit(QTextEdit):
    def keyPressEvent(self, event: QKeyEvent):
        if event.text() == ';':
            self.insertPlainText(';\n')
            # Opcional: impedir o caractere padrão
            return
        super().keyPressEvent(event)

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, event):
        if event.button() == 1:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

class ServiceList(QWidget):
    
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.repo = ServiceRepository(db)
        self.editing_service_id = None
        self.setWindowTitle("Gestão de Serviços")
        self.resize(900, 700)
        self.init_ui()
        self.load_services()
        self.connect_events()
        self.load_config_lists()  # Garante que as listas sejam carregadas ao iniciar

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        # Formulário de cadastro de serviços
        form_box = QGroupBox("Cadastro de Serviço")
        form_layout = QVBoxLayout()
        # Linha 1: Membro e Projeto
        row1 = QHBoxLayout()
        self.membro_combo = QComboBox()
        self.projeto_combo = QComboBox()
        row1.addWidget(QLabel("Membro:"))
        row1.addWidget(self.membro_combo)
        row1.addWidget(QLabel("Projeto:"))
        row1.addWidget(self.projeto_combo)
        form_layout.addLayout(row1)
        # Linha 2: Papel e Local (apenas ComboBox, sem botões)
        self.papel_combo = QComboBox()
        self.local_combo = QComboBox()
        papel_label = ClickableLabel("Papel:")
        papel_label.setToolTip("Clique para gerenciar lista de papéis")
        papel_label.clicked.connect(self.open_papel_manager)
        local_label = ClickableLabel("Local:")
        local_label.setToolTip("Clique para gerenciar lista de locais")
        local_label.clicked.connect(self.open_local_manager)
        row2 = QHBoxLayout()
        row2.addWidget(papel_label)
        row2.addWidget(self.papel_combo)
        row2.addWidget(local_label)
        row2.addWidget(self.local_combo)
        form_layout.addLayout(row2)
        # Linha 3: Descrição
        row3 = QVBoxLayout()
        self.descricao_edit = DescricaoTextEdit()
        self.descricao_edit.setFixedHeight(50)
        self.descricao_edit.setPlaceholderText("Descrição do serviço")
        row3.addWidget(QLabel("Descrição:"))
        row3.addWidget(self.descricao_edit)
        form_layout.addLayout(row3)
        form_box.setLayout(form_layout)
        main_layout.addWidget(form_box)
        # Formulário de contratos
        contrato_box = QGroupBox("Cadastro de Contrato")
        contrato_layout = QVBoxLayout()
        rowc1 = QHBoxLayout()
        self.contrato_tipo_combo = QComboBox()
        self.contrato_tipo_combo.addItems(["Termo certo", "Sem Termo", "Termo Incerto"])
        self.contrato_salario_edit = QLineEdit()
        self.contrato_salario_edit.setPlaceholderText("Salário")
        rowc1.addWidget(QLabel("Tipo:"))
        rowc1.addWidget(self.contrato_tipo_combo)
        rowc1.addWidget(QLabel("Salário:"))
        rowc1.addWidget(self.contrato_salario_edit)
        contrato_layout.addLayout(rowc1)
        rowc2 = QHBoxLayout()
        self.contrato_inicio_edit = QDateEdit()
        self.contrato_inicio_edit.setCalendarPopup(True)
        self.contrato_inicio_edit.setDate(QDate.currentDate())
        self.contrato_fim_edit = QDateEdit()
        self.contrato_fim_edit.setCalendarPopup(True)
        self.contrato_fim_edit.setDate(QDate.currentDate())
        rowc2.addWidget(QLabel("Início:"))
        rowc2.addWidget(self.contrato_inicio_edit)
        rowc2.addWidget(QLabel("Fim:"))
        rowc2.addWidget(self.contrato_fim_edit)
        contrato_layout.addLayout(rowc2)
        rowc3 = QVBoxLayout()
        self.contrato_obs_edit = QTextEdit()
        self.contrato_obs_edit.setFixedHeight(40)
        self.contrato_obs_edit.setPlaceholderText("Observações")
        rowc3.addWidget(QLabel("Observações:"))
        rowc3.addWidget(self.contrato_obs_edit)
        contrato_layout.addLayout(rowc3)
        contrato_box.setLayout(contrato_layout)
        main_layout.addWidget(contrato_box)
        # Barra de pesquisa + botões
        search_hbox = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Pesquisar serviço")
        self.btn_salvar = QPushButton("Salvar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_novo = QPushButton("Novo")
        search_hbox.addWidget(self.search_edit)
        search_hbox.addWidget(self.btn_salvar)
        search_hbox.addWidget(self.btn_excluir)
        search_hbox.addWidget(self.btn_novo)
        main_layout.addLayout(search_hbox)
        # Tabela de serviços
        self.service_table = QTableWidget()
        self.service_table.setColumnCount(7)
        self.service_table.setHorizontalHeaderLabels([
            "Membro", "Projeto", "Papel", "Tipo contrato", "Fim", "Salário", "Descrição"
        ])
        self.service_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.service_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.service_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.service_table.horizontalHeader().setStretchLastSection(True)
        self.service_table.setColumnWidth(0, 150)
        self.service_table.setColumnWidth(1, 150)
        self.service_table.setColumnWidth(2, 120)
        self.service_table.setColumnWidth(3, 120)
        self.service_table.setColumnWidth(4, 100)
        self.service_table.setColumnWidth(5, 120)
        self.service_table.setColumnWidth(6, 200)
        self.service_table.setSortingEnabled(True)
        main_layout.addWidget(self.service_table, stretch=1)
        self.setLayout(main_layout)
        self.load_config_lists()
        self.papel_combo.installEventFilter(self)
        self.local_combo.installEventFilter(self)
        self.papel_combo.setToolTip("Clique com o botão direito para gerenciar lista de papéis")
        self.local_combo.setToolTip("Clique com o botão direito para gerenciar lista de locais")
    
    def connect_events(self):
        self.btn_salvar.clicked.connect(self.save_service)
        self.btn_excluir.clicked.connect(self.delete_service)
        self.btn_novo.clicked.connect(self.clear_form)
        self.search_edit.textChanged.connect(self.filter_services)
        self.service_table.cellClicked.connect(self.edit_service)
        self.contrato_tipo_combo.currentTextChanged.connect(self.on_tipo_contrato_changed)
        self.projeto_combo.currentTextChanged.connect(self.on_projeto_changed)
        self.contrato_salario_edit.textChanged.connect(self.on_salario_changed)
        self.contrato_salario_edit.focusInEvent = self.salario_focus_in
        self.contrato_salario_edit.focusOutEvent = self.salario_focus_out
        self.descricao_edit.textChanged.connect(self.on_descricao_changed)


    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.RightButton:
                if obj == self.papel_combo:
                    self.open_papel_manager()
                    return True
                if obj == self.local_combo:
                    self.open_local_manager()
                    return True
        return super().eventFilter(obj, event)

    def load_config_lists(self):
        papel_list = sorted(self.repo.get_config_list('papel_list'), key=lambda x: x.lower())
        self.papel_combo.clear()
        self.papel_combo.addItems(papel_list)
        local_list = sorted(self.repo.get_config_list('local_list'), key=lambda x: x.lower())
        self.local_combo.clear()
        self.local_combo.addItems(local_list)

    def save_config_list(self, key, items):
        cursor = self.db.cursor
        value = json.dumps(items)
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        self.db.conn.commit()

    def add_papel(self):
        item = self.papel_combo.currentText().strip()
        if item:
            items = [self.papel_combo.itemText(i) for i in range(self.papel_combo.count())]
            if item not in items:
                items.append(item)
                self.save_config_list('papel_list', items)
                self.papel_combo.addItem(item)

    def remove_papel(self):
        item = self.papel_combo.currentText().strip()
        idx = self.papel_combo.findText(item)
        if idx >= 0:
            self.papel_combo.removeItem(idx)
            items = [self.papel_combo.itemText(i) for i in range(self.papel_combo.count())]
            self.save_config_list('papel_list', items)

    def add_local(self):
        item = self.local_combo.currentText().strip()
        if item:
            items = [self.local_combo.itemText(i) for i in range(self.local_combo.count())]
            if item not in items:
                items.append(item)
                self.save_config_list('local_list', items)
                self.local_combo.addItem(item)

    def remove_local(self):
        item = self.local_combo.currentText().strip()
        idx = self.local_combo.findText(item)
        if idx >= 0:
            self.local_combo.removeItem(idx)
            items = [self.local_combo.itemText(i) for i in range(self.local_combo.count())]
            self.save_config_list('local_list', items)

    
    def on_salario_changed(self, text):
        # Formata em tempo real: dois últimos dígitos como centavos
        clean = ''.join(c for c in text if c.isdigit())
        if not clean:
            formatted = "MZN 0,00"
        elif len(clean) == 1:
            formatted = f"MZN 0,0{clean}"
        elif len(clean) == 2:
            formatted = f"MZN 0,{clean}"
        else:
            inteiro = clean[:-2]
            decimal = clean[-2:]
            inteiro_formatado = f"{int(inteiro):,}".replace(',', '.')
            formatted = f"MZN {inteiro_formatado},{decimal}"
        if text != formatted:
            self.contrato_salario_edit.blockSignals(True)
            self.contrato_salario_edit.setText(formatted)
            self.contrato_salario_edit.blockSignals(False)

    def salario_focus_in(self, event):
        # Remove a máscara MZN ao entrar no campo
        text = self.contrato_salario_edit.text().replace(' MZN', '').replace(',', '').strip()
        self.contrato_salario_edit.setText(text)
        QLineEdit.focusInEvent(self.contrato_salario_edit, event)

    def salario_focus_out(self, event):
        # Aplica a máscara MZN ao sair do campo, tratando os dois últimos dígitos como centavos
        text = self.contrato_salario_edit.text().replace('MZN', '').replace(' ', '').replace('.', '').replace(',', '').strip()
        if not text.isdigit():
            formatted = "MZN 0,00"
        else:
            # Se o usuário digitou menos de 3 dígitos, trata como centavos
            if len(text) == 0:
                formatted = "MZN 0,00"
            elif len(text) == 1:
                formatted = f"MZN 0,0{text}"
            elif len(text) == 2:
                formatted = f"MZN 0,{text}"
            else:
                inteiro = text[:-2]
                decimal = text[-2:]
                inteiro_formatado = f"{int(inteiro):,}".replace(',', '.')
                formatted = f"MZN {inteiro_formatado},{decimal}"
        self.contrato_salario_edit.setText(formatted)
        QLineEdit.focusOutEvent(self.contrato_salario_edit, event)

    def get_salario_value(self):
        # Extrai valor numérico do campo formatado
        text = self.contrato_salario_edit.text().replace('MZN', '').replace(',', '').strip()
        try:
            value = float(text)
        except ValueError:
            value = 0.0
        return value
    
    def on_tipo_contrato_changed(self, tipo):
        if tipo in ["Sem Termo", "Termo Incerto"]:
            self.contrato_fim_edit.setEnabled(False)
            self.contrato_fim_edit.setDate(QDate.currentDate())
            self.contrato_fim_edit.clear()
        else:
            self.contrato_fim_edit.setEnabled(True)

    def on_projeto_changed(self, nome):
        # Permitir datas futuras para data fim do contrato
        self.contrato_fim_edit.setMinimumDate(QDate.currentDate())
        # Buscar data fim do projeto para limitar data início do contrato
        cursor = self.db.cursor
        cursor.execute("SELECT fim FROM projetos WHERE nome = ?", (nome,))
        row = cursor.fetchone()
        if row and row[0]:
            fim_proj = QDate.fromString(row[0], "yyyy-MM-dd")
            self.contrato_inicio_edit.setMaximumDate(fim_proj)
        else:
            self.contrato_inicio_edit.setMaximumDate(QDate(2999, 12, 31))

    def save_service(self):
        if not self.db:
            return
        membro_nome = self.membro_combo.currentText()
        projeto_nome = self.projeto_combo.currentText()
        local_servico = self.local_combo.currentText().strip()
        papel = self.papel_combo.currentText().strip()
        descricao = self.descricao_edit.toPlainText().strip()
        contrato_tipo = self.contrato_tipo_combo.currentText().strip()
        contrato_salario = str(self.get_salario_value())
        contrato_inicio = self.contrato_inicio_edit.date().toString("yyyy-MM-dd")
        contrato_fim = self.contrato_fim_edit.date().toString("yyyy-MM-dd")
        contrato_obs = self.contrato_obs_edit.toPlainText().strip()
        if not membro_nome or not projeto_nome or not papel or not contrato_tipo:
            return
        membro_id = self.repo.get_membro_id(membro_nome)
        projeto_id = self.repo.get_projeto_id(projeto_nome)
        if self.editing_service_id:
            self.repo.update_servico(self.editing_service_id, membro_id, projeto_id, local_servico, papel, descricao)
            self.repo.update_contrato(self.editing_service_id, membro_id, contrato_tipo, contrato_inicio, contrato_fim, contrato_salario, contrato_obs)
        else:
            servico_id = self.repo.insert_servico(membro_id, projeto_id, local_servico, papel, descricao)
            self.repo.insert_contrato(membro_id, servico_id, contrato_tipo, contrato_inicio, contrato_fim, contrato_salario, contrato_obs)
        self.load_services()
        self.clear_form()
        self.load_services()

    def delete_service(self):
        if not self.db or not self.editing_service_id:
            return
        self.repo.delete_servico(self.editing_service_id)
        self.load_services()
        self.clear_form()
        self.load_services()

    def clear_form(self):
        self.editing_service_id = None
        self.membro_combo.setCurrentIndex(0)
        self.projeto_combo.setCurrentIndex(0)
        self.papel_combo.setCurrentIndex(0)
        self.local_combo.setCurrentIndex(0)
        self.contrato_tipo_combo.setCurrentIndex(0)
        self.contrato_salario_edit.clear()
        self.contrato_inicio_edit.setDate(QDate.currentDate())
        self.contrato_fim_edit.setDate(QDate.currentDate())
        self.contrato_obs_edit.clear()
        self.descricao_edit.clear()
        self.load_config_lists()  # Recarrega listas papel/local
        self.load_services()

    def edit_service(self, row, col):
        svc = self.get_service_by_row(row)
        if not svc:
            return
        self.editing_service_id = svc[0]
        # Buscar nomes
        cursor = self.db.cursor
        cursor.execute("SELECT nome FROM membros WHERE id = ?", (svc[1],))
        row = cursor.fetchone()
        membro_nome = row[0] if row else ""
        cursor.execute("SELECT nome FROM projetos WHERE id = ?", (svc[2],))
        row = cursor.fetchone()
        projeto_nome = row[0] if row else ""
        self.membro_combo.setCurrentText(membro_nome)
        self.projeto_combo.setCurrentText(projeto_nome)
        self.load_config_lists()  # Garante que as listas estejam atualizadas
        self.papel_combo.setCurrentText(svc[4])
        self.local_combo.setCurrentText(svc[3])
        self.descricao_edit.setPlainText(svc[5])
        # Buscar contrato vinculado ao serviço
        cursor.execute("SELECT tipo, salario, inicio, fim, observacoes FROM contratos WHERE servico_id = ?", (svc[0],))
        contrato = cursor.fetchone()
        if contrato:
            idx_tipo = self.contrato_tipo_combo.findText(contrato[0])
            if idx_tipo >= 0:
                self.contrato_tipo_combo.setCurrentIndex(idx_tipo)
            else:
                self.contrato_tipo_combo.setCurrentIndex(0)
            self.contrato_salario_edit.setText(str(contrato[1]))
            self.contrato_inicio_edit.setDate(QDate.fromString(contrato[2], "yyyy-MM-dd"))
            self.contrato_fim_edit.setDate(QDate.fromString(contrato[3], "yyyy-MM-dd"))
            self.contrato_obs_edit.setPlainText(contrato[4])
        else:
            self.contrato_tipo_combo.setCurrentIndex(0)
            self.contrato_salario_edit.clear()
            self.contrato_inicio_edit.setDate(QDate.currentDate())
            self.contrato_fim_edit.setDate(QDate.currentDate())
            self.contrato_obs_edit.clear()

    def get_service_by_row(self, row):
        if not hasattr(self, 'services'):
            return None
        if row < 0 or row >= len(self.services):
            return None
        return self.services[row]

    def filter_services(self):
        filtro = self.search_edit.text().lower()
        self.service_table.setRowCount(0)
        for svc in getattr(self, 'services', []):
            cursor = self.db.cursor
            cursor.execute("SELECT nome FROM membros WHERE id = ?", (svc[1],))
            row = cursor.fetchone()
            membro_nome = row[0] if row else ""
            cursor.execute("SELECT nome FROM projetos WHERE id = ?", (svc[2],))
            row = cursor.fetchone()
            projeto_nome = row[0] if row else ""
            cursor.execute("SELECT tipo, fim, salario FROM contratos WHERE servico_id = ?", (svc[0],))
            contrato = cursor.fetchone()
            tipo_contrato = contrato[0] if contrato else ""
            fim_contrato = contrato[1] if contrato else ""
            salario = contrato[2] if contrato else ""
            # Formatar salário
            if salario:
                salario_str = str(salario)
                salario_clean = ''.join(c for c in salario_str if c.isdigit())
                if salario_clean:
                    if len(salario_clean) == 1:
                        salario_fmt = f"MZN 0,0{salario_clean}"
                    elif len(salario_clean) == 2:
                        salario_fmt = f"MZN 0,{salario_clean}"
                    else:
                        inteiro = salario_clean[:-2]
                        decimal = salario_clean[-2:]
                        inteiro_formatado = f"{int(inteiro):,}".replace(',', '.')
                        salario_fmt = f"MZN {inteiro_formatado},{decimal}"
                else:
                    salario_fmt = "MZN 0,00"
            else:
                salario_fmt = "MZN 0,00"
            # Verifica filtro em todos os campos relevantes
            campos = [
                membro_nome.lower(),
                projeto_nome.lower(),
                svc[4].lower(), # papel
                tipo_contrato.lower(),
                fim_contrato.lower(),
                salario_fmt.lower(),
                svc[5].lower() # descricao
            ]
            if any(filtro in campo for campo in campos):
                row_idx = self.service_table.rowCount()
                self.service_table.insertRow(row_idx)
                self.service_table.setItem(row_idx, 0, QTableWidgetItem(membro_nome))
                self.service_table.setItem(row_idx, 1, QTableWidgetItem(projeto_nome))
                self.service_table.setItem(row_idx, 2, QTableWidgetItem(svc[4]))
                self.service_table.setItem(row_idx, 3, QTableWidgetItem(tipo_contrato))
                self.service_table.setItem(row_idx, 4, QTableWidgetItem(fim_contrato))
                self.service_table.setItem(row_idx, 5, QTableWidgetItem(salario_fmt))
                self.service_table.setItem(row_idx, 6, QTableWidgetItem(svc[5]))

    def load_services(self):
        self.service_table.setSortingEnabled(False)
        self.service_table.setRowCount(0)
        self.services = self.repo.get_services()
        membros = self.repo.get_membros_dict()
        projetos = self.repo.get_projetos_dict()
        # Preencher combos em ordem alfabética
        membros_list = sorted(membros.values(), key=lambda x: x.lower())
        projetos_list = sorted(projetos.values(), key=lambda x: x.lower())
        self.membro_combo.clear()
        self.projeto_combo.clear()
        self.membro_combo.addItems(membros_list)
        self.projeto_combo.addItems(projetos_list)
        # Preencher tabela com todos os serviços
        for row_idx, svc in enumerate(self.services):
            membro_nome = membros.get(svc[1], "")
            projeto_nome = projetos.get(svc[2], "")
            contrato = self.repo.get_contrato_by_servico(svc[0])
            tipo_contrato = contrato[0] if contrato else ""
            fim_contrato = contrato[1] if contrato else ""
            salario = contrato[2] if contrato else ""
            # Formatar salário
            if salario:
                salario_str = str(salario)
                salario_clean = ''.join(c for c in salario_str if c.isdigit())
                if salario_clean:
                    if len(salario_clean) == 1:
                        salario_fmt = f"MZN 0,0{salario_clean}"
                    elif len(salario_clean) == 2:
                        salario_fmt = f"MZN 0,{salario_clean}"
                    else:
                        inteiro = salario_clean[:-2]
                        decimal = salario_clean[-2:]
                        inteiro_formatado = f"{int(inteiro):,}".replace(',', '.')
                        salario_fmt = f"MZN {inteiro_formatado},{decimal}"
                else:
                    salario_fmt = "MZN 0,00"
            else:
                salario_fmt = "MZN 0,00"
            self.service_table.insertRow(row_idx)
            self.service_table.setItem(row_idx, 0, QTableWidgetItem(membro_nome))
            self.service_table.setItem(row_idx, 1, QTableWidgetItem(projeto_nome))
            self.service_table.setItem(row_idx, 2, QTableWidgetItem(svc[4]))
            self.service_table.setItem(row_idx, 3, QTableWidgetItem(tipo_contrato))
            self.service_table.setItem(row_idx, 4, QTableWidgetItem(fim_contrato))
            self.service_table.setItem(row_idx, 5, QTableWidgetItem(salario_fmt))
            self.service_table.setItem(row_idx, 6, QTableWidgetItem(svc[5]))
        self.service_table.setSortingEnabled(True)

    def set_signals(self, member_form=None, project_list=None):
        if member_form:
            member_form.membro_salvo.connect(self.load_services)
        if project_list:
            project_list.projeto_salvo.connect(self.load_services)

    def open_papel_manager(self, event=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Gerenciar lista de Papéis")
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        items = [self.papel_combo.itemText(i) for i in range(self.papel_combo.count())]
        list_widget.addItems(items)
        layout.addWidget(list_widget)
        btn_add = QPushButton("Adicionar")
        btn_remove = QPushButton("Remover")
        btn_close = QPushButton("Fechar")
        hbox = QHBoxLayout()
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_remove)
        hbox.addWidget(btn_close)
        layout.addLayout(hbox)
        def add_item():
            text, ok = QInputDialog.getText(dialog, "Adicionar Papel", "Novo papel:")
            if ok and text.strip():
                # Validação para não permitir duplicados
                for i in range(list_widget.count()):
                    if list_widget.item(i).text().lower() == text.strip().lower():
                        QMessageBox.warning(dialog, "Duplicado", "Já existe esse papel na lista.")
                        return
                list_widget.addItem(text.strip())
        def remove_item():
            row = list_widget.currentRow()
            if row >= 0:
                list_widget.takeItem(row)
        def save_and_close():
            items = [list_widget.item(i).text() for i in range(list_widget.count())]
            self.save_config_list('papel_list', items)
            self.load_config_lists()  # Sincroniza combo após salvar
            dialog.accept()
        btn_add.clicked.connect(add_item)
        btn_remove.clicked.connect(remove_item)
        btn_close.clicked.connect(save_and_close)
        dialog.exec()

    def open_local_manager(self, event=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Gerenciar lista de Locais")
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        items = [self.local_combo.itemText(i) for i in range(self.local_combo.count())]
        list_widget.addItems(items)
        layout.addWidget(list_widget)
        btn_add = QPushButton("Adicionar")
        btn_remove = QPushButton("Remover")
        btn_close = QPushButton("Fechar")
        hbox = QHBoxLayout()
        hbox.addWidget(btn_add)
        hbox.addWidget(btn_remove)
        hbox.addWidget(btn_close)
        layout.addLayout(hbox)
        def add_item():
            text, ok = QInputDialog.getText(dialog, "Adicionar Local", "Novo local:")
            if ok and text.strip():
                # Validação para não permitir duplicados
                for i in range(list_widget.count()):
                    if list_widget.item(i).text().lower() == text.strip().lower():
                        QMessageBox.warning(dialog, "Duplicado", "Já existe esse local na lista.")
                        return
                list_widget.addItem(text.strip())
        def remove_item():
            row = list_widget.currentRow()
            if row >= 0:
                list_widget.takeItem(row)
        def save_and_close():
            items = [list_widget.item(i).text() for i in range(list_widget.count())]
            self.save_config_list('local_list', items)
            self.load_config_lists()  # Sincroniza combo após salvar
            dialog.accept()
        btn_add.clicked.connect(add_item)
        btn_remove.clicked.connect(remove_item)
        btn_close.clicked.connect(save_and_close)
        dialog.exec()

    def on_descricao_changed(self):
        text = self.descricao_edit.toPlainText()
        if text.endswith(';'):
            # Divide por ponto e vírgula, remove espaços e linhas vazias
            items = [item.strip() for item in text.split(';') if item.strip()]
            # Reescreve o campo como lista (um item por linha)
            self.descricao_edit.blockSignals(True)
            self.descricao_edit.setPlainText('\n'.join(items))
            self.descricao_edit.blockSignals(False)
            # Opcional: move o cursor para o final
            cursor = self.descricao_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.descricao_edit.setTextCursor(cursor)


