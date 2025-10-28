# 🎓 AluConnect

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-orange)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-%232496ED.svg?&style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

Plataforma educacional desenvolvida em Django + Celery + Redis + PostgreSQL, com suporte à geração automática de certificados e integração com APIs de IA.  
O projeto utiliza Docker para orquestração dos serviços e oferece um ambiente de desenvolvimento totalmente containerizado.

---

## 📑 Sumário
- [Tecnologias utilizadas](#-tecnologias-utilizadas)
- [Funcionalidades e resultados do case](#-funcionalidades-e-resultados-do-case)
- [Executando o projeto](#-executando-o-projeto)
- [Rodando os testes](#-rodando-os-testes)
- [Testando a API no Postman](#-testando-a-api-no-postman)
- [Parar e limpar containers](#-parar-e-limpar-containers)
- [Principais decisões de design](#-principais-decisoes-de-design)
- [Resultados do case](#-resultados-do-case)

---

## 🧩 Tecnologias utilizadas
- Python 3.12
- Django 5
- PostgreSQL 16
- Redis 7
- Celery 5
- Docker & Docker Compose
- Pytest para testes automatizados

---

## 🚀 Funcionalidades e resultados do case

- **Gestão de usuários**: cadastro, autenticação JWT e permissões diferenciadas por perfil (Admin, Instrutor e Aluno).
- **Gestão de cursos e aulas**: criação, atualização, exclusão e listagem de cursos e aulas, com controle de acesso granular.
- **Inscrição de alunos**: Admin pode inscrever qualquer aluno; alunos podem se auto-inscrever em cursos ativos.
- **Progresso do aluno**: acompanhamento do progresso em cada curso, com marcação de aulas concluídas.
- **Geração de certificados**: certificados automáticos gerados ao concluir todas as aulas de um curso, processados de forma assíncrona via Celery.
- **Integração com APIs de IA**: permite geração de conteúdos dinâmicos e textos para certificados.
- **Testes automatizados**: cobertura de funcionalidades críticas garantindo confiabilidade do sistema.

**Resultados alcançados:**
- Ambiente totalmente containerizado, pronto para desenvolvimento e testes.
- Estrutura modular e escalável, facilitando manutenção e futuras integrações.
- Controle de permissões robusto, assegurando segurança e integridade dos dados.

---

## 🚀 Executando o projeto

1. **Pré-requisitos**
   - Docker: https://docs.docker.com/get-docker/
   - Docker Compose: https://docs.docker.com/compose/
   - Verifique a instalação:
    ```bash
    docker --version
    docker-compose --version
    ```

2. **Clonar o repositório**
    ```bash
    git clone https://github.com/thaynararm/desafio-alu-connect.git
    cd desafio-alu-connect
    ```

3. **Criar o arquivo `.env`**
    ```env
    # Banco de dados PostgreSQL
    DATABASE_NAME=mydatabase
    DATABASE_USER=postgres
    DATABASE_PASSWORD=postgres
    DATABASE_HOST=db       
    DATABASE_PORT=5432
    
    # Redis
    REDIS_HOST=redis       
    REDIS_PORT=6379
    
    # Django Secret Key
    SECRET_KEY=sua_secret_key
    DEBUG=True
    
    # Django Allowed Hosts
    ALLOWED_HOSTS=localhost,127.0.0.1
    
    # Celery
    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0

    # API de IA
    GEMINI_API_KEY=sua_chave_gemini
    ```

4. **Subir os containers**
    ```bash
    docker-compose up --build
    # ou para rodar em segundo plano
    docker-compose up -d --build
    ```

---

## 🧪 Rodando os testes

1. Acessar o container Django:
    ```bash
    docker-compose exec web bash
    ```
2. Rodar todos os testes:
    ```bash
    pytest -v
    ```
3. Cobertura de testes:
    ```bash
    pytest --cov=.
    ```
4. Testes de arquivo específico:
    ```bash
    pytest user/tests/test_user.py
    ```

---

## 🧪 Testando a API no Postman

1. Baixe o arquivo da collection em [`/postman/aluconnect_api_collection.json`](./postman/aluconnect_api_collection.json).
2. No Postman, clique em **Import > File** e selecione o arquivo.
3. Configure as variáveis de ambiente (ex: `BASE_URL`, `TOKEN`, etc.) se necessário.
4. Execute os requests para testar os endpoints.

## 🧼 Parar e limpar containers
```bash
docker-compose down
docker-compose down -v  # para remover volumes
```

---

## 🏗️ Principais decisões de design

### Arquitetura e organização
- **Django + Django REST Framework**: robustez em APIs REST, fácil serialização e suporte a autenticação/permssões.
- **ViewSets e Routers**: endpoints organizados de forma consistente e escalável.
- **Lookup por UUID**: evita exposição de IDs sequenciais e aumenta segurança.

### Autenticação e segurança
- **JWT (JSON Web Token)**: autenticação stateless, permitindo escalabilidade horizontal.
- **CustomTokenObtainPairView**: atualiza `last_login` ao autenticar.
- **Permissões customizadas**: controle granular por perfil (Admin, Instrutor, Aluno) e por ação (create, update, retrieve, etc.).

### Modelagem e relacionamentos
- **Aluno–Curso–Progresso**: estrutura clara para inscrições e acompanhamento do progresso.
- **Aulas com ordem única por curso**: garante consistência na sequência de aprendizagem.
- **Relacionamentos ManyToMany**: flexibilidade para múltiplos instrutores e alunos em cursos.

### Funcionalidades adicionais
- **Marcação de progresso e geração de certificados**: processadas de forma assíncrona via Celery.
- **Inscrição dinâmica de alunos**: Admin pode inscrever qualquer aluno; alunos podem se auto-inscrever em cursos ativos.

### Tratamento de erros
- Retornos claros e específicos para ações inválidas.
- Proteção de endpoints para usuários não autenticados, garantindo que dados sensíveis não sejam expostos.

### Escalabilidade
- **Celery + Redis**: desacopla tarefas assíncronas do fluxo principal.
- **Design modular**: separação por apps (`user`, `student`, `instructor`, `course`) facilita manutenção, testes e futuras evoluções.

---

## 📈 Resultados do case
- Sistema funcional de gestão de cursos e alunos, com controle de progresso.
- Certificados gerados automaticamente ao concluir cursos.
- Testes automatizados cobrindo funcionalidades críticas.
- Arquitetura modular e segura, pronta para crescimento e novas integrações.

---

