#  Sistema de Gestão de Stock - Enchente São Vicente

Sistema web desenvolvido para apoiar as vítimas da enchente de São Vicente (11/08), permitindo a gestão centralizada de stock e de beneficiários, com a participação de múltiplas instituições de apoio.

##  Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Credenciais de Acesso](#credenciais-de-acesso)
- [API Endpoints](#api-endpoints)
- [Sistema de Alertas](#sistema-de-alertas)
- [Segurança](#segurança)
- [Contribuição](#contribuição)
- [Licença](#licença)

##  Visão Geral

O **Sistema de Gestão de Stock - Enchente São Vicente** foi desenvolvido para coordenar as doações e distribuição de ajuda às famílias afetadas pela enchente que ocorreu em São Vicente a 11 de agosto. O sistema permite que múltiplas instituições (Cáritas, Bombeiros, ONGs, etc.) registrem suas doações e distribuam itens de forma coordenada, evitando duplicações e garantindo que a ajuda chegue a quem mais precisa.

##  Funcionalidades

###  Gestão de Beneficiários
- Cadastro completo de beneficiários (NIF, nome, contacto, zona de residência)
- Consulta cruzada entre instituições para histórico de ajudas
- Histórico detalhado de todas as ajudas recebidas
- Filtros por zona, nome ou NIF

###  Gestão de Stock
- Registro de entradas (doações recebidas)
- Registro de saídas (distribuições)
- Controle de stock por item e categoria
- Resumo de stock com indicadores visuais

###  Gestão de Instituições
- Registro de novas instituições com validação
- Fluxo de aprovação de instituições (admin)
- Cada instituição tem username e password únicos
- Alteração de password segura

###  Sistema de Alertas Inteligentes
- Prevenção de distribuição excessiva para o mesmo beneficiário
- Alertas de distribuição muito frequente
- Sugestão de beneficiários prioritários
- Relatório de distribuição equitativa

###  Relatórios
- Relatórios mensais automatizados
- Exportação para impressão
- Estatísticas de distribuição
- Histórico de movimentos

##  Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.10+ | Linguagem principal |
| Flask | 2.3.3 | Framework web |
| PostgreSQL | 14+ | Banco de dados |
| SQLAlchemy | 3.1.1 | ORM |
| psycopg2 | 2.9.9 | Driver PostgreSQL |
| python-dotenv | 1.0.0 | Gerenciamento de variáveis de ambiente |
| Werkzeug | 2.3.7 | Segurança (hashing de passwords) |

##  Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [Python 3.10 ou superior](https://www.python.org/downloads/)
- [PostgreSQL 14 ou superior](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/) (opcional, para clonar o repositório)
- [pgAdmin](https://www.pgadmin.org/) (opcional, para gerenciar o banco de dados)

##  Instalação e Configuração

### 1. Clonar o repositório

```bash
git clone https://github.com/Edmilson-999/sistema-stock-sv.git
cd sistema-stock-sv
