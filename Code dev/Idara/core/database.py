import sqlite3

class DBManager:
    def __init__(self, db_path="idara.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self._create_config()
        self._create_membros()
        self._create_dados_pessoais()
        self._create_contratos()
        self._create_servicos()
        self._create_projetos()
        self._create_arquivos_pessoais()
        self._create_categorias_orcamento()
        self._create_lancamentos()

    def _create_membros(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS membros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                cargo TEXT,
                email TEXT,
                telefone TEXT,
                departamento TEXT,
                data_entrada TEXT
            )
        """)
        self.conn.commit()

    def _create_dados_pessoais(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_pessoais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER UNIQUE,
                genero TEXT,
                estado_civil TEXT,
                nacionalidade TEXT,
                data_nascimento TEXT,
                endereco TEXT,
                foto TEXT,
                idiomas TEXT,
                habilidades TEXT,
                FOREIGN KEY (membro_id) REFERENCES membros(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def _create_arquivos_pessoais(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS arquivos_pessoais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER,
                tipo TEXT,
                arquivo TEXT,
                FOREIGN KEY (membro_id) REFERENCES membros(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def _create_contratos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                colaborador_id INTEGER,
                servico_id INTEGER,
                tipo TEXT, -- vínculo, serviço, parcial, etc.
                inicio TEXT,
                fim TEXT,
                salario REAL,
                observacoes TEXT,
                FOREIGN KEY (colaborador_id) REFERENCES membros(id) ON DELETE CASCADE,
                FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def _create_servicos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                membro_id INTEGER,
                projeto_id INTEGER,
                local_servico TEXT,
                papel TEXT,
                descricao TEXT,
                FOREIGN KEY (membro_id) REFERENCES membros(id) ON DELETE CASCADE,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def _create_projetos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                cliente TEXT,
                orcado_em REAL DEFAULT 0,
                inicio TEXT,
                fim TEXT,
                status TEXT,
                descricao TEXT
            )
        """)
        self.conn.commit()

    def _create_config(self):
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT
                )
            """)
            self.conn.commit()

    def _create_categorias_orcamento(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_orcamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projeto_id INTEGER,
                nome TEXT NOT NULL,
                valor_orcado REAL DEFAULT 0,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id)
            )
        """)
        self.conn.commit()

    def _create_lancamentos(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projeto_id INTEGER,
                categoria_id INTEGER,
                tipo TEXT CHECK(tipo IN ('Receita','Despesa')),
                valor_unitario REAL NOT NULL,
                quantidade REAL NOT NULL DEFAULT 1,
                valor_total REAL NOT NULL,
                descricao TEXT,
                data TEXT,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id),
                FOREIGN KEY (categoria_id) REFERENCES categorias_orcamento(id)
            )
        """)
        self.conn.commit()

    def insert_member(self, dados):
        self.cursor.execute("SELECT COUNT(*) FROM membros WHERE nome = ?", (dados["nome"],))
        row = self.cursor.fetchone()
        if row and row[0] > 0:
            raise ValueError("Membro já cadastrado.")

        self.cursor.execute("""
            INSERT INTO membros (nome, cargo, email, telefone, departamento, data_entrada)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dados["nome"],
            dados["cargo"],
            dados["email"],
            dados["telefone"],
            dados["departamento"],
            dados["data_entrada"]
        ))
        self.conn.commit()

    def close(self):
        self.conn.close()


    def nome_exists(self, nome):
        query = "SELECT COUNT(*) FROM membros WHERE nome = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (nome,))
        row = cursor.fetchone()
        return row[0] > 0 if row else False

    def email_exists(self, email):
        query = "SELECT COUNT(*) FROM membros WHERE email = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        return row[0] > 0 if row else False

