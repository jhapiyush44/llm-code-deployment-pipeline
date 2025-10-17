import os
import re
import json
import base64
import asyncio
import httpx
import stat
import shutil
from typing import List, Optional

from config import get_settings, get_api_info

settings = get_settings()

# Import constants
from constants import GITHUB_API_BASE, GEMINI_API_URL

# Set up GitHub Pages URL based on username
GITHUB_PAGES_BASE = f"https://{settings.GITHUB_USERNAME}.github.io"

# Get API configuration (Gemini only)
api_url, api_key = get_api_info(settings)


def verify_secret(secret_from_request: str) -> bool:
    """Checks if the provided secret matches the expected student secret."""
    return secret_from_request == settings.STUDENT_SECRET


def data_uri_to_gemini_part(data_uri: str) -> Optional[dict]:
    """
    Extracts Base64 data and MIME type from a Data URI and formats it
    as the 'inlineData' structure required for a Gemini API multimodal part.
    """
    if not data_uri or not data_uri.startswith("data:"):
        return None

    try:
        match = re.search(r"data:(?P<mime_type>[^;]+);base64,(?P<base64_data>.*)", data_uri, re.IGNORECASE)
        if not match:
            return None

        mime_type = match.group('mime_type')
        base64_data = match.group('base64_data')

        if not mime_type.startswith("image/"):
            return None

        return {
            "inlineData": {
                "data": base64_data,
                "mimeType": mime_type
            }
        }
    except Exception:
        return None


def is_image_data_uri(data_uri: str) -> bool:
    """Checks if the data URI refers to an image based on the MIME type."""
    if not data_uri or not data_uri.startswith("data:"):
        return False
    return re.search(r"data:image/[^;]+;base64,", data_uri, re.IGNORECASE) is not None


async def save_generated_files_locally(task_id: str, files: dict) -> str:
    """
    Saves generated files into generated_tasks/<task_id> and returns that path.
    """
    base_dir = os.path.join(os.getcwd(), "generated_tasks")
    task_dir = os.path.join(base_dir, task_id)
    os.makedirs(task_dir, exist_ok=True)

    for filename, content in files.items():
        file_path = os.path.join(task_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    return task_dir


async def save_attachments_locally(task_dir: str, attachments: List[object]) -> List[str]:
    """
    Decodes and saves attachments (provided as Base64 Data URIs) into the task directory.
    Returns a list of saved filenames.
    """
    saved_files = []

    for attachment in attachments:
        filename = getattr(attachment, 'name', None)
        data_uri = getattr(attachment, 'url', None)
        if not filename or not data_uri or not data_uri.startswith("data:"):
            continue

        match = re.search(r"base64,(.*)", data_uri, re.IGNORECASE)
        if not match:
            continue

        base64_data = match.group(1)
        file_path = os.path.join(task_dir, filename)

        file_bytes = base64.b64decode(base64_data)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        saved_files.append(filename)

    return saved_files


async def call_llm_for_code(prompt: str, task_id: str, image_parts: List[dict]) -> dict:
    """
    Calls the Gemini API to generate the web application files and returns a dict.
    This mirrors the behaviour originally in main.py (with retries and schema enforcement).
    """
    normalized_prompt = prompt.lower().strip()
    if "captcha solver" in normalized_prompt and "responsive" not in normalized_prompt:
        prompt += (
            "\n\n"
            "Ensure the web app is a single, complete, fully responsive HTML file using Tailwind CSS. "
            "It must fetch an image from the query parameter '?url=https://.../image.png', display it, "
            "and perform OCR using Tesseract.js via CDN. "
            "If the URL parameter is missing, use the attached sample image by default. "
            "Show the recognized text and any errors clearly in the UI. "
            "Return output strictly as a JSON object with keys: 'index.html', 'README.md', and 'LICENSE'."
        )

    system_prompt = (
        "You are an expert full-stack engineer and technical writer. Your task is to generate "
        "three files in a single structured JSON response: 'index.html', 'README.md', and 'LICENSE'. "
        "The 'index.html' must be a single, complete, fully responsive HTML file using Tailwind CSS "
        "for styling and must implement the requested application logic.\n"
        "The 'README.md' must be professional, detailed, and user-friendly. It should include: "
        "a project summary, setup instructions, usage instructions, a code explanation section, "
        "and a license section. Use clear Markdown formatting, code blocks, and bullet points where helpful.\n"
        "The 'LICENSE' must contain the full text of the MIT license."
    )

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "index.html": {"type": "STRING"},
            "README.md": {"type": "STRING"},
            "LICENSE": {"type": "STRING"}
        },
        "required": ["index.html", "README.md", "LICENSE"]
    }

    contents = []
    if image_parts:
        all_parts = image_parts + [{"text": prompt}]
        contents.append({"parts": all_parts})
    else:
        contents.append({"parts": [{"text": prompt}]})

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    max_retries = 3
    base_delay = 1

    for attempt in range(max_retries):
        try:
            url = f"{api_url}?key={api_key}"
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, json=payload, headers={"Content-Type": "application/json"})
                response.raise_for_status()
                result = response.json()
                json_text = result['candidates'][0]['content']['parts'][0]['text']
                generated_files = json.loads(json_text)
                return generated_files
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))

    raise Exception("LLM Code Generation Failure")


async def notify_evaluation_server(
    evaluation_url: str,
    email: str,
    task_id: str,
    round_index: int,
    nonce: str,
    repo_url: str,
    commit_sha: str,
    pages_url: str
) -> bool:
    payload = {
        "email": email,
        "task": task_id,
        "round": round_index,
        "nonce": nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }

    max_retries = 3
    base_delay = 1

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(evaluation_url, json=payload)
                response.raise_for_status()
                return True
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))

    return False
