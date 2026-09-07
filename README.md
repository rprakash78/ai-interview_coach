# AI Interview Coach

A FastAPI learning project that asks Groq to generate structured interview
questions, with a second endpoint demonstrating tool calling.

## Run locally

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create a `.env` file containing `GROQ_API_KEY`. Then open
`http://localhost:8000/docs`, or use the Bruno collection in `api-client/`.

## Layout

```text
app/          API application code
api-client/   Bruno requests for manually testing endpoints
requirements.txt
```
# AI Interview Coach

A FastAPI learning project that asks Groq to generate structured interview
questions, with a second endpoint demonstrating tool calling.

## Requirements

- Python 3.12 or newer
- A Groq API key

## Run locally

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY` in `.env`, then start the API:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation at `http://localhost:8000/docs`.

## Endpoints

- `POST /interview/question` generates structured interview questions.
- `POST /interview/question-with-toools` demonstrates Groq tool calling.
- `GET /` checks that the API is running.

Example request:

```bash
curl -X POST http://localhost:8000/interview/question \
	-H 'Content-Type: application/json' \
	-d '{"topic":"Python","difficulty":"medium","limit":2}'
```

The Bruno collection for manual testing is in `api-client/`.

## Layout

```text
app/          API application code
api-client/   Bruno requests for manually testing endpoints
data/         Sample interview knowledge data
requirements.txt
```
