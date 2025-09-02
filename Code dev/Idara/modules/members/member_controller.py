from modules.members.member_model import MemberModel

class MemberController:
    
    def __init__(self, db):
        self.db = db
        self.model = MemberModel(db)

    def excluir_membro(self, membro_id):
        self.model.excluir(membro_id)
        
    def cadastrar_membro(self, dados):
        if self.model.nome_duplicado(dados["nome"]):
            raise ValueError("Já existe um membro com este nome.")
        if self.model.email_duplicado(dados["email"]):
            raise ValueError("Já existe um membro com este email.")
        self.model.salvar(dados)

    def listar_membros(self):
        return self.model.get_all()

    def obter_membros(self):
        return self.model.listar_membros()

    def buscar_por_nome(self, nome):
        return self.model.buscar_por_nome(nome)
    def atualizar_membro(self, dados):
        self.model.atualizar(dados)