# Desafio de Backend: API customer-loans

Esta API foi desenvolvida como parte de um **Desafio Técnico de Backend**, com o objetivo de demonstrar competências em engenharia de software, arquitetura de sistemas e implementação de regras de negócio complexas utilizando as melhores práticas do ecossistema Python moderno.

A solução recebe o perfil financeiro de um cliente e determina dinamicamente as modalidades de empréstimo (Pessoal, Com Garantia e Consignado) às quais ele tem acesso, aplicando taxas de juros específicas para cada perfil.

## 🚀 Tech Stack

- **Python 3.14**: Utilizando as funcionalidades mais recentes da linguagem.
- **FastAPI**: Framework web de alta performance e assíncrono.
- **Pydantic v2**: Garantia de tipagem e validação rigorosa de dados (I/O).
- **uv**: Gerenciador de pacotes e ambientes Python ultra-rápido da Astral.
- **SQLite**: Persistência leve para auditoria e logs de requisições.
- **pytest + httpx**: Suite de testes para validação unitária e de integração.
- **ruff**: Ferramenta completa de Linting e Formatação de código.

## 🏗️ Arquitetura do Projeto

A aplicação segue o padrão **MVC (Model-View-Controller)**, priorizando a separação de interesses e a testabilidade:

- **Controller (`app/controllers`)**: Gerencia o protocolo HTTP, traduz requisições para chamadas de serviço e formata as respostas.
- **Service (`app/services`)**: Camada central onde residem as **Regras de Negócio**. É agnóstica a transporte (HTTP) e persistência.
- **Model (`app/models`)**: Define os contratos de dados (Schemas) e a interface de persistência (SQLite).
- **Core (`app/core`)**: Centraliza enums globais, constantes e o motor de tratamento de erros customizado.

## 🧠 Princípios de Engenharia

Para este desafio, foram aplicados rigorosamente os seguintes princípios:
- **TDD (Test-Driven Development)**: Código escrito sob a metodologia Red-Green-Refactor.
- **Clean Code**: Código semântico, legível e autoexplicativo.
- **SOLID**: Aplicação prática dos princípios de design de software robusto.
- **DRY (Don't Repeat Yourself)** & **KISS (Keep It Simple, Stupid)**.
- **YAGNI**: Implementação focada estritamente nos requisitos do desafio, evitando over-engineering.

## 📋 Regras de Negócio e Elegibilidade

A inteligência da API avalia as modalidades de crédito com base em condicionais lógicas:

| Modalidade | Taxa | Critérios de Aprovação |
| :--- | :--- | :--- |
| **PERSONAL** | 4% | Modalidade base avaliada para todos os perfis. |
| **GUARANTEED** | 3% | Elegível se: (Renda entre 3k e 5k) OU (Idade < 30 e reside em SP). |
| **CONSIGNMENT** | 2% | Elegível se: (Renda > 5k) OU (Renda entre 3k e 5k) OU (Idade < 30 e reside em SP). |

> **Observação Crucial:** Se a renda do cliente exceder R$ 5.000,00, as regras restringem o acesso **exclusivamente** à modalidade de Empréstimo Consignado.

## 🛣️ API Docs e Endpoints

### `POST /customer-loans`

Calcula e retorna as opções de empréstimo disponíveis.

**Request Exemplo:**
```json
{
  "age": 28,
  "cpf": "123.456.789-09",
  "name": "João da Silva",
  "income": 4500.00,
  "location": "SP"
}
```

**Response Exemplo (200 OK):**
```json
{
  "customer": "João da Silva",
  "loans": [
    { "type": "CONSIGNMENT", "interest_rate": 2 },
    { "type": "GUARANTEED",  "interest_rate": 3 }
  ]
}
```

## ⚠️ Tratamento de Erros Padronizado

A API responde com um schema de erro único e descritivo para qualquer falha (validação, lógica ou sistema):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Um ou mais campos enviados são inválidos.",
    "details": [
      { "field": "age", "message": "Idade mínima permitida é 18 anos." }
    ]
  }
}
```

## 🚦 Como Rodar o Projeto

### Pré-requisitos
- Ter o gerenciador [uv](https://github.com/astral-sh/uv) instalado.

### Passo a Passo
```bash
# 1. Instalar dependências e configurar venv
uv sync

# 2. Rodar a suite de testes (TDD)
uv run pytest

# 3. Validar qualidade de código (Linter/Formatter)
uv run ruff check

# 4. Subir o servidor (Hot Reload ativo)
uv run uvicorn app.main:app --reload

```
---
