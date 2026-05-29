# 💈 Barber API

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.136%2B-009485.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Uma API REST moderna e escalável para gerenciamento completo de sistemas de agendamento em barbearias, construída com as melhores práticas de desenvolvimento Python e arquitetura de software.

---

## ✨ Features

- 🔐 **Autenticação JWT** - Sistema seguro de autenticação com tokens JWT
- 👥 **Multi-Tenancy** - Suporte completo para múltiplos tenants (barbearias independentes)
- 📅 **Agendamentos** - Gerenciamento completo de agendamentos e slots de horário
- 💇 **Barbeiros** - Cadastro e gerenciamento de barbeiros e seus serviços
- 📋 **Clientes** - Sistema de clientes com histórico de agendamentos
- 🛠️ **Serviços** - Catálogo de serviços com preços e duração
- ⏰ **Horários de Trabalho** - Configuração de horários por barbeiro e dia da semana
- 🧪 **Testes Automatizados** - Testes unitários e de integração com alta cobertura
- 🗄️ **Migrations** - Controle de versão do banco com Alembic
- 📚 **Documentação Automática** - Swagger e ReDoc integrados

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Descrição |
|-----------|--------|-----------|
| [Python](https://www.python.org/) | 3.12+ | Linguagem de programação |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.136.1 | Framework web assíncrono |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.0.49 | ORM para banco de dados |
| [Pydantic](https://docs.pydantic.dev/) | 2.13.4 | Validação de dados |
| [Alembic](https://alembic.sqlalchemy.org/) | 1.18.4 | Migrations de banco de dados |
| [Uvicorn](https://www.uvicorn.org/) | 0.46.0 | Servidor ASGI |
| [PyJWT](https://pyjwt.readthedocs.io/) | 3.5.0 | Autenticação JWT |
| [Bcrypt](https://github.com/pyca/bcrypt) | 4.0.1 | Hash de senhas |
| [Pytest](https://docs.pytest.org/) | 9.0.3+ | Framework de testes |
| [Poetry](https://python-poetry.org/) | Latest | Gerenciador de dependências |

---

## 📁 Estrutura do Projeto

```
barber_api/
├── alembic/                          # Migrations do banco de dados
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                     # Scripts de migração
│
├── app/
│   ├── __init__.py
│   ├── main.py                       # Entry point da aplicação
│   ├── models.py                     # Modelos SQLAlchemy
│   │
│   ├── core/
│   │   ├── auth.py                   # Lógica de autenticação JWT
│   │   ├── config.py                 # Configurações da aplicação
│   │   ├── database.py               # Conexão com banco de dados
│   │   └── dependencies.py           # Dependências do FastAPI
│   │
│   ├── routes/                       # Rotas da API
│   │   ├── appointment.py            # CRUD de agendamentos
│   │   ├── auth.py                   # Login e registro
│   │   ├── clientes.py               # Gerenciamento de clientes
│   │   ├── services.py               # Catálogo de serviços
│   │   ├── slots.py                  # Slots de horário disponíveis
│   │   ├── tenants.py                # Multi-tenancy
│   │   ├── user.py                   # Gerenciamento de usuários
│   │   ├── user_service.py           # Serviços por usuário
│   │   └── workschedules.py          # Horários de trabalho
│   │
│   ├── schemas/                      # Schemas de validação (Pydantic)
│   │   ├── appointment_schema.py
│   │   ├── client_schema.py
│   │   ├── service_schema.py
│   │   ├── slot_schema.py
│   │   ├── tenant_schema.py
│   │   ├── user_schema.py
│   │   ├── user_service_schema.py
│   │   └── work_schedule.py
│   │
│   └── services/                     # Camada de negócio
│       ├── appointment_service.py
│       ├── client_service.py
│       ├── service_service.py
│       ├── slot_service.py
│       ├── tenant_service.py
│       ├── user_service_service.py
│       ├── user_service.py
│       └── work_schedule_service.py
│
├── tests/
│   ├── conftest.py                   # Configurações de testes
│   ├── test_main.py
│   │
│   ├── integration/                  # Testes de integração
│   │   ├── test_appointment_routes.py
│   │   ├── test_auth_routes.py
│   │   ├── test_client_routes.py
│   │   └── ...
│   │
│   └── unit/                         # Testes unitários
│       ├── test_appointment_service.py
│       ├── test_client_service.py
│       └── ...
│
├── .env.example                      # Exemplo de variáveis de ambiente
├── alembic.ini                       # Configuração do Alembic
├── pyproject.toml                    # Dependências e configurações do Poetry
└── README.md                         # Este arquivo
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.12 ou superior
- Poetry
- Banco de dados PostgreSQL (recomendado) ou SQLite

### Passo 1: Clone o Repositório

```bash
git clone https://github.com/seu-usuario/barber-api.git
cd barber-api
```

### Passo 2: Configure o Ambiente Virtual

**Usando Poetry:**
```bash
# Instalar Poetry (se ainda não tiver)
curl -sSL https://install.python-poetry.org | python3 -

# Criar ambiente virtual e instalar dependências
poetry install
poetry shell
```

### Passo 3: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env com suas configurações
nano .env
```

### Passo 4: Executar Migrations

```bash
# Criar tabelas no banco de dados
alembic upgrade head
```

### Passo 5: Iniciar o Servidor

```bash
# Com Poetry
poetry run uvicorn app.main:app --reload

# Ou diretamente
uvicorn app.main:app --reload
```

O servidor estará disponível em `http://localhost:8000`

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/barber_api
# Para SQLite em desenvolvimento:
DATABASE_URL=sqlite:///./barber_api.db

# Autenticação JWT
SECRET_KEY=sua_chave_secreta_super_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Timezone
TIME_ZONE=America/Sao_Paulo

# Desenvolvimento
DEBUG=True
ENVIRONMENT=development
```

### Gerando uma Chave Secreta Segura

```python
# Python shell
import secrets
print(secrets.token_urlsafe(32))
```

---

## 📚 Exemplos de Uso

### 1. Documentação Interativa

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


### 2. Com Python (usando requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "usuario@example.com",
        "password": "senha123"
    }
)
token = response.json()["access_token"]

# Usar token nas próximas requisições
headers = {"Authorization": f"Bearer {token}"}

# Listar clientes
response = requests.get(f"{BASE_URL}/clientes", headers=headers)
print(response.json())
```

---

## 🧪 Testes

### Executar Todos os Testes

```bash
pytest
```

### Executar Apenas Testes de Integração

```bash
pytest tests/integration/
```

### Executar Apenas Testes Unitários

```bash
pytest tests/unit/
```

---


## 🤝 Contribuindo

Contributions são bem-vindas! Por favor, siga os passos abaixo:

### 1. Fork o Projeto

```bash
git clone https://github.com/seu-usuario/barber-api.git
```

### 2. Crie uma Branch para sua Feature

```bash
git checkout -b feature/AmazingFeature
```

### 3. Commit suas Mudanças

```bash
git commit -m 'Add some AmazingFeature'
```

### 4. Push para a Branch

```bash
git push origin feature/AmazingFeature
```

### 5. Abra um Pull Request

- Descreva as mudanças realizadas
- Certifique-se de que todos os testes passam
- Mantenha a cobertura de testes acima de 80%

### Diretrizes de Contribuição

- ✅ Escreva testes para novas features
- ✅ Siga o PEP 8 para estilo de código
- ✅ Mantenha o código limpo e legível
- ✅ Atualize a documentação conforme necessário
- ✅ Use type hints em todo o código

---

## 📝 Licença

Este projeto é licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🎯 Roadmap

- [ ] Autenticação com Google/GitHub
- [ ] Sistema de notificações por email/SMS
- [ ] Relatórios e analytics
- [ ] Aplicação mobile (React Native/Flutter)
- [ ] Integração com sistemas de pagamento
- [ ] Dashboard com métricas em tempo real
- [ ] Sistema de avaliações

---

## 👨‍💻 Autor

**Matheus Marques Ferreira dos Santos**
- GitHub: [@matheus-mfs](https://github.com/matheus-mfs)
- Email: mmferreira2000@gmail.com

---

**Feito com ❤️ e Python**

