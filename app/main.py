import os

from enum import Enum
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import Groq
from pydantic import BaseModel, Field
import json

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is not configured")

client = Groq(api_key=api_key)

app = FastAPI(
    title="AI Interview Coach",
    version="0.1.0",
)


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionRequest(BaseModel):
    topic: str
    difficulty: Difficulty = Field(default=Difficulty.EASY)
    limit: int = Field(default=1, ge=1, le=10)


class InterviewQuestion(BaseModel):
    topic: str
    difficulty: str
    question: str

class InterviewQuestionList(BaseModel):
    questions: list[InterviewQuestion]


@app.get("/")
def health_check():
    return {
        "message": "AI Interview Coach API is running"
    }

def get_topic_guidelines(topic: str) -> list[str]:
    guidelines = {
        "python": ["generators", "decorators", "asyncio"],
        "javascript": ["closures", "promises", "async/await"],
        "react": ["hooks", "context", "lifecycle methods"],
        "data structures": ["arrays", "linked lists", "trees", "graphs"],
        "algorithms": ["sorting", "searching", "dynamic programming", "greedy algorithms"],
        "system design": ["scalability", "caching", "load balancing", "distributed systems"],
        "web development": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
        "mobile development": ["Android", "iOS", "React Native", "Flutter"],
        "database": ["SQL", "NoSQL", "relational", "non-relational"],
        "devops": ["CI/CD", "containers", "kubernetes", "monitoring"],
        "kafka": ["producers", "consumers", "topics", "partitions", "offsets"],
    }
    return guidelines.get(topic.lower(), ["fundamental concepts", "best practices", "common pitfalls"])


def parse_question_list(content: str) -> InterviewQuestionList:
    parsed_content = json.loads(content)
    if isinstance(parsed_content, list):
        parsed_content = {"questions": parsed_content}
    return InterviewQuestionList.model_validate(parsed_content)


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_topic_guidelines",
            "description": "Get the guidelines for a given topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The topic to get the guidelines for"},
                },
                "required": ["topic"],
            },
        }
    }
]


@app.post("/interview/question")
def generate_question(request: QuestionRequest) -> InterviewQuestionList:
    try:
        schema = InterviewQuestionList.model_json_schema()
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            # tools=tools,
            # tool_choice="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software engineering interviewer. "
                        "Generate concise and technically meaningful questions. "
                        "Return exactly the requested number of questions."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate exactly {request.limit} interview questions "
                        f"about {request.topic} with difficulty {request.difficulty}."
                    ),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "InterviewQuestionList",
                    "schema": schema,
                }
            }
        )

        return parse_question_list(response.choices[0].message.content)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

@app.post("/interview/question-with-toools")
def generate_question_with_tools(request: QuestionRequest) -> InterviewQuestionList:
    try:
        schema = InterviewQuestionList.model_json_schema()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a senior software engineering interviewer. "
                    "Use the available tools to identify important areas "
                    "before generating interview questions."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Generate {request.limit} "
                    f"{request.difficulty.value} interview questions "
                    f"about {request.topic}."
                ),
            },
        ]
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            tools=tools,
            tool_choice="auto",
            messages=messages,
        )

        assistant_message = response.choices[0].message
        assistant_payload = {
            "role": "assistant",
            "content": assistant_message.content,
        }
        if assistant_message.tool_calls:
            assistant_payload["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in assistant_message.tool_calls
            ]
        messages.append(assistant_payload)

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                if tool_call.function.name != "get_topic_guidelines":
                    raise ValueError(f"Unknown tool call: {tool_call.function.name}")

                arguments = json.loads(tool_call.function.arguments)
                guidelines = get_topic_guidelines(arguments["topic"])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(guidelines),
                })

            final_response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "InterviewQuestionList",
                        "schema": schema,
                    }
                }
            )
            return parse_question_list(final_response.choices[0].message.content)

        return parse_question_list(assistant_message.content)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )