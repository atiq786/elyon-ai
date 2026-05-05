import os
from typing import List, Optional

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

import base64

load_dotenv()

app = FastAPI()

USE_MODEL = os.getenv("USE_MODEL", "openai")


class Artifact(BaseModel):
    name: str
    contentType: Optional[str] = None
    path: Optional[str] = None

class FailureLocation(BaseModel):
    file: str
    line: int
    column: int

class FailurePayload(BaseModel):
    testTitle: str
    file: str
    line: int
    status: str
    errorMessage: str
    errorStack: str
    screenshotPath: Optional[str] = None
    testCode: Optional[str] = None
    failureLocation: Optional[FailureLocation] = None

@app.get("/")
async def root():
    return {"message": "Elyon analyzer is running", "model": USE_MODEL}

def build_prompt(payload: FailurePayload):
    return f"""
You are a senior QA engineer and software debugger.

Analyze this failed Playwright test.

If a screenshot is provided, use it as primary evidence.
Do not assume the app is slow unless the screenshot/log proves it.
If the expected UI element is visibly missing, say that clearly.
Compare the test code against the screenshot. If the test is looking for text, buttons, selectors, URLs, or assertions that do not match the visible UI, call that out directly.
Do not guess about credentials, backend behavior, or app logic unless the error log or screenshot proves it.

When possible, reference the exact file and line number where the failure occurred.

Test: {payload.testTitle}
File: {payload.file}:{payload.line}
Status: {payload.status}

Error:
{payload.errorMessage}

Stack:
{payload.errorStack}

Test Code:
{payload.testCode}

Return in this exact format:

Quick Fix:
[Return exactly one line of code only. No prose. No markdown. No backticks.]
----------------------------------------------

Failure Type:
[Selector mismatch | Timing issue | Assertion mismatch | Navigation issue | App error | Unknown]

Confidence:
[High | Medium | Low]

Failure Location:
[file:line if available]

❌ Issue:
[One sentence describing what failed]

🧠 Root Cause:
[Specific root cause]

🔍 Evidence:
[Use screenshot + log + test code evidence]


✅ Suggested Fix:
[Exact fix, preferably code-level]

⚡ Alternative Fixes:
[1-2 options]

Failure Location:
{payload.failureLocation}

🛡️ Best Practice:
[How to prevent it next time]
"""

def analyze_with_openai(prompt: str, image_base64: Optional[str]):
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    content = [
        {"type": "text", "text": prompt}
    ]

    if image_base64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}"
            }
        })

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
    )

    return response.choices[0].message.content

def analyze_with_claude(prompt: str, image_base64: Optional[str]) -> str:
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    content = [
        {
            "type": "text",
            "text": prompt
        }
    ]

    if image_base64:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_base64
            }
        })

    response = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=700,
        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return response.content[0].text

def encode_image(path: str):

    try:

        with open(path, "rb") as f:

            return base64.b64encode(f.read()).decode("utf-8")

    except:

        return None

@app.post("/analyze-playwright-failure")
async def analyze_failure(payload: FailurePayload):
    prompt = build_prompt(payload)

    image_base64 = None
    if payload.screenshotPath:
        image_base64 = encode_image(payload.screenshotPath)

    try:
        if USE_MODEL == "openai":
            analysis = analyze_with_openai(prompt, image_base64)
        elif USE_MODEL == "claude":
            analysis = analyze_with_claude(prompt, image_base64)
        else:
            analysis = "Invalid model"

        return {
            "analysis": analysis,
            "model_used": USE_MODEL
        }

    except Exception as e:
        return {
            "analysis": f"AI analysis failed: {str(e)}",
            "model_used": USE_MODEL
        }