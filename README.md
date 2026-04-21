# Pipefy-Manager-Api
A simple management REST api with integration to Pipefy, as a IT challenge. Should include midway integration with Pipefy, which uses GraphQL api for management.

## Should be capable of:
1. Create cards in Pipefy with specific fields.
2. Delete cards by ID.
3. Move cards trough different phases in the Pipe.


## Installation
1. Clone the repository:
```bash
git clone https://github.com/limatila/pipefy-manager-api.git
```

```
1. Install the dependencies using pip:
```bash
pip install -r requirements.txt
```


- Optionally, use venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

- Or better, with Astral UV (https://docs.astral.sh/uv/):
```bash
uv sync
```



1. configure a .env file to set the PIPEFY_TOKEN and PIPE_ID variables, as shown in example:
```env
# Pipefy Identification
PIPEFY_TOKEN=SECRET_TOKEN
PIPE_ID=123456789


4. Run in module mode
```bash
python -m src.main
```

This way, all dependencies will be installed, and a first demo token for usage is generated and displayed in console.


# Architecture and Implementation Guidelines

## Technologys
- Python
- FastAPI, Pydantic
- Uvicorn
- SQLModel (SQLite)
- Dotenv
- Pytest

Additionally, developed with Astral UV, which manages the installation flow automatically.


## Code Workflow
Endpoints -> Router (DTO validation) -> Service (orchestrates flow) -> Mapper (DTO <-> Pipefy payload) -> Builder (dynamic GraphQL) -> Client (HTTP call)

- Endpoints: create card, delete card, move card phase (with final-phase response).
- Router: validates request DTOs, calls service, returns response DTOs.
- Service: orchestrates mapping, GraphQL execution, response interpretation, and local persistence during runtime.
- Mapper: translates internal DTOs to provider payload and provider data to internal response DTOs.
- Builder: builds GraphQL query/mutation strings dynamically based on input.
- Client: executes HTTP calls to Pipefy GraphQL endpoint with Bearer auth from the PIPEFY_TOKEN variable.


## Architectural Reasoning
- Separation of concerns: each layer has a single responsibility, making the codebase easier to maintain and extend.
- Scalability: the architecture allows for easy addition of new endpoints and operations without affecting existing code.
- Testability: with clear boundaries, each component can be tested in isolation, ensuring reliability and ease of debugging.
- Simplicity: the architecture is designed to be straightforward and easy to understand, avoiding unnecessary complexity while still providing a solid foundation for future growth.
- Security: by using DTOs and mappers, we can control the data flow and ensure that sensitive information (like Pipefy field IDs) is not exposed in public contracts.
- Flexibility: a dynamic builder allows for easy adjustments to GraphQL operations as requirements evolve, without needing to rewrite large portions of code.