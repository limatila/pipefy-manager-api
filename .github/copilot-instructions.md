# 🧠 Copilot Instructions — Pipefy Integration API

## Objetivo

- Implementar endpoints para criar card (campos Pessoa), deletar card por ID, mover card de fase (com sinalização de fase final).
- Garantir arquitetura escalável, simples e clara para expansão futura.

## Práticas Obrigatórias

### 1. Contratos DTO
- Sempre use Pydantic para request/response DTOs públicos.
- Nunca exponha IDs ou campos internos do Pipefy nos DTOs públicos.

### 2. Separação de Camadas
- Router: valida DTO, chama service, retorna DTO.
- Service: orquestra fluxo, chama mapper, builder, client, parser, persiste dados locais.
- Mapper: converte DTO interno <-> payload Pipefy.
- Builder: monta string GraphQL dinamicamente, sem duplicação.
- Client: executa requisição HTTP GraphQL.
- Parser: normaliza resposta para `{data, errors}`.

### 3. Persistência Local
- Service deve persistir dados relevantes de runtime (ex: cards criados, fases movidas, deleções) em banco local.
- Não misture lógica de persistência com mapeamento ou transporte.

### 4. Builder Dinâmico
- Use helpers para montar queries/mutations GraphQL de forma dinâmica e simples.
- Evite duplicação de strings; extraia padrões recorrentes.

### 5. Resposta Normalizada
- Sempre normalize resposta do Pipefy para `{data, errors}`.
- Endpoint de mover fase deve retornar flag de fase final (`is_final_phase: bool`).

## Exemplos

- Para criar um card:
	- Receba DTO com campos de Pessoa.
	- Mapeie para payload Pipefy via mapper.
	- Monte mutation com builder dinâmico.
	- Execute via client.
	- Normalize resposta e retorne DTO público.

- Para mover fase:
	- Receba DTO com card_id e destination_phase_id.
	- Após mover, compare fase atual com fase final (obtida via fetchPipePhases).
	- Retorne DTO com `is_final_phase`.

## Proibido
- Expor field_id, phase_id ou payloads brutos do Pipefy em endpoints públicos.
- Colocar lógica de mapeamento ou transporte no router.
- Duplicar queries/mutations GraphQL.
- Persistir dados fora do service.

## Checklist de Qualidade
- DTOs validados por Pydantic.
- Mapper centralizado e testável.
- Service sem vazamento de payloads externos.
- Builder dinâmico e reutilizável.
- Parser sempre retorna `{data, errors}`.
- Testes para DTO, mapper e sinalização de fase final.

## Referências
- Veja `.github/skills/api-payload-architecture/SKILL.md` e `.github/skills/graphql-abstraction/SKILL.md` para detalhes e exemplos.
