---
name: api-authentication-flow
description: 'The main authentication flow for the API, including token management and secure access to endpoints, via tokens stored in DB data.'
argument-hint: 'What aspect of authentication are you implementing or refactoring? Token management, endpoint protection, or secure storage?'
---

# API Authentication Flow

## Outcome
- Implement a secure and efficient authentication flow for the API.
- Manage tokens effectively, including generation, storage, and validation.
- Ensure that API endpoints are protected and only accessible with valid tokens.
- Store tokens securely in the database, at the Person model/table following best practices for sensitive data.

## When to Use
- All endpoints must require authentication via tokens.
- Tokens should be generated upon user registration or login and stored securely.
- Implement token validation logic to protect API routes.
- Ensure that token management is efficient and does not introduce significant overhead.

## Main Goal
- Stablish a db storage of the tokens
- For demonstration purposes, create a simple token at API startup (if no Person exists in db), and print that token in terminal.
