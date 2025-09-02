from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QGroupBox, QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDialogButtonBox, QDateEdit

class ServiceAccounting(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        layout = QVBoxLayout(self)

        # Seleção de projeto
        project_box = QGroupBox("Projeto")
        project_layout = QHBoxLayout()
        self.project_combo = QComboBox()
        project_layout.addWidget(QLabel("Selecione o projeto:"))
        project_layout.addWidget(self.project_combo)
        project_box.setLayout(project_layout)
        layout.addWidget(project_box)

        """# Tabela de receitas/despesas
        self.finance_table = QTableWidget()
        self.finance_table.setColumnCount(5)
        self.finance_table.setHorizontalHeaderLabels([
            "Tipo", "Descrição", "Valor Orçado", "Valor Realizado", "Diferença"
        ])
        self.finance_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.finance_table)"""


        # Tabela de categorias/sub-orçamentos
        category_box = QGroupBox("Categorias / Sub-Orçamentos")
        category_layout = QVBoxLayout()
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels([
            "Categoria", "Valor Orçado", "Valor Realizado", "Diferença"
        ])
        self.category_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.category_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.category_table.horizontalHeader().setStretchLastSection(True)
        self.category_table.setColumnWidth(0, 180)
        self.category_table.setColumnWidth(1, 120)
        self.category_table.setColumnWidth(2, 120)
        self.category_table.setColumnWidth(3, 120)
        category_layout.addWidget(self.category_table)
        # Botões para gerenciar categorias
        category_btn_layout = QHBoxLayout()
        self.btn_add_category = QPushButton("Adicionar Categoria")
        self.btn_edit_category = QPushButton("Editar Categoria")
        self.btn_remove_category = QPushButton("Remover Categoria")
        category_btn_layout.addWidget(self.btn_add_category)
        category_btn_layout.addWidget(self.btn_edit_category)
        category_btn_layout.addWidget(self.btn_remove_category)
        category_layout.addLayout(category_btn_layout)
        category_box.setLayout(category_layout)
        layout.addWidget(category_box)

        # Tabela de lançamentos
        self.lancamentos_table = QTableWidget()
        self.lancamentos_table.setColumnCount(6)
        self.lancamentos_table.setHorizontalHeaderLabels([
            "Tipo", "Descrição", "Valor Unitário", "Quantidade", "Valor Total", "Data"
        ])
        self.lancamentos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.lancamentos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.lancamentos_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.lancamentos_table.horizontalHeader().setStretchLastSection(True)
        self.lancamentos_table.setColumnWidth(0, 80)
        self.lancamentos_table.setColumnWidth(1, 180)
        self.lancamentos_table.setColumnWidth(2, 100)
        self.lancamentos_table.setColumnWidth(3, 80)
        self.lancamentos_table.setColumnWidth(4, 120)
        self.lancamentos_table.setColumnWidth(5, 100)
        layout.addWidget(self.lancamentos_table)
        
        # Botões para adicionar/editar receitas/despesas
        btn_layout = QHBoxLayout()
        self.btn_add_receita = QPushButton("Adicionar Receita")
        self.btn_add_despesa = QPushButton("Adicionar Despesa")
        btn_layout.addWidget(self.btn_add_receita)
        btn_layout.addWidget(self.btn_add_despesa)
        layout.addLayout(btn_layout)

        # Resumo financeiro
        summary_box = QGroupBox("Resumo da Execução Financeira")
        summary_layout = QHBoxLayout()
        self.label_total_orcado = QLabel("Total Orçado: MZN 0,00")
        self.label_total_realizado = QLabel("Total Realizado: MZN 0,00")
        self.label_total_diferenca = QLabel("Diferença: MZN 0,00")
        summary_layout.addWidget(self.label_total_orcado)
        summary_layout.addWidget(self.label_total_realizado)
        summary_layout.addWidget(self.label_total_diferenca)
        summary_box.setLayout(summary_layout)
        layout.addWidget(summary_box)

        # Carregar projetos no ComboBox
        self.load_projects()
        self.project_combo.currentIndexChanged.connect(self.on_project_selected)
        # Carregar categorias do projeto selecionado
        self.on_project_selected()

        # Conectar botões de categoria e lançamentos
        self.btn_add_category.clicked.connect(self.add_category)
        self.btn_edit_category.clicked.connect(self.edit_category)
        self.btn_remove_category.clicked.connect(self.remove_category)
        self.btn_add_receita.clicked.connect(lambda: self.add_lancamento('Receita'))
        self.btn_add_despesa.clicked.connect(lambda: self.add_lancamento('Despesa'))

    def load_projects(self):
        if not self.db:
            return
        cursor = self.db.cursor
        cursor.execute("SELECT id, nome FROM projetos ORDER BY nome")
        self.projects = cursor.fetchall()
        self.project_combo.clear()
        for proj in self.projects:
            self.project_combo.addItem(proj[1], proj[0])

    def on_project_selected(self):
        if not hasattr(self, 'projects') or not self.projects:
            return
        idx = self.project_combo.currentIndex()
        if idx < 0:
            return
        projeto_id = self.project_combo.currentData()
        self.load_categories(projeto_id)
        # Exibir lançamentos da primeira categoria, se houver
        if self.category_table.rowCount() > 0:
            cat_nome = self.category_table.item(0, 0).text()
            cat_id = self.get_category_id(projeto_id, cat_nome)
            self.load_lancamentos(projeto_id, cat_id)
        else:
            self.lancamentos_table.setRowCount(0)

    def load_categories(self, projeto_id):
        cursor = self.db.cursor
        cursor.execute("SELECT id, nome, valor_orcado FROM categorias_orcamento WHERE projeto_id = ? ORDER BY nome", (projeto_id,))
        categorias = cursor.fetchall()
        self.category_table.setRowCount(0)
        total_orcado = 0.0
        total_realizado = 0.0
        for row_idx, cat in enumerate(categorias):
            cat_id, nome, valor_orcado = cat
            self.category_table.insertRow(row_idx)
            self.category_table.setItem(row_idx, 0, QTableWidgetItem(nome))
            self.category_table.setItem(row_idx, 1, QTableWidgetItem(f"MZN {valor_orcado:,.2f}"))
            total_orcado += valor_orcado
            # Calcular valor realizado (somatório das receitas - despesas)
            cursor.execute("SELECT tipo, SUM(valor_total) FROM lancamentos WHERE categoria_id = ? GROUP BY tipo", (cat_id,))
            lancs = cursor.fetchall()
            realizado = 0.0
            for tipo, soma in lancs:
                if tipo == 'Receita':
                    realizado += soma if soma else 0.0
                elif tipo == 'Despesa':
                    realizado -= soma if soma else 0.0
            self.category_table.setItem(row_idx, 2, QTableWidgetItem(f"MZN {realizado:,.2f}"))
            diff = valor_orcado - realizado
            self.category_table.setItem(row_idx, 3, QTableWidgetItem(f"MZN {diff:,.2f}"))
            total_realizado += realizado
        # Atualizar resumo financeiro geral
        total_diferenca = total_orcado - total_realizado
        self.label_total_orcado.setText(f"Total Orçado: MZN {total_orcado:,.2f}")
        self.label_total_realizado.setText(f"Total Realizado: MZN {total_realizado:,.2f}")
        self.label_total_diferenca.setText(f"Diferença: MZN {total_diferenca:,.2f}")
        # TODO: implementar lógica de registro, edição e análise dos dados
    
    def add_category(self):
        projeto_id = self.project_combo.currentData()
        if not projeto_id:
            return
        dialog = CategoryDialog(self)
        if dialog.exec():
            nome, valor = dialog.get_data()
            if nome:
                cursor = self.db.cursor
                cursor.execute("INSERT INTO categorias_orcamento (projeto_id, nome, valor_orcado) VALUES (?, ?, ?)", (projeto_id, nome, valor))
                self.db.conn.commit()
                self.load_categories(projeto_id)

    def edit_category(self):
        projeto_id = self.project_combo.currentData()
        row = self.category_table.currentRow()
        if row < 0:
            return
        cat_nome = self.category_table.item(row, 0).text()
        cat_valor = self.category_table.item(row, 1).text().replace('MZN', '').replace(',', '').strip()
        try:
            cat_valor = float(cat_valor)
        except ValueError:
            cat_valor = 0.0
        dialog = CategoryDialog(self)
        dialog.nome_edit.setText(cat_nome)
        dialog.valor_edit.setValue(cat_valor)
        if dialog.exec():
            nome, valor = dialog.get_data()
            if nome:
                cursor = self.db.cursor
                cat_id = self.get_category_id(projeto_id, cat_nome)
                cursor.execute("UPDATE categorias_orcamento SET nome = ?, valor_orcado = ? WHERE id = ?", (nome, valor, cat_id))
                self.db.conn.commit()
                self.load_categories(projeto_id)

    def remove_category(self):
        projeto_id = self.project_combo.currentData()
        row = self.category_table.currentRow()
        if row < 0:
            return
        cat_nome = self.category_table.item(row, 0).text()
        cursor = self.db.cursor
        cat_id = self.get_category_id(projeto_id, cat_nome)
        cursor.execute("DELETE FROM categorias_orcamento WHERE id = ?", (cat_id,))
        self.db.conn.commit()
        self.load_categories(projeto_id)

    def get_category_id(self, projeto_id, cat_nome):
        cursor = self.db.cursor
        cursor.execute("SELECT id FROM categorias_orcamento WHERE projeto_id = ? AND nome = ?", (projeto_id, cat_nome))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def add_lancamento(self, tipo):
        projeto_id = self.project_combo.currentData()
        row = self.category_table.currentRow()
        if row < 0:
            return
        cat_nome = self.category_table.item(row, 0).text()
        cat_id = self.get_category_id(projeto_id, cat_nome)
        dialog = LancamentoDialog(tipo, self)
        if dialog.exec():
            valor_unitario, quantidade, valor_total, descricao, data = dialog.get_data()
            cursor = self.db.cursor
            cursor.execute("INSERT INTO lancamentos (projeto_id, categoria_id, tipo, valor_unitario, quantidade, valor_total, descricao, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (projeto_id, cat_id, tipo, valor_unitario, quantidade, valor_total, descricao, data))
            self.db.conn.commit()
            self.load_categories(projeto_id)
            self.load_lancamentos(projeto_id, cat_id)

    def load_lancamentos(self, projeto_id, categoria_id):
        cursor = self.db.cursor
        cursor.execute("SELECT tipo, descricao, valor_unitario, quantidade, valor_total, data FROM lancamentos WHERE projeto_id = ? AND categoria_id = ? ORDER BY data DESC", (projeto_id, categoria_id))
        lancs = cursor.fetchall()
        self.lancamentos_table.setRowCount(0)
        for row_idx, l in enumerate(lancs):
            self.lancamentos_table.insertRow(row_idx)
            self.lancamentos_table.setItem(row_idx, 0, QTableWidgetItem(l[0]))
            self.lancamentos_table.setItem(row_idx, 1, QTableWidgetItem(l[1]))
            self.lancamentos_table.setItem(row_idx, 2, QTableWidgetItem(f"MZN {l[2]:,.2f}"))
            self.lancamentos_table.setItem(row_idx, 3, QTableWidgetItem(f"{l[3]:,.2f}"))
            self.lancamentos_table.setItem(row_idx, 4, QTableWidgetItem(f"MZN {l[4]:,.2f}"))
            self.lancamentos_table.setItem(row_idx, 5, QTableWidgetItem(l[5]))

    def on_category_selected(self):
        projeto_id = self.project_combo.currentData()
        row = self.category_table.currentRow()
        if row < 0:
            self.lancamentos_table.setRowCount(0)
            return
        cat_nome = self.category_table.item(row, 0).text()
        cat_id = self.get_category_id(projeto_id, cat_nome)
        self.load_lancamentos(projeto_id, cat_id)

    def refresh_projects(self):
        self.load_projects()
        # Seleciona o último projeto criado, se houver
        if self.projects:
            self.project_combo.setCurrentIndex(len(self.projects) - 1)
        self.on_project_selected()

class CategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Categoria")
        layout = QFormLayout(self)
        self.nome_edit = QLineEdit()
        self.valor_edit = QDoubleSpinBox()
        self.valor_edit.setMaximum(999999999)
        self.valor_edit.setDecimals(2)
        self.valor_edit.setPrefix("MZN ")
        layout.addRow("Nome da categoria:", self.nome_edit)
        layout.addRow("Valor orçado:", self.valor_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_data(self):
        return self.nome_edit.text().strip(), self.valor_edit.value()

    
    def get_category_id(self, projeto_id, cat_nome):
        cursor = self.db.cursor
        cursor.execute("SELECT id FROM categorias_orcamento WHERE projeto_id = ? AND nome = ?", (projeto_id, cat_nome))
        result = cursor.fetchone()
        return result[0] if result else None

    

class LancamentoDialog(QDialog):
    def __init__(self, tipo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Adicionar {tipo}")
        layout = QFormLayout(self)
        self.valor_unitario_edit = QDoubleSpinBox()
        self.valor_unitario_edit.setMaximum(999999999)
        self.valor_unitario_edit.setDecimals(2)
        self.valor_unitario_edit.setPrefix("MZN ")
        self.quantidade_edit = QDoubleSpinBox()
        self.quantidade_edit.setMaximum(999999999)
        self.quantidade_edit.setDecimals(2)
        self.quantidade_edit.setValue(1)
        self.valor_total_edit = QLineEdit()
        self.valor_total_edit.setReadOnly(True)
        self.descricao_edit = QLineEdit()
        self.data_edit = QDateEdit()
        self.data_edit.setCalendarPopup(True)
        layout.addRow("Valor unitário:", self.valor_unitario_edit)
        layout.addRow("Quantidade:", self.quantidade_edit)
        layout.addRow("Valor total:", self.valor_total_edit)
        layout.addRow("Descrição:", self.descricao_edit)
        layout.addRow("Data:", self.data_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(self.button_box)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        # Atualiza valor total automaticamente
        self.valor_unitario_edit.valueChanged.connect(self.update_valor_total)
        self.quantidade_edit.valueChanged.connect(self.update_valor_total)
        self.update_valor_total()

    def update_valor_total(self):
        valor = self.valor_unitario_edit.value()
        qtd = self.quantidade_edit.value()
        total = valor * qtd
        self.valor_total_edit.setText(f"MZN {total:,.2f}")

    def get_data(self):
        valor_unitario = self.valor_unitario_edit.value()
        quantidade = self.quantidade_edit.value()
        valor_total = valor_unitario * quantidade
        descricao = self.descricao_edit.text().strip()
        data = self.data_edit.date().toString("yyyy-MM-dd")
        return valor_unitario, quantidade, valor_total, descricao, data