from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QDoubleSpinBox,QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox, QFormLayout, QTextEdit, QDateEdit, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont

class ProjectList(QWidget):
    projeto_salvo = pyqtSignal()
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.editing_project_id = None  # ID do projeto em edição
        self.setWindowTitle("Gestão de Projectos")
        self.resize(900, 700)
        self.init_ui()
        self.load_projects()
        self.connect_events()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Formulário de cadastro de projetos
        form_box = QGroupBox("Formulario de cadastro de Projectos")
        form_layout = QVBoxLayout()
        # Linha 1: Nome e Cliente
        row1 = QHBoxLayout()
        self.nome_edit = QLineEdit()
        self.nome_edit.setPlaceholderText("Nome do projeto")
        self.cliente_edit = QLineEdit()
        self.cliente_edit.setPlaceholderText("Cliente")
        row1.addWidget(QLabel("Nome:"))
        row1.addWidget(self.nome_edit)
        row1.addWidget(QLabel("Cliente:"))
        row1.addWidget(self.cliente_edit)
        form_layout.addLayout(row1)
        # Linha 2: Status, Data Início, Data Fim
        row2 = QHBoxLayout()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Em andamento", "Concluído", "Pendente"])
        self.data_inicio_edit = QDateEdit()
        self.data_inicio_edit.setCalendarPopup(True)
        self.data_inicio_edit.setDate(QDate.currentDate())
        self.data_inicio_edit.setFixedWidth(120)
        self.data_fim_edit = QDateEdit()
        self.data_fim_edit.setCalendarPopup(True)
        self.data_fim_edit.setDate(QDate.currentDate())
        self.data_fim_edit.setFixedWidth(120)
        row2.addWidget(QLabel("Status:"))
        row2.addWidget(self.status_combo)
        row2.addWidget(QLabel("Data de Início:"))
        row2.addWidget(self.data_inicio_edit)
        row2.addWidget(QLabel("Data de Fim:"))
        row2.addWidget(self.data_fim_edit)
        
        # Linha 3: Orçado em
        row2.addWidget(QLabel("Orçado em:"))
        self.orcado_em_edit = QTextEdit()
        self.orcado_em_edit.setFixedHeight(28)
        self.orcado_em_edit.setPlaceholderText("Orçado em")
        row2.addWidget(self.orcado_em_edit)
        form_layout.addLayout(row2)
        # Linha 3: Descrição
        row3 = QVBoxLayout()
        self.descricao_edit = QTextEdit()
        self.descricao_edit.setPlaceholderText("Descrição do projeto")
        self.descricao_edit.setFixedHeight(50)
        row3.addWidget(QLabel("Descrição:"))
        row3.addWidget(self.descricao_edit)
        form_layout.addLayout(row3)
        form_box.setLayout(form_layout)
        main_layout.addWidget(form_box)

        # Barra de pesquisa automática + botões
        search_hbox = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Barra de pesquisa automática")
        search_hbox.addWidget(self.search_edit)
        self.btn_salvar = QPushButton("Salvar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_novo = QPushButton("Novo")
        search_hbox.addWidget(self.btn_novo)
        search_hbox.addWidget(self.btn_salvar)
        search_hbox.addWidget(self.btn_excluir)
        main_layout.addLayout(search_hbox)

        # Lista de projetos (QTableWidget)
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(6)
        self.project_table.setHorizontalHeaderLabels(["Nome", "Cliente", "Status", "Início", "Fim", "Orçado em"])
        self.project_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.project_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.project_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.project_table.horizontalHeader().setStretchLastSection(True)
        self.project_table.setColumnWidth(0, 320)  # Nome
        self.project_table.setColumnWidth(1, 240)  # Cliente
        self.project_table.setColumnWidth(2, 100)  # Status
        self.project_table.setColumnWidth(3, 100)  # Início
        self.project_table.setColumnWidth(4, 100)  # Fim
        self.project_table.setColumnWidth(5, 120)  # Orçado em
        self.project_table.setSortingEnabled(True)
        main_layout.addWidget(self.project_table, stretch=1)

        # Barra de ordenação
        order_hbox = QHBoxLayout()
        self.order_combo = QComboBox()
        self.order_combo.addItems(["Nome", "Cliente", "Data de Início", "Status"])
        order_label = QLabel("Ordenar por:")
        order_hbox.addWidget(order_label)
        order_hbox.addWidget(self.order_combo)
        main_layout.addLayout(order_hbox)

        self.setLayout(main_layout)


    def connect_events(self):
        self.btn_salvar.clicked.connect(self.save_project)
        self.btn_excluir.clicked.connect(self.delete_project)
        self.btn_novo.clicked.connect(self.clear_form)
        self.search_edit.textChanged.connect(self.filter_projects)
        self.order_combo.currentIndexChanged.connect(self.load_projects)
        self.project_table.cellClicked.connect(self.edit_project)
        self.orcado_em_edit.textChanged.connect(self.on_orcado_changed)
        self.orcado_em_edit.focusInEvent = self.orcado_focus_in
        self.orcado_em_edit.focusOutEvent = self.orcado_focus_out

    def load_projects(self):
        self.project_table.setRowCount(0)
        if not self.db:
            return
        cursor = self.db.cursor
        order_field = {
            0: "nome",
            1: "cliente",
            2: "inicio",
            3: "status"
        }.get(self.order_combo.currentIndex(), "nome")
        cursor.execute(f"SELECT id, nome, cliente, inicio, fim, status, descricao, orcado_em FROM projetos ORDER BY {order_field}")
        self.projects = cursor.fetchall()
        for row_idx, proj in enumerate(self.projects):
            self.project_table.insertRow(row_idx)
            self.project_table.setItem(row_idx, 0, QTableWidgetItem(proj[1]))
            self.project_table.setItem(row_idx, 1, QTableWidgetItem(proj[2]))
            status_item = QTableWidgetItem(proj[5])
            if proj[5] == "Concluído":
                status_item.setForeground(Qt.GlobalColor.green)
            elif proj[5] == "Em andamento":
                status_item.setForeground(Qt.GlobalColor.yellow)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.project_table.setItem(row_idx, 2, status_item)
            self.project_table.setItem(row_idx, 3, QTableWidgetItem(proj[3]))
            self.project_table.setItem(row_idx, 4, QTableWidgetItem(proj[4]))
            # Exibir valor orçado em formato monetário
            orcado_str = f"MZN {proj[7]:,.2f}" if proj[7] is not None else "MZN 0,00"
            self.project_table.setItem(row_idx, 5, QTableWidgetItem(orcado_str))

    def filter_projects(self):
        filtro = self.search_edit.text().lower()
        self.project_table.setRowCount(0)
        for row_idx, proj in enumerate(getattr(self, 'projects', [])):
            orcado_str = f"MZN {proj[7]:,.2f}" if proj[7] is not None else "MZN 0,00"
            if (filtro in proj[1].lower() or filtro in proj[2].lower() or filtro in proj[5].lower() or filtro in orcado_str.lower()):
                self.project_table.insertRow(self.project_table.rowCount())
                self.project_table.setItem(self.project_table.rowCount()-1, 0, QTableWidgetItem(proj[1]))
                self.project_table.setItem(self.project_table.rowCount()-1, 1, QTableWidgetItem(proj[2]))
                status_item = QTableWidgetItem(proj[5])
                if proj[5] == "Concluído":
                    status_item.setForeground(Qt.GlobalColor.green)
                elif proj[5] == "Em andamento":
                    status_item.setForeground(Qt.GlobalColor.yellow)
                else:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.project_table.setItem(self.project_table.rowCount()-1, 2, status_item)
                self.project_table.setItem(self.project_table.rowCount()-1, 3, QTableWidgetItem(proj[3]))
                self.project_table.setItem(self.project_table.rowCount()-1, 4, QTableWidgetItem(proj[4]))
                self.project_table.setItem(self.project_table.rowCount()-1, 5, QTableWidgetItem(orcado_str))

    def save_project(self):
        if not self.db:
            return
        nome = self.nome_edit.text().strip()
        cliente = self.cliente_edit.text().strip()
        status = self.status_combo.currentText()
        inicio = self.data_inicio_edit.date().toString("yyyy-MM-dd")
        fim = self.data_fim_edit.date().toString("yyyy-MM-dd")
        descricao = self.descricao_edit.toPlainText().strip()
        orcado_em = self.get_orcado_value()
        if not self.db:
            return
        nome = self.nome_edit.text().strip()
        cliente = self.cliente_edit.text().strip()
        status = self.status_combo.currentText()
        inicio = self.data_inicio_edit.date().toString("yyyy-MM-dd")
        if not nome:
            return  # Pode adicionar mensagem de erro
        cursor = self.db.cursor
        if self.editing_project_id:
            cursor.execute("SELECT COUNT(*) FROM projetos WHERE nome = ? AND cliente = ? AND id != ?", (nome, cliente, self.editing_project_id))
            if cursor.fetchone()[0] > 0:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Projeto duplicado", "Já existe um projeto com esse nome e cliente.")
                return
            cursor.execute("UPDATE projetos SET nome = ?, cliente = ?, inicio = ?, fim = ?, status = ?, descricao = ?, orcado_em = ? WHERE id = ?",
                           (nome, cliente, inicio, fim, status, descricao, orcado_em, self.editing_project_id))
        else:
            cursor.execute("SELECT COUNT(*) FROM projetos WHERE nome = ? AND cliente = ?", (nome, cliente))
            if cursor.fetchone()[0] > 0:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Projeto duplicado", "Já existe um projeto com esse nome e cliente.")
                return
            cursor.execute("INSERT INTO projetos (nome, cliente, inicio, fim, status, descricao, orcado_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (nome, cliente, inicio, fim, status, descricao, orcado_em))
            self.db.conn.commit()
            self.load_projects()
            self.clear_form()
            self.projeto_salvo.emit()
            # Atualiza ComboBox de projetos na aba contabilidade
            try:
                from ..services.service_accounting import ServiceAccounting
                for widget in self.parent().findChildren(ServiceAccounting):
                    widget.refresh_projects()
            except Exception:
                pass

    def delete_project(self):
        if not self.db:
            return
        selected = self.project_table.currentRow()
        if selected < 0:
            return
        proj_id = self.projects[selected][0]
        cursor = self.db.cursor
        cursor.execute("DELETE FROM projetos WHERE id = ?", (proj_id,))
        self.db.conn.commit()
        self.load_projects()

    def edit_project(self, row, col):
        proj = self.projects[row]
        self.editing_project_id = proj[0]
        self.nome_edit.setText(proj[1])
        self.cliente_edit.setText(proj[2])
        self.status_combo.setCurrentText(proj[5])
        self.data_inicio_edit.setDate(QDate.fromString(proj[3], "yyyy-MM-dd"))
        self.data_fim_edit.setDate(QDate.fromString(proj[4], "yyyy-MM-dd"))
        self.descricao_edit.setPlainText(proj[6])
        # Carregar valor orçado em (sempre formatado)
        try:
            valor = float(proj[7]) if proj[7] is not None else 0.0
            inteiro = str(int(valor)).replace(',', '')
            decimal = f"{valor:.2f}".split('.')[-1]
            inteiro_formatado = f"{int(inteiro):,}".replace(',', '.') if inteiro else '0'
            formatted = f"MZN {inteiro_formatado},{decimal}"
        except (IndexError, ValueError):
            formatted = "MZN 0,00"
        self.orcado_em_edit.setText(formatted)

    def clear_form(self):
        self.editing_project_id = None
        self.nome_edit.clear()
        self.cliente_edit.clear()
        self.status_combo.setCurrentIndex(0)
        self.data_inicio_edit.setDate(QDate.currentDate())
        self.data_fim_edit.setDate(QDate.currentDate())
        self.descricao_edit.clear()
        self.orcado_em_edit.setText("MZN 0,00")

    
    def on_orcado_changed(self):
        # Captura apenas os dígitos inseridos
        text = self.orcado_em_edit.toPlainText()
        digits = ''.join(c for c in text if c.isdigit())
        # Se o usuário apagou tudo, zera
        if not digits:
            formatted = "MZN 0,00"
        else:
            # Limita tamanho máximo (ex: 12 dígitos)
            digits = digits[:12]
            # Formata da direita para esquerda (caixa bancário)
            inteiro = digits[:-2] if len(digits) > 2 else ''
            decimal = digits[-2:] if len(digits) >= 2 else digits.zfill(2)
            inteiro_formatado = f"{int(inteiro):,}".replace(',', '.') if inteiro else '0'
            formatted = f"MZN {inteiro_formatado},{decimal}"
        # Atualiza o campo apenas se necessário
        if text != formatted:
            self.orcado_em_edit.blockSignals(True)
            self.orcado_em_edit.setText(formatted)
            # Reposiciona o cursor para o final do texto
            from PyQt6.QtGui import QTextCursor
            cursor = self.orcado_em_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.orcado_em_edit.setTextCursor(cursor)
            self.orcado_em_edit.blockSignals(False)

    def orcado_focus_in(self, event):
        text = self.orcado_em_edit.toPlainText().replace(' MZN', '').replace(',', '').strip()
        self.orcado_em_edit.setText(text)
        QTextEdit.focusInEvent(self.orcado_em_edit, event)

    def orcado_focus_out(self, event):
        text = self.orcado_em_edit.toPlainText().replace('MZN', '').replace(' ', '').replace('.', '').replace(',', '').strip()
        if not text.isdigit():
            formatted = "MZN 0,00"
        else:
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
        self.orcado_em_edit.setText(formatted)
        QTextEdit.focusOutEvent(self.orcado_em_edit, event)

    def get_orcado_value(self):
        text = self.orcado_em_edit.toPlainText()
        # Remove máscara e espaços
        text = text.replace('MZN', '').replace(' ', '').replace('.', '')
        # Troca vírgula por ponto para float
        text = text.replace(',', '.')
        try:
            value = float(text)
        except ValueError:
            value = 0.0
        return value
