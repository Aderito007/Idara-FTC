# Idara - Sistema de Gestão Modular

Idara é um sistema modular para gestão de membros, projetos, serviços e relatórios em ambientes institucionais. Desenvolvido em Python com PyQt6, oferece uma interface moderna, responsiva e altamente customizável.

## Estrutura Geral

```
Idara/
├── main.py                # Inicialização da aplicação
├── README.md              # Documentação do projeto
├── idara.db               # Banco de dados SQLite
├── assets/                # Imagens, ícones, arquivos
│   ├── icons/
│   ├── images/
├── config/                # Configurações e estilos
│   ├── settings.py
│   ├── styles.qss
├── controller/            # Controladores principais
│   ├── app_controller.py
│   ├── dock_controller.py
├── core/                  # Utilitários e acesso ao banco
│   ├── database.py
│   ├── utils.py
│   ├── validators.py
├── modules/               # Funcionalidades principais
│   ├── members/           # Gestão de membros
│   │   ├── member_profile.py
│   │   ├── member_profile_form.py
│   │   ├── member_list.py
│   │   ├── pdf_viewer_widget.py
│   │   └── ...
│   ├── projects/          # Gestão de projetos
│   ├── reports/           # Relatórios
│   ├── services/          # Serviços
├── services/              # Serviços auxiliares
│   ├── navigation_service.py
├── state/                 # Gerenciamento de estado
│   ├── state_manager.py
```

## Funcionalidades Principais

- Gestão de membros, contratos, serviços e projetos
- Cadastro e controle de projetos com orçamento geral
- Aba Contabilidade para controle financeiro dos projetos
- Sub-orçamentos por categoria dentro de cada projeto
- Lançamentos de receitas e despesas vinculados a categorias
- Campos de valor unitário, quantidade e valor total nos lançamentos
- Tabelas dinâmicas para categorias e lançamentos, com atualização automática
- Resumo financeiro por categoria e por projeto
- Integração entre cadastro de projetos e aba contabilidade (ComboBox sempre atualizado)

## Como usar

1. Cadastre projetos e membros normalmente
2. Na aba Contabilidade, selecione o projeto desejado
3. Adicione categorias (sub-orçamentos) para o projeto
4. Lance receitas ou despesas, informando valor unitário, quantidade e descrição
5. Acompanhe o saldo de cada categoria e o balanço geral do projeto
6. Novos projetos aparecem automaticamente na aba contabilidade

## Estrutura do Banco de Dados

- Tabela `projetos`: dados do projeto e orçamento geral
- Tabela `categorias_orcamento`: categorias/sub-orçamentos por projeto
- Tabela `lancamentos`: lançamentos financeiros com valor unitário, quantidade e valor total

## Observações

- O sistema é modular e expansível
- Todas as operações são refletidas em tempo real na interface
- Para dúvidas ou sugestões, consulte os arquivos de cada módulo

---
Desenvolvido por [Seu Nome/Instituição]