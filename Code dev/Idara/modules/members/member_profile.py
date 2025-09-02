# member_profile.py
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QFormLayout, QScrollArea, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument
from modules.members.member_profile_form import MemberProfileForm
from modules.members.pdf_viewer_widget import PdfViewerWidget


class MemberProfile(QWidget):
    def __init__(self, membro_id, db, parent_list=None):
        super().__init__()
        self.membro_id = membro_id
        self.db = db
        self.parent_list = parent_list
        self.setWindowTitle("👤 Perfil do Membro")
        self.resize(800, 1120)  # Proporção A4
        self.init_ui()
        self.carregar_dados()

    def init_ui(self):
        # Área principal A4 com rolagem
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        a4_widget = QWidget()
        a4_widget.setMinimumSize(800, 1120)
        a4_layout = QVBoxLayout(a4_widget)
        a4_layout.setContentsMargins(20, 20, 20, 20)
        a4_layout.setSpacing(12)

        # Foto e nome no topo, centralizados e compactos
        foto_nome_hbox = QHBoxLayout()
        foto_nome_hbox.setSpacing(2)
        foto_nome_hbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.foto_label = QLabel()
        self.foto_label.setFixedSize(120, 120)
        self.foto_label.setStyleSheet("border-radius: 40px; background: #eee; border: 2px solid #3498db;")
        self.foto_label.setScaledContents(True)
        self.foto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foto_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.foto_label.customContextMenuRequested.connect(self.abrir_menu_foto)
        self.foto_label.mouseDoubleClickEvent = self.abrir_dialogo_foto
        self.nome_label = QLabel()
        self.nome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-left: 16px;")
        self.nome_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        foto_nome_hbox.addWidget(self.foto_label)
        foto_nome_hbox.addWidget(self.nome_label)
        a4_layout.insertLayout(0, foto_nome_hbox)

        # Sessões lado a lado
        hbox = QHBoxLayout()
        institucional = QGroupBox("Institucional")
        pessoal = QGroupBox("Pessoal")
        institucional_layout = QFormLayout()
        pessoal_layout = QFormLayout()
        institucional.setLayout(institucional_layout)
        pessoal.setLayout(pessoal_layout)
        hbox.addWidget(institucional)
        hbox.addWidget(pessoal)
        a4_layout.addLayout(hbox)

        # Institucional widgets
        self.nome = QLabel()
        self.cargo = QLabel()
        self.departamento = QLabel()
        self.email = QLabel()
        self.telefone = QLabel()
        self.data_entrada = QLabel()
        institucional_layout.addRow("Nome:", self.nome)
        institucional_layout.addRow("Cargo:", self.cargo)
        institucional_layout.addRow("Departamento:", self.departamento)
        institucional_layout.addRow("Email:", self.email)
        institucional_layout.addRow("Telefone:", self.telefone)
        institucional_layout.addRow("Data de Entrada:", self.data_entrada)

        # Pessoal widgets
        self.genero = QLabel()
        self.estado_civil = QLabel()
        self.nacionalidade = QLabel()
        self.data_nascimento = QLabel()
        self.endereco = QLabel()
        self.habilidades = QLabel()
        self.idiomas = QLabel()
        pessoal_layout.addRow("Gênero:", self.genero)
        pessoal_layout.addRow("Estado Civil:", self.estado_civil)
        pessoal_layout.addRow("Nacionalidade:", self.nacionalidade)
        pessoal_layout.addRow("Data de Nascimento:", self.data_nascimento)
        pessoal_layout.addRow("Endereço:", self.endereco)
        pessoal_layout.addRow("Idiomas:", self.idiomas)
        pessoal_layout.addRow("Habilidades:", self.habilidades)

        # Arquivos e visualizador PDF
        arquivos_box = QGroupBox("Arquivos Anexados")
        arquivos_layout = QVBoxLayout()
        # Lista horizontal de arquivos
        self.arquivos_hbox = QHBoxLayout()
        arquivos_layout.addLayout(self.arquivos_hbox)
        self.btn_add_arquivo = QPushButton("Adicionar Arquivo")
        self.btn_add_arquivo.clicked.connect(self.upload_arquivo)
        arquivos_layout.addWidget(self.btn_add_arquivo)
        from modules.members.pdf_viewer_widget import PdfViewerWidget
        self.pdf_viewer = PdfViewerWidget(self)
        arquivos_layout.addWidget(self.pdf_viewer)
        arquivos_box.setLayout(arquivos_layout)
        a4_layout.addWidget(arquivos_box)

        # Botões
        self.add_info_btn = QPushButton("✏️ Editar Informações")
        self.add_info_btn.setStyleSheet("background: #2980b9; color: white; font-weight: bold; border-radius: 6px; padding: 6px 16px;")
        self.add_info_btn.clicked.connect(self.abrir_formulario)
        self.atualizar_btn = QPushButton("🔄 Atualizar")
        self.atualizar_btn.setStyleSheet("background: #27ae60; color: white; font-weight: bold; border-radius: 6px; padding: 6px 16px;")
        self.atualizar_btn.clicked.connect(self.carregar_dados)
        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.add_info_btn)
        btn_hbox.addWidget(self.atualizar_btn)
        a4_layout.addLayout(btn_hbox)

        scroll.setWidget(a4_widget)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        # Salvar layouts para uso posterior
        self.institucional_layout = institucional_layout
        self.pessoal_layout = pessoal_layout


    def carregar_dados(self):
        try:
            cursor = self.db.cursor
            # Buscar dados institucionais do membro
            cursor.execute("SELECT nome, cargo, departamento, email, telefone, data_entrada FROM membros WHERE id = ?", (self.membro_id,))
            dados_inst = cursor.fetchone()
            if dados_inst:
                self.nome.setText(dados_inst[0] or "")
                self.nome_label.setText(dados_inst[0] or "")
                self.cargo.setText(dados_inst[1] or "")
                self.departamento.setText(dados_inst[2] or "")
                self.email.setText(dados_inst[3] or "")
                self.telefone.setText(dados_inst[4] or "")
                self.data_entrada.setText(dados_inst[5] or "")

            cursor.execute("""
                SELECT genero, estado_civil, nacionalidade, data_nascimento, endereco, foto, idiomas, habilidades
                FROM dados_pessoais
                WHERE membro_id = ?
            """, (self.membro_id,))
            dados_pessoais = cursor.fetchone()
            if dados_pessoais:
                self.genero.setText(dados_pessoais[0] or "")
                self.estado_civil.setText(dados_pessoais[1] or "")
                self.nacionalidade.setText(dados_pessoais[2] or "")
                self.data_nascimento.setText(dados_pessoais[3] or "")
                self.endereco.setText(dados_pessoais[4] or "")
                foto_path = dados_pessoais[5]
                if foto_path:
                    self.set_foto_circular(foto_path)
                else:
                    self.foto_label.clear()
                self.idiomas.setText(dados_pessoais[6] or "")
                self.habilidades.setText(dados_pessoais[7] or "")

            # Arquivos pessoais (lista horizontal de botões)
            cursor.execute("SELECT tipo, arquivo FROM arquivos_pessoais WHERE membro_id = ?", (self.membro_id,))
            arquivos = cursor.fetchall()
            # Limpa a lista horizontal
            while self.arquivos_hbox.count():
                item = self.arquivos_hbox.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            primeiro_pdf = None
            for tipo, arquivo in arquivos:
                nome = os.path.basename(arquivo)
                nome_sem_ext = os.path.splitext(nome)[0]
                btn = QPushButton(nome_sem_ext)
                btn.setToolTip(arquivo)
                btn.clicked.connect(lambda checked, arq=arquivo: self.abrir_pdf(arq))
                self.arquivos_hbox.addWidget(btn)
                if not primeiro_pdf and nome.lower().endswith('.pdf'):
                    primeiro_pdf = arquivo
            if primeiro_pdf:
                self.pdf_viewer.load_pdf(primeiro_pdf)
        except Exception as e:
            from PyQt6.QtWidgets import QLabel
            erro_label = QLabel(f"Erro ao carregar dados: {e}")
            self.arquivos_hbox.addWidget(erro_label)

    # Método de salvar removido, pois não é mais necessário

    def abrir_formulario(self):
        self.form_window = MemberProfileForm(self.membro_id, self.db, parent_profile=self)
        self.form_window.show()

    def upload_arquivo(self):
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            if file_dialog.exec():
                file_paths = file_dialog.selectedFiles()
                if file_paths:
                    file_path = file_paths[0]
                    import os, shutil
                    dest_dir = os.path.join(os.path.dirname(__file__), '../../assets/files')
                    os.makedirs(dest_dir, exist_ok=True)
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(dest_dir, file_name)
                    try:
                        shutil.copy(file_path, dest_path)
                        cursor = self.db.cursor
                        cursor.execute(
                            "INSERT INTO arquivos_pessoais (membro_id, tipo, arquivo) VALUES (?, ?, ?)",
                            (self.membro_id, 'outro', dest_path)
                        )
                        self.db.conn.commit()
                        QMessageBox.information(self, "Sucesso", f"Arquivo '{file_name}' adicionado!")
                        self.carregar_dados()
                    except Exception as e:
                        QMessageBox.critical(self, "Erro", f"Falha ao adicionar arquivo: {e}")
            
    def abrir_menu_foto(self, pos):
            menu = QMessageBox()
            menu.setText("Deseja alterar a foto?")
            menu.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            ret = menu.exec()
            if ret == QMessageBox.StandardButton.Yes:
                self.selecionar_foto()

    def abrir_dialogo_foto(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selecionar_foto()

    def selecionar_foto(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Imagens (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                import shutil
                dest_dir = os.path.join(os.path.dirname(__file__), '../../assets/images')
                os.makedirs(dest_dir, exist_ok=True)
                file_name = f"foto_{self.membro_id}{os.path.splitext(file_path)[1]}"
                dest_path = os.path.join(dest_dir, file_name)
                try:
                    shutil.copy(file_path, dest_path)
                    cursor = self.db.cursor
                    cursor.execute(
                        "UPDATE dados_pessoais SET foto = ? WHERE membro_id = ?",
                        (dest_path, self.membro_id)
                    )
                    self.db.conn.commit()
                    # Exibir foto circular
                    self.set_foto_circular(dest_path)
                    QMessageBox.information(self, "Foto", "Foto atualizada com sucesso!")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Falha ao salvar foto: {e}")

    def set_foto_circular(self, foto_path):
        from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
        from PyQt6.QtCore import Qt
        size = self.foto_label.size()
        pixmap = QPixmap(foto_path).scaled(size.width(), size.height(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        final = QPixmap(size.width(), size.height())
        final.fill(Qt.GlobalColor.transparent)
        painter = QPainter(final)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size.width(), size.height())
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        self.foto_label.setPixmap(final)

    def closeEvent(self, event):
        # Remove referência da janela aberta no MemberList
        try:
            if self.parent_list and self.membro_id in self.parent_list.perfil_windows:
                self.parent_list.perfil_windows.pop(self.membro_id, None)
        except Exception:
            pass
        super().closeEvent(event)

    def abrir_pdf(self, arquivo):
        self.pdf_viewer.load_pdf(arquivo)


