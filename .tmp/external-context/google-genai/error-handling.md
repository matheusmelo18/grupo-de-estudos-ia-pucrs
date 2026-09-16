---
source: Official PyPI + GitHub docs
library: google-genai
package: google-genai
topic: error-handling-and-503-errors
fetched: 2026-09-16
official_docs: https://ai.google.dev/gemini-api/docs/troubleshooting
---

# Google Gemini API - Error Handling & 503 Errors

## Error Handling

The SDK provides `APIError` class for error handling:

```python
from google.genai import errors

try:
    response = client.models.generate_content(
        model="invalid-model-name",
        contents="What is your name?",
    )
except errors.APIError as e:
    print(e.code)    # HTTP status code (e.g., 404, 429, 500, 503)
    print(e.message) # Error message from API
```

## Common Causes for 503 Errors (Service Unavailable)

503 errors from the Gemini API typically indicate:

### 1. **Model Overloaded / High Traffic**
- The API is experiencing high demand
- The specific model endpoint is temporarily at capacity
- **Solution**: Retry with exponential backoff

### 2. **Rate Limiting (Related to 429)**
- Free tier has lower rate limits than paid
- RPM (requests per minute) and TPM (tokens per minute) limits exceeded
- **Solution**: Implement retry logic, reduce request frequency

### 3. **Temporary Service Outage**
- Google's infrastructure may be experiencing issues
- **Solution**: Check https://status.cloud.google.com or retry later

### 4. **Invalid Model Name**
- Using a model ID that doesn't exist or is deprecated
- **Solution**: Use correct model IDs like `gemini-2.5-flash`, `gemini-2.0-flash-001`

### 5. **Network/Proxy Issues**
- Corporate proxies or firewalls blocking requests
- **Solution**: Configure proxy settings properly

## Retry Strategy (Recommended)

```python
import time
from google.genai import errors

def generate_with_retry(client, model, contents, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
            )
            return response
        except errors.APIError as e:
            if e.code == 503 and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Service unavailable (503), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

## Client Cleanup (Prevents Connection Errors)

Always close the client or use context managers:

```python
# Context manager (recommended)
with genai.Client(api_key='YOUR_KEY') as client:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )

# Or explicit close
client = genai.Client(api_key='YOUR_KEY')
try:
    response = client.models.generate_content(...)
finally:
    client.close()
```

## Environment Variable Configuration

```bash
# For Developer API
export GEMINI_API_KEY='your-api-key'

# For Enterprise/Vertex
export GOOGLE_GENAI_USE_ENTERPRISE=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
export GOOGLE_CLOUD_LOCATION='global'
```

## Common Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid parameters, malformed request |
| 403 | Forbidden | Invalid API key, insufficient permissions |
| 404 | Not Found | Model doesn't exist, wrong endpoint |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Google server issue |
| 503 | Service Unavailable | Model overloaded, temporary outage |
