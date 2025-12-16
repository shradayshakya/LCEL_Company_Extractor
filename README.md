# LCEL Company Extractor

Extract company names, founding dates, and founders from essay paragraphs using LCEL runnables, and insert into PostgreSQL.

## Setup

1. Create `.env` from `.env.example` and set `DATABASE_URL`.
2. Install deps:

```zsh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run PostgreSQL via Docker Compose

```zsh
docker compose up -d
# DATABASE_URL should be: postgresql+psycopg2://postgres:postgres@localhost:5432/companies
```

## Run

Provide a file path to the CLI:

```zsh
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
python -m src.cli essay.txt
```

Or with an absolute path:

```zsh
python -m src.cli /Users/you/path/to/essay.txt
```

## Output Table

Table: `Company_details`
Columns: id, company_name, founded_in, founded_by(JSON list as string)

![Company_details table](image.png)
