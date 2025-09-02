from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QFormLayout, QComboBox, QDateEdit, QTextEdit, QListWidget, QAbstractItemView, QInputDialog
from PyQt6.QtWidgets import QListWidgetItem
import json
import os
from PyQt6.QtCore import Qt

class MemberProfileForm(QWidget):
    def __init__(self, membro_id, db, parent_profile=None):
        super().__init__()
        self.membro_id = membro_id
        self.db = db
        self.parent_profile = parent_profile
        self.setWindowTitle("➕ Adicionar Dados ao Perfil")
        self.setMinimumWidth(350)
        self.init_ui()
        self.carregar_dados()

    def init_ui(self):
        layout = QFormLayout()

        # Pessoais
        self.genero = QComboBox()
        self.genero.addItems(["Masculino", "Feminino", "Outro"])
        self.estado_civil = QComboBox()
        self.estado_civil.addItems(["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"])
        self.nacionalidade = QComboBox()
        self.nacionalidade.addItems(["Angolana", "Brasileira", "Portuguesa", "Moçambicana", "Outra"])
        self.data_nascimento = QDateEdit()
        self.data_nascimento.setCalendarPopup(True)
        self.endereco = QLineEdit()
        self.idiomas = QListWidget()
        self.carregar_idiomas()
        
        
        self.habilidades = QTextEdit()
        layout.addRow("Gênero:", self.genero)
        layout.addRow("Estado Civil:", self.estado_civil)
        layout.addRow("Nacionalidade:", self.nacionalidade)
        layout.addRow("Data de Nascimento:", self.data_nascimento)
        layout.addRow("Endereço:", self.endereco)
        layout.addRow("Idiomas (Seleção múltipla):", self.idiomas)
        layout.addRow("Habilidades:", self.habilidades)

        salvar_btn = QPushButton("💾 Salvar")
    
        # Adiciona opção "Outro"
        outro_item = QListWidgetItem("Outro")
        outro_item.setFlags(outro_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        outro_item.setCheckState(Qt.CheckState.Unchecked)
        self.idiomas.addItem(outro_item)
        salvar_btn.clicked.connect(self.salvar_dados)
        layout.addRow(salvar_btn)

        self.setLayout(layout)


    def carregar_idiomas(self):
            self.idiomas.clear()
            idiomas_path = os.path.join(os.path.dirname(__file__), '../../config/idiomas.json')
            try:
                with open(idiomas_path, 'r', encoding='utf-8') as f:
                    idiomas = json.load(f)
            except Exception:
                idiomas = ["Português", "Inglês", "Francês", "Espanhol"]
            for idioma in idiomas:
                item = QListWidgetItem(idioma)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.idiomas.addItem(item)

    def carregar_dados(self):
        cursor = self.db.cursor
        # Pessoais
        cursor.execute("""
            SELECT genero, estado_civil, nacionalidade, data_nascimento, endereco, idiomas, habilidades
            FROM dados_pessoais
            WHERE membro_id = ?
        """, (self.membro_id,))
        dados = cursor.fetchone()
        if dados:
            genero_idx = self.genero.findText(dados[0] or "", Qt.MatchFlag.MatchFixedString)
            if genero_idx >= 0:
                self.genero.setCurrentIndex(genero_idx)
            self.estado_civil.setCurrentIndex(self.estado_civil.findText(dados[1] or "", Qt.MatchFlag.MatchFixedString))
            self.nacionalidade.setCurrentIndex(self.nacionalidade.findText(dados[2] or "", Qt.MatchFlag.MatchFixedString))
            if dados[3]:
                from PyQt6.QtCore import QDate
                try:
                    date = QDate.fromString(dados[3], "yyyy-MM-dd")
                    if date.isValid():
                        self.data_nascimento.setDate(date)
                except Exception:
                    pass
            self.endereco.setText(dados[4] or "")
            # Seleciona idiomas salvos
            if dados[5]:
                idiomas_salvos = [i.strip() for i in dados[5].split(",")]
                for i in range(self.idiomas.count()):
                    item = self.idiomas.item(i)
                    if item.text() in idiomas_salvos:
                        item.setCheckState(Qt.CheckState.Checked)
            self.habilidades.setPlainText(dados[6] or "")

    def salvar_dados(self):
        cursor = self.db.cursor
        # Coleta idiomas selecionados
        idiomas_selecionados = []
        outro_selecionado = False
        for i in range(self.idiomas.count()):
            item = self.idiomas.item(i)
            if item.text() == "Outro" and item.checkState() == Qt.CheckState.Checked:
                outro_selecionado = True
            elif item.checkState() == Qt.CheckState.Checked:
                idiomas_selecionados.append(item.text())

        # Se "Outro" estiver selecionado, solicita novo idioma
        if outro_selecionado:
            novo_idioma, ok = QInputDialog.getText(self, "Novo idioma", "Digite o novo idioma:")
            if ok and novo_idioma:
                idiomas_path = os.path.join(os.path.dirname(__file__), '../../config/idiomas.json')
                try:
                    with open(idiomas_path, 'r', encoding='utf-8') as f:
                        idiomas = json.load(f)
                except Exception:
                    idiomas = []
                if novo_idioma not in idiomas:
                    idiomas.append(novo_idioma)
                    with open(idiomas_path, 'w', encoding='utf-8') as f:
                        json.dump(idiomas, f, ensure_ascii=False, indent=2)
                self.carregar_idiomas()
                # Seleciona o novo idioma
                for i in range(self.idiomas.count()):
                    item = self.idiomas.item(i)
                    if item.text() == novo_idioma:
                        item.setCheckState(Qt.CheckState.Checked)
                # Desmarca "Outro"
                for i in range(self.idiomas.count()):
                    item = self.idiomas.item(i)
                    if item.text() == "Outro":
                        item.setCheckState(Qt.CheckState.Unchecked)
                idiomas_selecionados.append(novo_idioma)

        # Buscar valor atual da foto
        cursor.execute("SELECT foto FROM dados_pessoais WHERE membro_id = ?", (self.membro_id,))
        foto_atual = None
        row = cursor.fetchone()
        if row:
            foto_atual = row[0]

        # Atualizar dados pessoais preservando foto
        cursor.execute("""
            INSERT OR REPLACE INTO dados_pessoais (
                membro_id, genero, estado_civil, nacionalidade, data_nascimento, endereco, foto, idiomas, habilidades
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            self.membro_id,
            self.genero.currentText(),
            self.estado_civil.currentText(),
            self.nacionalidade.currentText(),
            self.data_nascimento.date().toString("yyyy-MM-dd"),
            self.endereco.text(),
            foto_atual,
            ','.join(idiomas_selecionados),
            self.habilidades.toPlainText()
        ))
        self.db.conn.commit()

        # Atualiza member_profile se existir e fecha o form
        if hasattr(self, 'parent_profile') and self.parent_profile:
            try:
                self.parent_profile.carregar_dados()
            except Exception:
                pass
        self.close()
