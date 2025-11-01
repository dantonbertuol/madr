
# MADR - Minha Coleção Digital de Romances

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Uma API REST para gerenciar uma coleção digital de livros e autores, desenvolvida como projeto final de curso de FastAPI.


## 📑 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Decisões Técnicas](#-decisões-técnicas)
- [Como Executar](#-como-executar)
- [Endpoints da API](#-endpoints-da-api)
- [Autenticação](#-autenticação)
- [Funcionalidades Especiais](#-funcionalidades-especiais)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Contribuindo](#-contribuindo)
- [Autor](#-autor)


## 📖 Sobre o Projeto

O MADR (Minha Coleção Digital de Romances) é um sistema completo de gerenciamento de biblioteca pessoal que permite:
- Cadastro de usuários e autenticação JWT;
- Gerenciamento de autores (romancistas);
- Gerenciamento de livros;
- Busca avançada e filtros;
- Sanitização automática de dados.

O projeto foi desenvolvido seguindo boas práticas, incluindo testes automatizados, validação de dados com Pydantic e arquitetura organizada.

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e de alta performance.
- **Python 3.112+**: Linguagem de programação.
- **SQLAlchemy 2.0**: ORM com suporte a type hints modernos.
- **PostgreSQL**: Banco de dados relacional.
- **Pydantic**: Validação e serialização de dados.
- **UV**: Gerenciador de dependências.
- **Alembic**: Migrações.

### Segurança
- **pyjwt**: Implementação de JWT.
- **pwdlib[argon]**: Hash de senhas.
- **OAuth2**: Padrão de autenticação.

### Testes
- **pytest**: Framework de testes.
- **factory-boy**: Geração de dados de teste.
- **testcontainers**: Containers para testes.
- **freezegun**: Manipulação do tempo em testes.

### Infraestrutura
- **Docker**: Containerização do PostgreSQL e da aplicação.
- **Uvicorn**: Servidor ASGI.

## 💡 Decisões Técnicas

### Por que FastAPI?
FastAPI foi escolhido por sua alta performance, documentação automática (Swagger/OpenAPI), validação de dados integrada com Pydantic e suporte nativo a async/await. A documentação interativa facilita o desenvolvimento e teste dos endpoints.

### Por que SQLAlchemy 2.0 com Registry Pattern?
Foi optado pela versão mais recente do SQLAlchemy (2.0+) para usar type hints modernos com `Mapped` e `mapped_column`, tornando o código mais legível e com melhor suporte em IDEs. O padrão registry oferece maior flexibilidade na organização dos modelos.

### Por que PostgreSQL?
O PostgreSQL é um banco robusto, open-source e amplamente utilizado em produção. Suporta recursos avançados como transações ACID, indexação eficiente e alta confiabilidade.

### Sanitização de Dados
Foi implementada uma camada de sanitização que:
- Converte nomes para minúsculas;
- Remove espaços extras e caracteres especiais;
- Garante consistência dos dados.

Isso evita duplicidade por diferenças de capitalização e melhora a experiência de busca.

### Arquitetura em Camadas
O projeto foi organizado em camadas bem definidas:
- **Routers**: Endpoints e lógica de request/response;
- **Schemas**: Validação de entrada/saída com Pydantic;
- **Models**: Representação do banco de dados;
- **Core**: Configuração, autenticação e utilitários.

## 🚀 Como Executar

### Pré-requisitos
- Docker e Docker Compose
- Git

### Instalação

1. **Clone o repositório**
    ```bash
    git clone https://github.com/dantonbertuol/madr.git
    cd madr
    ```

2. **Configure as variáveis de ambiente**

    Renomeie o arquivo `.env.default` na raiz do projeto para `.env` e preencha as variáveis:
    - **DATABASE_URL**: URL do banco de dados, pode ficar em branco, pois é preenchida no docker-compose;
    - **SECRET_KEY**: Secret Key utilizada para criar os tokens, pode ser gerada com o seguinte comando python: 
        ```python
        import secrets

        key = secrets.token_hex(32)
        print(key)
        ```
    - **ALGORITHM**: Algoritmo para criar o token, por padrão, `HS256`;
    - **ACCESS_TOKEN_EXPIRE_MINUTES**: Tempo que o token irá durar, por padrão, 60 minutos.

3. **Inicie os containers**
    ```bash
    docker compose up -d
    ```

4. **Acesse a aplicação**

    A API estará disponível em: `http://localhost:8000`

    Documentação interativa (Swagger): `http://localhost:8000/docs`

### Executando os Testes

Para executar os testes, primeiramente o ambiente deve ser configurado, utilizando o comando `uv sync`.

Após isso, ative o ambiente virtual e execute os testes com:

```bash
task test
```

## 📚 Endpoints da API

### Usuários
- `POST /conta/` - Criar nova conta (público)
- `POST /conta/token` - Login e geração de token JWT
- `POST /conta/refresh_token` - Renovação de token
- `GET /conta/{id}` - Buscar usuário por ID (público)
- `PUT /conta/{id}` - Atualizar dados do usuário (requer autenticação e pode ser feito apenas pelo próprio usuário)
- `DELETE /conta/{id}` - Excluir conta (requer autenticação e pode ser feito apenas pelo próprio usuário)

### Romancistas
- `POST /romancista/` - Adicionar romancista (requer autenticação)
- `GET /romancista/` - Listar romancistas com filtros e paginação
- `GET /romancista/{id}` - Buscar romancista por ID
- `PATCH /romancista/{id}` - Atualizar romancista (requer autenticação)
- `DELETE /romancista/{id}` - Excluir romancista (requer autenticação)

### Livros
- `POST /livro/` - Adicionar livro (requer autenticação)
- `GET /livro/` - Listar livros com filtros (título, ano) e paginação
- `GET /livro/{id}` - Buscar livro por ID
- `PATCH /livro/{id}` - Atualizar livro (requer autenticação)
- `DELETE /livro/{id}` - Excluir livro (requer autenticação)

## 🔐 Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Para acessar endpoints protegidos:

1. Faça login em `/conta/token` com email e senha
2. Receba o `access_token` na resposta
3. Inclua o token no header da requisição: `Authorization: Bearer {token}`

Os tokens expiram em 60 minutos. Use `/conta/refresh_token` para renovar.

## 🔍 Funcionalidades Especiais

### Sanitização Automática
Nomes de romancistas e títulos de livros são automaticamente sanitizados:
- "Machado de Assis" → "machado de assis"
- "Edgar Allan Poe    " → "edgar allan poe"

### Paginação Inteligente
Listagens só aplicam paginação quando há mais de 20 resultados, otimizando a performance.

### Validações de Integridade
- Impede duplicidade de usernames, emails, romancistas ou títulos
- Valida existência do romancista ao criar/atualizar livros
- Verifica propriedade nas operações de usuário

### Tratamento de Erros
Mensagens claras e padronizadas:
- `400 BAD REQUEST` - Dados inválidos
- `401 UNAUTHORIZED` - Não autenticado
- `403 FORBIDDEN` - Sem permissão
- `404 NOT FOUND` - Recurso não encontrado
- `409 CONFLICT` - Conflito de dados (duplicidade)

## 📂 Estrutura do Projeto

```
.github/
    └── workflows/
        └── pipeline.yaml
madr/
    ├── routers/
        ├── contas.py
        ├── livros.py
        └── romancistas.py
    ├── __init__.py
    ├── app.py
    ├── database.py
    ├── models.py
    ├── schemas.py
    ├── security.py
    ├── settings.py
    └── utils.py
migrations/
    ├── versions/
        ├── 5257d1859b7c_add_created_at_and_update_at_in_livros_.py
        └── ff60df26779b_add_users_romancistas_and_livros_tables.py
    ├── env.py
    ├── README
    └── script.py.mako
tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_contas.py
    ├── test_db.py
    ├── test_livros.py
    ├── test_romancistas.py
    ├── test_security.py
    └── test_utils.py
.env.default
.gitignore
.python-version
alembic.ini
docker-compose.yaml
Dockerfile
entrypoint.sh
pyproject.toml
README.md
uv.lock
```

## 🧪 Testes

O projeto possui cobertura abrangente de testes, incluindo:
- Testes unitários para todas operações CRUD
- Testes de fluxo de autenticação
- Testes de cenários de erro (404, 401, 409, etc.)
- Testes de integridade do banco
- Testes de paginação e filtros

A meta é cobrir 100% dos caminhos críticos do código.

## 🤝 Contribuindo

Este é um projeto de aprendizado, mas sugestões e feedbacks são bem-vindos! Sinta-se à vontade para:
1. Fazer um fork do projeto
2. Criar uma branch de feature (`git checkout -b feature/MadrFeature`)
3. Comitar suas alterações (`git commit -m 'Adiciona MadrFeature'`)
4. Fazer push para a branch (`git push origin feature/MadrFeature`)
5. Abrir um Pull Request

## 👤 Autor

**Danton Bertuol**

- GitHub: [dantonbertuol](https://github.com/dantonbertuol)
- Email: dantonjb@gmail.com