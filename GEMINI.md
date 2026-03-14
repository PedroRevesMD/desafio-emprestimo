# Especificação Técnica — API `customer-loans`

> **Versão:** 1.0  
> **Stack:** Python 3.14 · FastAPI · Pydantic · SQLite · uv  
> **Arquitetura:** MVC  
> **Práticas:** TDD · Clean Code · DRY · KISS · YAGNI · SOLID

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Stack e Ferramentas](#2-stack-e-ferramentas)
3. [Arquitetura do Projeto](#3-arquitetura-do-projeto)
4. [Contrato de Dados](#4-contrato-de-dados)
5. [Regras de Negócio](#5-regras-de-negócio)
6. [Validações de Entrada](#6-validações-de-entrada)
7. [Error Handling](#7-error-handling)
8. [Boas Práticas de Código](#8-boas-práticas-de-código)
9. [Estratégia de Testes (TDD)](#9-estratégia-de-testes-tdd)
10. [Casos de Teste](#10-casos-de-teste)

---

## 1. Visão Geral

A API recebe o perfil financeiro de um cliente e retorna, dinamicamente, as modalidades de empréstimo às quais ele tem acesso, com suas respectivas taxas de juros.

### 1.1 Endpoint

```
POST /customer-loans
```

| Atributo        | Valor                          |
|-----------------|--------------------------------|
| Método          | `POST`                         |
| Path            | `/customer-loans`              |
| Content-Type    | `application/json`             |
| Accept          | `application/json`             |

---

## 2. Stack e Ferramentas

| Ferramenta      | Papel                                          | Versão mínima |
|-----------------|------------------------------------------------|---------------|
| Python          | Runtime                                        | 3.14          |
| uv              | Gerenciador de pacotes e ambientes virtuais    | latest        |
| FastAPI         | Framework web assíncrono                       | 0.115+        |
| Pydantic v2     | Validação e serialização de dados (I/O)        | 2.x           |
| SQLite          | Persistência leve (log de requests/responses)  | built-in      |
| pytest          | Runner de testes                               | 8.x           |
| httpx           | Cliente HTTP para testes de integração         | 0.27+         |
| ruff            | Linter e formatter                             | latest        |

### 2.1 Setup Inicial com uv

```bash
cd backend-emprestimo 

uv add fastapi pydantic uvicorn
uv add --dev pytest httpx ruff pytest-asyncio
```

---

## 3. Arquitetura do Projeto

A API segue o padrão **MVC adaptado para APIs REST**, onde:

- **Model** — define os schemas de dados e a camada de acesso ao banco (SQLite).
- **Controller** — orquestra o fluxo: recebe o request, delega para o Service, retorna o response. Não contém lógica de negócio.
- **Service** — contém toda a lógica de negócio (regras de elegibilidade). Não conhece HTTP.

```
backend-emprestimo/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # Instância do FastAPI, registro de routers e handlers
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── loan_controller.py   # Rotas HTTP — recebe requests, retorna responses
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── loan_service.py      # Regras de negócio — elegibilidade de empréstimos
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py           # Pydantic: CustomerInput, LoanResponse, ErrorResponse
│   │   └── database.py          # Conexão SQLite e operações de log
│   │
│   └── core/
│       ├── __init__.py
│       ├── enums.py             # LoanTypeEnum e outros enums
│       └── exceptions.py        # Exceções customizadas do domínio
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_loan_service.py     # Testes unitários das regras de negócio
│   │   └── test_schemas.py          # Testes de validação Pydantic
│   └── integration/
│       └── test_loan_controller.py  # Testes de integração (endpoint completo)
│
├── pyproject.toml
└── README.md
```

### 3.1 Responsabilidades por Camada

```
HTTP Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Controller  (loan_controller.py)                   │
│  • Recebe e tipifica o request via Pydantic         │
│  • Chama o Service                                  │
│  • Formata e retorna o response                     │
│  • NÃO contém lógica de negócio                     │
└─────────────────────┬───────────────────────────────┘
                      │ chama
                      ▼
┌─────────────────────────────────────────────────────┐
│  Service  (loan_service.py)                         │
│  • Aplica as regras de elegibilidade                │
│  • Retorna a lista de empréstimos elegíveis         │
│  • NÃO conhece HTTP, request ou response            │
│  • NÃO acessa banco diretamente                     │
└─────────────────────┬───────────────────────────────┘
                      │ persiste log
                      ▼
┌─────────────────────────────────────────────────────┐
│  Model  (database.py + schemas.py)                  │
│  • Schemas Pydantic para I/O                        │
│  • Acesso ao SQLite (log de requisições)            │
└─────────────────────────────────────────────────────┘
```

---

## 4. Contrato de Dados

### 4.1 Request Body

```json
{
  "age": 28,
  "cpf": "123.456.789-09",
  "name": "João da Silva",
  "income": 4500.00,
  "location": "SP"
}
```

| Campo      | Tipo      | Obrigatório | Descrição                              |
|------------|-----------|-------------|----------------------------------------|
| `age`      | `integer` | ✅           | Idade do cliente em anos completos     |
| `cpf`      | `string`  | ✅           | CPF no formato `xxx.xxx.xxx-xx`        |
| `name`     | `string`  | ✅           | Nome completo do cliente               |
| `income`   | `float`   | ✅           | Renda mensal bruta em R$               |
| `location` | `string`  | ✅           | UF brasileira — 2 letras maiúsculas    |

### 4.2 Response — Sucesso

**HTTP 200 OK**

```json
{
  "customer": "João da Silva",
  "loans": [
    { "type": "PERSONAL",    "interest_rate": 4 },
    { "type": "GUARANTEED",  "interest_rate": 3 },
    { "type": "CONSIGNMENT", "interest_rate": 2 }
  ]
}
```

| Campo      | Tipo            | Descrição                                        |
|------------|-----------------|--------------------------------------------------|
| `customer` | `string`        | Nome do cliente conforme enviado                 |
| `loans`    | `array[LoanType]` | Lista de modalidades elegíveis (pode ser vazia) |

#### LoanType

| Campo           | Tipo      | Descrição                            |
|-----------------|-----------|--------------------------------------|
| `type`          | `string`  | Enum: `PERSONAL`, `GUARANTEED`, `CONSIGNMENT` |
| `interest_rate` | `integer` | Taxa de juros em % ao mês            |

#### LoanTypeEnum

| Enum           | `interest_rate` | Modalidade               |
|----------------|-----------------|--------------------------|
| `PERSONAL`     | `4`             | Empréstimo Pessoal       |
| `GUARANTEED`   | `3`             | Empréstimo com Garantia  |
| `CONSIGNMENT`  | `2`             | Empréstimo Consignado    |

### 4.3 Response — Nenhuma Modalidade Elegível

**HTTP 200 OK** — processamento bem-sucedido, porém sem modalidades disponíveis:

```json
{
  "customer": "João da Silva",
  "loans": []
}
```

---

## 5. Regras de Negócio

As regras são avaliadas de forma independente e não excludente. As condicionais estão organizadas em dois blocos lógicos principais.

### 5.1 Regra 1 — Renda Alta (income > 5.000)

> **Concessão restrita:** o cliente tem acesso **apenas** à modalidade de empréstimo consignado.

```
SE income > 5000:
    RETORNAR [CONSIGNMENT]
```

| Modalidade    | Taxa |
|---------------|------|
| `CONSIGNMENT` | 2%   |

---

### 5.2 Regra 2 — Acesso Limitado

> O cliente recebe `CONSIGNMENT` e `GUARANTEED` **se** satisfizer ao menos **uma** das condições abaixo:

```
SE (3000 <= income <= 5000)
   OU (age < 30 E location == "SP"):
    RETORNAR [CONSIGNMENT, GUARANTEED]

SENÃO:
    RETORNAR []
```

**Condições da Regra 2:**

| Condição A                                | Condição B                              |
|-------------------------------------------|-----------------------------------------|
| `3000 <= income <= 5000`                  | `age < 30` **E** `location == "SP"` |
| Satisfeita → concede CONSIGNMENT + GUARANTEED | Satisfeita → concede CONSIGNMENT + GUARANTEED |

> **Nota:** as Condições A e B são ligadas por **OU lógico** — basta uma ser verdadeira.

---

### 5.3 Diagrama de Decisão

```
income > 5000?
  ├─ SIM → [CONSIGNMENT]
  └─ NÃO →
        (3000 <= income <= 5000)
        OU (age < 30 AND location == "SP")?
          ├─ SIM → [CONSIGNMENT, GUARANTEED]
          └─ NÃO → []
```

---

### 5.4 Tabela de Exemplos

| `income`  | `age` | `location` | Resultado                       |
|-----------|-------|------------|---------------------------------|
| 8.000     | 40    | RJ         | CONSIGNMENT                     |
| 5.001     | 18    | SP         | CONSIGNMENT                     |
| 5.000     | 40    | MG         | CONSIGNMENT, GUARANTEED         |
| 3.000     | 40    | MG         | CONSIGNMENT, GUARANTEED         |
| 4.000     | 25    | SP         | CONSIGNMENT, GUARANTEED         |
| 4.000     | 35    | MG         | CONSIGNMENT, GUARANTEED (pela Cond. A) |
| 2.000     | 25    | SP         | [] (income < 3000, age < 30 mas não entra na Regra 1 nem 2) |
| 2.500     | 40    | RJ         | []                              |

> **Atenção:** `income <= 2.999,99` não satisfaz a Condição A (exige `>= 3000`). A Condição B (`age < 30 AND location == "SP"`) também não cobre income baixo — portanto, renda abaixo de 3.000 só resulta em `[]`.

---

## 6. Validações de Entrada

> A validação é feita exclusivamente via **Pydantic v2**. O objetivo é garantir que os dados estejam no formato correto — não há verificação de autenticidade (ex.: dígitos verificadores do CPF).

### 6.1 `age` — integer

| Regra              | Detalhe                                    |
|--------------------|--------------------------------------------|
| Tipo               | Inteiro (`int`) — rejeitar `float`, `str`  |
| Valor mínimo       | `18`                                       |
| Valor máximo       | `120`                                      |

```python
age: Annotated[int, Field(ge=18, le=120)]
```

---

### 6.2 `cpf` — string

| Regra          | Detalhe                                              |
|----------------|------------------------------------------------------|
| Formato        | `XXX.XXX.XXX-XX` (pontuação obrigatória)            |
| Regex          | `^\d{3}\.\d{3}\.\d{3}-\d{2}$`                      |
| Escopo         | Apenas validação de formato — sem verificação de dígitos |

```python
cpf: Annotated[str, Field(pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')]
```

---

### 6.3 `name` — string

| Regra              | Detalhe                                        |
|--------------------|------------------------------------------------|
| Não vazio          | `min_length=2`                                 |
| Comprimento máximo | `max_length=200`                               |
| Trim automático    | `strip_whitespace=True` (via `Field`)          |

```python
name: Annotated[str, Field(min_length=2, max_length=200, strip_whitespace=True)]
```

---

### 6.4 `income` — float

| Regra          | Detalhe                          |
|----------------|----------------------------------|
| Tipo           | `float` (ou `int` coercível)     |
| Valor mínimo   | `> 0` (`gt=0`)                   |

```python
income: Annotated[float, Field(gt=0)]
```

---

### 6.5 `location` — string

| Regra               | Detalhe                                          |
|---------------------|--------------------------------------------------|
| Comprimento exato   | 2 caracteres                                     |
| Case                | Maiúsculas (`str.upper()` no validator)          |
| Valores válidos     | UFs brasileiras (lista definida em `enums.py`)   |

**UFs válidas:**
```
AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI
RJ RN RS RO RR SC SP SE TO
```

```python
location: Annotated[str, Field(min_length=2, max_length=2)]

@field_validator('location')
@classmethod
def validate_location(cls, v: str) -> str:
    upper = v.upper()
    if upper not in VALID_UFS:
        raise ValueError(f"'{v}' não é uma UF brasileira válida.")
    return upper
```

---

## 7. Error Handling

### 7.1 Filosofia

- Erros são **previsíveis** (validação, negócio) ou **imprevisíveis** (erros internos).
- Toda resposta de erro segue um **schema único e consistente**.
- Nunca expor stack traces ou informações internas ao cliente.
- Logar detalhes internamente; retornar mensagens legíveis ao usuário.

---

### 7.2 Schema Padrão de Erro

Todos os erros retornam o mesmo envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Um ou mais campos enviados são inválidos.",
    "details": [
      {
        "field": "cpf",
        "message": "CPF deve seguir o formato xxx.xxx.xxx-xx."
      }
    ]
  }
}
```

| Campo              | Tipo            | Descrição                                                          |
|--------------------|-----------------|--------------------------------------------------------------------|
| `error.code`       | `string`        | Código de erro legível por máquina (ex.: `VALIDATION_ERROR`)      |
| `error.message`    | `string`        | Mensagem genérica e legível por humanos                            |
| `error.details`    | `array` ou `null` | Lista de erros individuais (campo + mensagem), quando aplicável  |

---

### 7.3 Catálogo de Erros

#### `400 Bad Request` — Payload Malformado

Disparado quando o corpo da requisição não é um JSON válido.

```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "O corpo da requisição é inválido ou não é um JSON bem-formado.",
    "details": null
  }
}
```

---

#### `422 Unprocessable Entity` — Erro de Validação

Disparado quando o JSON é válido, mas os dados não passam pelas regras do Pydantic.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Um ou mais campos enviados são inválidos.",
    "details": [
      { "field": "age",      "message": "Idade mínima permitida é 18 anos." },
      { "field": "location", "message": "'xx' não é uma UF brasileira válida." }
    ]
  }
}
```

> **Nota:** O FastAPI dispara automaticamente `RequestValidationError` ao falhar na validação do Pydantic. O handler customizado intercepta esse erro e o reformata para o schema padrão acima.

---

#### `404 Not Found` — Rota Não Encontrada

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "A rota solicitada não existe.",
    "details": null
  }
}
```

---

#### `405 Method Not Allowed` — Método HTTP Inválido

```json
{
  "error": {
    "code": "METHOD_NOT_ALLOWED",
    "message": "O método HTTP utilizado não é permitido para esta rota.",
    "details": null
  }
}
```

---

#### `500 Internal Server Error` — Erro Interno

Disparado para qualquer exceção não tratada. O detalhe do erro é **logado internamente** e **nunca exposto** ao cliente.

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.",
    "details": null
  }
}
```

---

### 7.4 Registro dos Handlers no FastAPI

Cada tipo de erro possui seu próprio handler registrado em `main.py`, respeitando o princípio da **responsabilidade única**:

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.core.exceptions import handle_validation_error
from app.core.exceptions import handle_http_exception
from app.core.exceptions import handle_internal_error

app = FastAPI()

app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(HTTPException,          handle_http_exception)
app.add_exception_handler(Exception,              handle_internal_error)
```

---

### 7.5 Tabela de Status Codes

| Situação                          | Status Code | `error.code`             |
|-----------------------------------|-------------|--------------------------|
| Sucesso                           | `200`       | —                        |
| JSON malformado                   | `400`       | `BAD_REQUEST`            |
| Falha de validação (Pydantic)     | `422`       | `VALIDATION_ERROR`       |
| Rota não encontrada               | `404`       | `NOT_FOUND`              |
| Método HTTP inválido              | `405`       | `METHOD_NOT_ALLOWED`     |
| Erro interno não tratado          | `500`       | `INTERNAL_SERVER_ERROR`  |

---

## 8. Boas Práticas de Código

### 8.1 Clean Code

- Nomes de funções, variáveis e classes devem ser **autoexplicativos** — evitar abreviações (ex.: `get_eligible_loans`, não `get_loans` ou `calc`).
- Funções devem fazer **uma coisa só** e ter no máximo ~20 linhas.
- Comentários explicam o **"por quê"**, não o "o quê" — o código deve ser legível o suficiente para dispensar comentários óbvios.

### 8.2 DRY (Don't Repeat Yourself)

- As regras de elegibilidade ficam **exclusivamente** em `loan_service.py`.
- O schema de erro é definido uma única vez em `schemas.py` e reutilizado por todos os handlers.
- Constantes (UFs válidas, taxas de juros) são definidas uma vez em `enums.py`.

### 8.3 KISS (Keep It Simple, Stupid)

- A API tem um único endpoint — não criar abstrações desnecessárias para isso.
- SQLite é suficiente para o escopo; não adicionar complexidade de ORMs completos (SQLAlchemy) sem necessidade.
- Sem camadas de cache, filas ou middlewares não exigidos pelo requisito.

### 8.4 YAGNI (You Aren't Gonna Need It)

- Não implementar autenticação, paginação, versionamento de API ou multi-tenancy — nada foi solicitado.
- Não criar abstração de repositório se a única operação de banco é log de requisição.

### 8.5 SOLID

| Princípio | Aplicação                                                                   |
|-----------|-----------------------------------------------------------------------------|
| **S** — Single Responsibility | Cada arquivo/classe tem um único motivo para mudar: Controller cuida de HTTP, Service cuida de negócio, Model cuida de dados. |
| **O** — Open/Closed | Novas regras de elegibilidade são adicionadas ao Service sem modificar o Controller. |
| **L** — Liskov Substitution | Não aplicável diretamente (sem herança complexa na arquitetura MVC). |
| **I** — Interface Segregation | O Service recebe apenas os dados que precisa — sem depender do objeto Request completo. |
| **D** — Dependency Inversion | O Controller depende da abstração do Service (função pura), não de uma implementação concreta acoplada. |

### 8.6 Design Patterns Aplicados

| Pattern               | Onde                   | Motivo                                                        |
|-----------------------|------------------------|---------------------------------------------------------------|
| **Strategy** (implícito) | `loan_service.py`  | Cada regra de elegibilidade é uma função independente; facilita adicionar novas regras. |
| **Factory** (parcial)  | `schemas.py`           | `LoanResponse` é construído a partir de uma lista de enums, desacoplando criação de uso. |
| **Handler Chain**      | `core/exceptions.py`   | Cada tipo de exceção tem seu próprio handler registrado, evitando `if/elif` gigante. |

---

## 9. Estratégia de Testes (TDD)

### 9.1 Fluxo Red → Green → Refactor

```
1. RED    — Escrever o teste que descreve o comportamento esperado (falha).
2. GREEN  — Escrever o mínimo de código para o teste passar.
3. REFACTOR — Melhorar o código sem quebrar os testes.
```

### 9.2 Tipos de Teste

| Tipo          | Local                               | Foco                                             |
|---------------|-------------------------------------|--------------------------------------------------|
| **Unitário**  | `tests/unit/test_loan_service.py`   | Regras de negócio isoladas, sem I/O              |
| **Unitário**  | `tests/unit/test_schemas.py`        | Validações Pydantic campo a campo                |
| **Integração**| `tests/integration/test_loan_controller.py` | Fluxo completo: HTTP → Controller → Service → Response |

### 9.3 Nomenclatura de Testes

```
test_<unidade>_<cenario>_<resultado_esperado>

Exemplos:
  test_get_eligible_loans_income_above_5000_returns_all_loans
  test_get_eligible_loans_income_between_3000_and_5000_returns_limited_loans
  test_customer_input_invalid_cpf_format_raises_validation_error
  test_post_customer_loans_missing_field_returns_422
```

### 9.4 Cobertura Mínima Esperada

| Camada         | Cobertura mínima |
|----------------|-----------------|
| `loan_service` | 100%            |
| `schemas`      | 90%             |
| `controller`   | 80%             |
| `exceptions`   | 80%             |

---

## 10. Casos de Teste

### 10.1 Regras de Negócio — `test_loan_service.py`

| ID      | `income`  | `age` | `location` | Resultado Esperado                        |
|---------|-----------|-------|------------|-------------------------------------------|
| TC-N-01 | 5.001     | 40    | RJ         | [CONSIGNMENT]                             |
| TC-N-02 | 10.000    | 18    | AM         | [CONSIGNMENT]                             |
| TC-N-03 | 5.000     | 40    | MG         | [CONSIGNMENT, GUARANTEED]                 |
| TC-N-04 | 3.000     | 40    | MG         | [CONSIGNMENT, GUARANTEED]                 |
| TC-N-05 | 4.000     | 29    | SP         | [CONSIGNMENT, GUARANTEED]                 |
| TC-N-06 | 4.000     | 35    | RJ         | [CONSIGNMENT, GUARANTEED] (pela Cond. A)  |
| TC-N-07 | 2.999     | 29    | SP         | [] (income < 3000, Cond. B não cobre)    |
| TC-N-08 | 2.999     | 40    | RJ         | []                                        |
| TC-N-09 | 4.000     | 30    | SP         | [CONSIGNMENT, GUARANTEED] (Cond. A)       |
| TC-N-10 | 2.000     | 25    | SP         | []                                        |

---

### 10.2 Validação de Campos — `test_schemas.py`

#### `cpf`

| ID      | Valor enviado       | Resultado    | Motivo                        |
|---------|---------------------|--------------|-------------------------------|
| TC-V-01 | `"123.456.789-09"`  | ✅ Válido     | Formato correto               |
| TC-V-02 | `"000.000.000-00"`  | ✅ Válido     | Formato correto (sem verificação de dígitos) |
| TC-V-03 | `"12345678909"`     | ❌ Inválido   | Sem pontuação                 |
| TC-V-04 | `"123.456.789-0"`   | ❌ Inválido   | Último bloco com 1 dígito     |
| TC-V-05 | `"abc.def.ghi-jk"`  | ❌ Inválido   | Não numérico                  |
| TC-V-06 | `""`                | ❌ Inválido   | Vazio                         |

#### `age`

| ID      | Valor   | Resultado  | Motivo              |
|---------|---------|------------|---------------------|
| TC-V-07 | `18`    | ✅ Válido   | Mínimo permitido    |
| TC-V-08 | `120`   | ✅ Válido   | Máximo permitido    |
| TC-V-09 | `17`    | ❌ Inválido | Abaixo do mínimo    |
| TC-V-10 | `121`   | ❌ Inválido | Acima do máximo     |
| TC-V-11 | `"28"`  | ❌ Inválido | Tipo errado (string)|

#### `location`

| ID      | Valor         | Resultado  | Motivo                       |
|---------|---------------|------------|------------------------------|
| TC-V-12 | `"SP"`        | ✅ Válido   | UF válida em maiúsculas      |
| TC-V-13 | `"sp"`        | ❌ Inválido | Letras minúsculas            |
| TC-V-14 | `"São Paulo"` | ❌ Inválido | Mais de 2 caracteres         |
| TC-V-15 | `"XX"`        | ❌ Inválido | UF inexistente               |
| TC-V-16 | `""`          | ❌ Inválido | Vazio                        |

#### `income`

| ID      | Valor    | Resultado  | Motivo               |
|---------|----------|------------|----------------------|
| TC-V-17 | `100.0`  | ✅ Válido   | Positivo             |
| TC-V-18 | `0`      | ❌ Inválido | Deve ser maior que 0 |
| TC-V-19 | `-500`   | ❌ Inválido | Negativo             |
| TC-V-20 | `"abc"`  | ❌ Inválido | Tipo errado          |

---

### 10.3 Error Handling — `test_loan_controller.py`

| ID      | Cenário                              | HTTP | `error.code`             |
|---------|--------------------------------------|------|--------------------------|
| TC-E-01 | Payload JSON malformado              | 400  | `BAD_REQUEST`            |
| TC-E-02 | Campo `cpf` com formato inválido     | 422  | `VALIDATION_ERROR`       |
| TC-E-03 | Campo `age` ausente                  | 422  | `VALIDATION_ERROR`       |
| TC-E-04 | Múltiplos campos inválidos           | 422  | `VALIDATION_ERROR`       |
| TC-E-05 | `GET /customer-loans`                | 405  | `METHOD_NOT_ALLOWED`     |
| TC-E-06 | `POST /rota-inexistente`             | 404  | `NOT_FOUND`              |

---

## Apêndice — Exemplo de Fluxo Completo

**Request:**
```bash
curl -X POST http://localhost:8000/customer-loans \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "cpf": "123.456.789-09",
    "name": "Maria Souza",
    "income": 4000.00,
    "location": "SP"
  }'
```

**Response (200 OK):**
```json
{
  "customer": "Maria Souza",
  "loans": [
    { "type": "CONSIGNMENT", "interest_rate": 2 },
    { "type": "GUARANTEED",  "interest_rate": 3 }
  ]
}
```

> Maria se enquadra na **Condição A** (income entre 3k e 5k) E na **Condição B** (age < 30 e location == SP). Como ambas levam ao mesmo resultado, o output é idêntico: [CONSIGNMENT, GUARANTEED].
