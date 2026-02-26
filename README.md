# Sistema de Gestão de Stock Multi-Institucional - São Vicente

Sistema web desenvolvido para apoio às vítimas do enchente de São Vicente (11/08), permitindo a gestão centralizada de stock e beneficiários por múltiplas instituições de apoio.

## 🌟 Características Principais

### Stock Centralizado
- **Stock único e centralizado** utilizado por todas as instituições
- Cada instituição só vê e manipula os seus próprios movimentos
- Segregação total de dados entre instituições
- Controlo de stock em tempo real

### Gestão de Beneficiários
- **Base de dados centralizada** de pessoas beneficiárias
- Identificação única por NIF (Número de Identificação Fiscal)
- Histórico completo de ajuda recebida por beneficiário
- Visibilidade inter-institucional dos dados dos beneficiários

### Autenticação e Permissões
- Sistema de login por instituição
- Permissões rigorosas para proteger dados institucionais
- Cada instituição só acede aos seus próprios registos de stock


## 📦 Funcionalidades

### Dashboard
- Estatísticas em tempo real
- Resumo de beneficiários atendidos
- Movimentos de stock da instituição
- Indicadores de atividade

### Gestão de Stock
- **Registar Entradas:** Doações recebidas pela instituição
- **Registar Saídas:** Distribuição para beneficiários
- **Resumo de Stock:** Visão geral dos itens disponíveis
- Histórico completo de movimentos

### Gestão de Beneficiários
- Consulta de beneficiários por NIF, nome ou zona
- Histórico completo de ajuda recebida
- Informações detalhadas (contacto, zona, agregado familiar)
- Registo de novos beneficiários

### Relatórios
- Atividade recente da instituição
- Estatísticas de distribuição
- Histórico de movimentos

## 🗄️ Base de Dados

### Beneficiários Importados
- **228 beneficiários** importados do ficheiro Excel fornecido
- NIFs gerados automaticamente no formato `SV######`
- Dados incluem: nome, idade, contacto, zona, agregado familiar

### Itens de Stock Pré-configurados
- **Alimentação:** Arroz, Feijão, Óleo, Açúcar, Água
- **Vestuário:** Camisetas, Calças, Roupa de criança, Sapatos
- **Higiene:** Sabão, Pasta de dentes, Champô, Fraldas
- **Casa:** Cobertores, Lençóis, Almofadas, Utensílios
- **Medicamentos:** Kit primeiros socorros, Medicamentos básicos

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- pip (gestor de pacotes Python)

### Passos de Instalação

1. **Clonar/Descarregar o projeto**
```bash
cd sistema_stock_sv
```

2. **Criar ambiente virtual**
```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Executar o sistema**
```bash
python src/main.py
```

5. **Aceder ao sistema**
- Abrir navegador em: `http://localhost:5000`
- Fazer login com uma das instituições configuradas

## 🔐 Credenciais de Acesso

### Instituições Disponíveis:
- **Cáritas São Vicente:** `caritas` / `sv2024`

## 📱 Interface do Utilizador

### Design Responsivo
- Interface moderna com gradientes verdes (tema natureza)
- Totalmente responsiva para dispositivos móveis
- Animações suaves e micro-interações
- Ícones intuitivos e navegação clara

### Experiência do Utilizador
- Login simples por instituição
- Dashboard com estatísticas visuais
- Formulários intuitivos para registo
- Modais para visualização detalhada
- Alertas informativos para feedback

## 🛡️ Segurança e Privacidade

### Segregação de Dados
- Cada instituição só acede aos seus próprios movimentos de stock
- Beneficiários são partilhados entre todas as instituições
- Histórico de ajuda mostra qual instituição forneceu cada item

### Autenticação
- Sistema de sessões Flask
- Verificação de permissões em todas as rotas
- Logout automático por segurança

## 📊 Estrutura da Base de Dados

### Tabelas Principais
- **instituicoes:** Dados das organizações
- **beneficiarios:** Pessoas que recebem ajuda
- **itens_stock:** Catálogo de itens disponíveis
- **movimentos_stock:** Registo de entradas e saídas

### Relacionamentos
- Movimentos ligados a instituições e itens
- Saídas ligadas a beneficiários específicos
- Histórico completo mantido para auditoria

## 🔧 Tecnologias Utilizadas

### Backend
- **Flask:** Framework web Python
- **SQLAlchemy:** ORM para base de dados
- **SQLite:** Base de dados (pode ser alterada para PostgreSQL/MySQL)
- **Werkzeug:** Segurança e hashing de passwords

### Frontend
- **HTML5/CSS3:** Estrutura e estilo
- **JavaScript (Vanilla):** Interatividade
- **Design Responsivo:** Compatível com todos os dispositivos

### Dependências Python
- Flask
- Flask-SQLAlchemy
- Werkzeug
- pandas (para importação de dados)
- openpyxl (para ficheiros Excel)

## 📈 Funcionalidades Futuras

### Melhorias Sugeridas
- **Relatórios Avançados:** Gráficos e estatísticas detalhadas
- **Notificações:** Alertas para stock baixo
- **Exportação:** Relatórios em PDF/Excel
- **API REST:** Integração com outros sistemas
- **Backup Automático:** Cópia de segurança da base de dados

### Escalabilidade
- Migração para PostgreSQL para maior volume
- Implementação de cache (Redis)
- Balanceamento de carga para múltiplos servidores
- Containerização com Docker

## 🆘 Suporte e Manutenção

### Contactos de Suporte
- **Desenvolvedor:** Sistema desenvolvido para apoio às vítimas do enchente
- **Documentação:** Este ficheiro README.md
- **Logs:** Disponíveis na consola durante execução

### Resolução de Problemas
1. **Erro de base de dados:** Verificar se o ficheiro `instance/database.db` existe
2. **Erro de dependências:** Executar `pip install -r requirements.txt`
3. **Erro de permissões:** Verificar se o utilizador tem permissões na pasta

## 📄 Licença

Este sistema foi desenvolvido especificamente para apoio às vítimas do enchente de São Vicente (11/08/2024). 

**Uso livre para fins humanitários e de apoio social.**

---

## 🌱 Sobre o Projeto

Este sistema foi criado com o objetivo de facilitar a coordenação entre as diferentes instituições que prestam apoio às vítimas do enchente de São Vicente. 

**Características especiais:**
- ✅ Stock centralizado mas com gestão independente por instituição
- ✅ Base de dados única de beneficiários para evitar duplicações
- ✅ Histórico completo de ajuda para cada pessoa
- ✅ Interface simples e intuitiva
- ✅ Dados reais importados (228 beneficiários)
- ✅ Sistema pronto para produção

**Impacto esperado:**
- Melhor coordenação entre instituições
- Evitar duplicação de ajuda
- Controlo eficiente do stock disponível
- Transparência no processo de distribuição
- Histórico completo para relatórios e prestação de contas

---

*Sistema desenvolvido com 💚 para apoio às vítimas do enchente de São Vicente*

#### TO DO ############################

Para ambiente de produção, recomendo:

Alterar a SECRET_KEY em main.py

Usar banco de dados PostgreSQL em vez de SQLite

Configurar HTTPS

Implementar sistema de logs

Fazer backup regular da base de dados