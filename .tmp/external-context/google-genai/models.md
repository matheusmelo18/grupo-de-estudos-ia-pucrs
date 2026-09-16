---
source: Official PyPI + GitHub docs
library: google-genai
package: google-genai
topic: model-names-and-client-setup
fetched: 2026-09-16
official_docs: https://ai.google.dev/gemini-api/docs
---

# Google Gemini API - Model Names & Client Setup

## Available Model IDs (Flash Models for Free Tier)

Based on the official SDK documentation (google-genai v2.23.0):

### Flash Models (Available in AI Studio Free Tier)
- **`gemini-2.5-flash`** - Latest flash model with thinking capabilities
- **`gemini-2.0-flash-001`** - Stable release
- **`gemini-2.0-flash`** - Alias for latest 2.0 flash
- **`gemini-1.5-flash`** - Previous generation flash model

### Pro Models
- **`gemini-2.5-pro`** - Latest pro with thinking
- **`gemini-2.0-pro`** - Stable pro model

### Other Models
- **`gemini-2.5-flash-image`** - Image generation
- **`gemini-embedding-001`** - Embedding model
- **`imagen-3.0-generate-002`** / **`imagen-4.0-generate-001`** - Image generation
- **`veo-3.1-generate-preview`** - Video generation

## Correct Client Initialization

### Gemini Developer API (Free Tier)

```python
from google import genai

# Option 1: Pass API key directly
client = genai.Client(api_key='YOUR_GEMINI_API_KEY')

# Option 2: Use environment variable (recommended)
# export GEMINI_API_KEY='your-api-key'
client = genai.Client()  # Automatically reads GEMINI_API_KEY or GOOGLE_API_KEY
```

### Enterprise/Vertex AI

```python
from google import genai

client = genai.Client(
    enterprise=True,
    project='your-project-id',
    location='global'
)
```

### Client Context Manager (Recommended to avoid httpx errors)

```python
from google import genai

with genai.Client(api_key='YOUR_KEY') as client:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )
    print(response.text)
```

### Environment Variables

```bash
# For Developer API (pick ONE):
export GEMINI_API_KEY='your-api-key'
# OR
export GOOGLE_API_KEY='your-api-key'  # Takes precedence if both set

# For Enterprise/Vertex:
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
```

## Making API Calls

### Basic Text Generation

```python
from google import genai

client = genai.Client(api_key='YOUR_KEY')

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?'
)
print(response.text)
```

### With Configuration (Typed or Dict)

```python
from google import genai
from google.genai import types

# Using Pydantic types
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?',
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
        max_output_tokens=1024,
        system_instruction='You are a helpful assistant.',
    ),
)

# Using dictionaries
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Why is the sky blue?',
    config={
        'temperature': 0,
        'top_p': 0.95,
        'top_k': 20,
    },
)
```

### Streaming

```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story in 300 words.'
):
    print(chunk.text, end='')
```

### Async

```python
import asyncio
from google import genai

async def main():
    client = genai.Client(api_key='YOUR_KEY')
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )
    print(response.text)
    await client.aio.aclose()

asyncio.run(main())
```

### Multi-turn Chat

```python
chat = client.chats.create(model='gemini-2.5-flash')
response = chat.send_message('Tell me a story')
print(response.text)
response = chat.send_message('Summarize that story in 1 sentence')
print(response.text)
```

### With Function Calling

```python
from google.genai import types

def get_current_weather(location: str) -> str:
    """Returns the current weather.
    
    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return 'sunny'

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather like in Boston?',
    config=types.GenerateContentConfig(tools=[get_current_weather]),
)
print(response.text)
```

### JSON Response Schema

```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me a random user profile.',
    config={
        'response_mime_type': 'application/json',
        'response_json_schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
            },
            'required': ['name', 'age'],
        }
    },
)
print(response.text)
```
