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
