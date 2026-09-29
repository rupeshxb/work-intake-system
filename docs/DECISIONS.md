# Architecture Decisions

## 001 - PostgreSQL over SQLite
Used PostgreSQL via Docker instead of SQLite because the concurrent
duplicate test needs real concurrent writes. SQLite serialises writes,
which would hide the race condition we are deliberately testing.

## 002 - Layered folder structure
Separated domain/, ai/, services/, api/ inside work_items so that:
- domain/ has zero Django imports — pure Python, trivially testable
- services/ holds business logic, views stay thin
- ai/ is isolated so swapping providers is a single file change

## 003 - Stack choice
Django + DRF for backend
React + TypeScript + Redux Toolkit for frontend.
Gemini Flash for LLM (free tier, no credit card, same interface pattern
means swapping to another provider is one env variable change).

## 004 - Pure domain layer with no Django imports
The state machine lives in domain/workflow.py with zero Django imports.
This means transition logic can be tested without a database or environment
variables. Tests run in milliseconds anywhere. The domain layer is also
reusable from a Celery worker or CLI without pulling in the full Django stack.