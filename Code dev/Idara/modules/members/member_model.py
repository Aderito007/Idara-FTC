class MemberModel:
    
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor

    def salvar(self, dados):
        self.db.insert_member(dados)
        
    def excluir(self, membro_id):
            self.db.cursor.execute("DELETE FROM membros WHERE id = ?", (membro_id,))
            self.db.conn.commit()
    def get_all(self):
        self.cursor.execute("""
            SELECT id, nome, cargo, email, telefone, departamento, data_entrada
            FROM membros
            ORDER BY id DESC
        """)
        rows = self.cursor.fetchall()
        return [
            {
                "id": r[0],
                "nome": r[1],
                "cargo": r[2],
                "email": r[3],
                "telefone": r[4],
                "departamento": r[5],
                "data_entrada": r[6]
            }
            for r in rows
        ]

    def listar_membros(self):
        self.cursor.execute("""
            SELECT id, nome, cargo, email, telefone, departamento, data_entrada
            FROM membros
            ORDER BY data_entrada DESC
        """)
        rows = self.cursor.fetchall()
        return [
            {
                "id": r[0],
                "nome": r[1],
                "cargo": r[2],
                "email": r[3],
                "telefone": r[4],
                "departamento": r[5],
                "data_entrada": r[6]
            }
            for r in rows
        ]

    def buscar_por_nome(self, nome):
        self.cursor.execute("""
            SELECT id, nome, cargo, email, telefone, departamento, data_entrada
            FROM membros
            WHERE LOWER(nome) = LOWER(?)
            LIMIT 1
        """, (nome,))
        r = self.cursor.fetchone()
        if r:
            return {
                "id": r[0],
                "nome": r[1],
                "cargo": r[2],
                "email": r[3],
                "telefone": r[4],
                "departamento": r[5],
                "data_entrada": r[6]
            }
        return None

    def nome_duplicado(self, nome):
        return self.db.nome_exists(nome)

    def email_duplicado(self, email):
        return self.db.email_exists(email)

    def atualizar(self, dados):
        self.db.cursor.execute("""
            UPDATE membros
            SET nome = ?, cargo = ?, email = ?, telefone = ?, departamento = ?, data_entrada = ?
            WHERE id = ?
        """, (
            dados["nome"],
            dados["cargo"],
            dados["email"],
            dados["telefone"],
            dados["departamento"],
            dados["data_entrada"],
            dados["id"]
        ))
        self.db.conn.commit()    
