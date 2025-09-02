import json

class ServiceRepository:
    def get_projetos_dict(self):
        self.cursor.execute("SELECT id, nome FROM projetos")
        return {pid: nome for pid, nome in self.cursor.fetchall()}
    def get_membros_dict(self):
        self.cursor.execute("SELECT id, nome FROM membros")
        return {mid: nome for mid, nome in self.cursor.fetchall()}
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def get_config_list(self, key):
        self.cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return json.loads(row[0]) if row and row[0] else []

    def save_config_list(self, key, items):
        value = json.dumps(items)
        self.cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        self.db.conn.commit()

    def get_membros(self):
        self.cursor.execute("SELECT id, nome FROM membros")
        return self.cursor.fetchall()

    def get_projetos(self):
        self.cursor.execute("SELECT id, nome FROM projetos")
        return self.cursor.fetchall()

    def get_services(self):
        self.cursor.execute("SELECT id, membro_id, projeto_id, local_servico, papel, descricao FROM servicos ORDER BY id DESC")
        return self.cursor.fetchall()

    def get_contrato_by_servico(self, servico_id):
        self.cursor.execute("SELECT tipo, fim, salario FROM contratos WHERE servico_id = ?", (servico_id,))
        return self.cursor.fetchone()

    def get_membro_id(self, nome):
        self.cursor.execute("SELECT id FROM membros WHERE nome = ?", (nome,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_projeto_id(self, nome):
        self.cursor.execute("SELECT id FROM projetos WHERE nome = ?", (nome,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def insert_servico(self, membro_id, projeto_id, local_servico, papel, descricao):
        self.cursor.execute(
            "INSERT INTO servicos (membro_id, projeto_id, local_servico, papel, descricao) VALUES (?, ?, ?, ?, ?)",
            (membro_id, projeto_id, local_servico, papel, descricao)
        )
        self.db.conn.commit()
        return self.cursor.lastrowid

    def update_servico(self, servico_id, membro_id, projeto_id, local_servico, papel, descricao):
        self.cursor.execute(
            "UPDATE servicos SET membro_id = ?, projeto_id = ?, local_servico = ?, papel = ?, descricao = ? WHERE id = ?",
            (membro_id, projeto_id, local_servico, papel, descricao, servico_id)
        )
        self.db.conn.commit()

    def delete_servico(self, servico_id):
        self.cursor.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
        self.db.conn.commit()

    def insert_contrato(self, membro_id, servico_id, tipo, inicio, fim, salario, observacoes):
        self.cursor.execute(
            "INSERT INTO contratos (colaborador_id, servico_id, tipo, inicio, fim, salario, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (membro_id, servico_id, tipo, inicio, fim, salario, observacoes)
        )
        self.db.conn.commit()

    def update_contrato(self, servico_id, membro_id, tipo, inicio, fim, salario, observacoes):
        self.cursor.execute(
            "UPDATE contratos SET colaborador_id = ?, servico_id = ?, tipo = ?, inicio = ?, fim = ?, salario = ?, observacoes = ? WHERE servico_id = ?",
            (membro_id, servico_id, tipo, inicio, fim, salario, observacoes, servico_id)
        )
        self.db.conn.commit()
