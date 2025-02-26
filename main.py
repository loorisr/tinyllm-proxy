from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
import asyncio
import yaml
import json
import litellm
from pathlib import Path

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load LLM configurations from YAML file
CONFIG_FILE = "models.yaml"
if not Path(CONFIG_FILE).exists():
    raise FileNotFoundError(f"Config file {CONFIG_FILE} not found.")

with open(CONFIG_FILE, "r") as file:
    LLM_CONFIGS = yaml.safe_load(file)
    
# Validate YAML structure
if not isinstance(LLM_CONFIGS, dict):
    raise ValueError("YAML file must contain a dictionary of LLM configurations.")

# print(litellm.supports_function_calling(model="mistral/mistral-small-latest"))
# from litellm import get_supported_openai_params
# params = get_supported_openai_params(model="mistral/mistral-small-latest")
# print(params)
# from litellm import supports_response_schema
# print(supports_response_schema(model="mistral/mistral-small-latest"))

async def async_generator(completion):
    async for chunk in completion:                
        response_data = {
            "id": chunk.id,
            "object": chunk.object,
            "created": chunk.created,
            "model": chunk.model,
            "system_fingerprint": chunk.system_fingerprint,
            "choices": [
                {
                    "index": chunk.choices[0].index,
                    "delta": {
                        "content": getattr(chunk.choices[0].delta, 'content', None)
                    },
                    "finish_reason": chunk.choices[0].finish_reason
                }
            ]
        }
        
        await asyncio.sleep(0)
        yield f"data: {json.dumps(response_data)}\n\n"

# for completion
@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def completion(request: Request):
    key = request.headers.get("Authorization").replace("Bearer ", "")  # type: ignore
    data = await request.json()
    
    if 'stream' in data:
        if type(data['stream']) == str: 
            data['stream'] = data['stream'].lower() == "true"                
       
    if not data['model'] in LLM_CONFIGS:
        data['model'] = LLM_CONFIGS['default']['model_name']
        print("ok")
        
    llm_config = LLM_CONFIGS[data['model']]
    data['api_key'] = llm_config.get("api_key")
    data['api_base'] = llm_config.get("endpoint")
    data['model'] = llm_config.get("model_name")  
    
    print(f"Query to {data['model']}")
            
    response = await litellm.acompletion(**data)
        
    if 'stream' in data and data['stream'] == True: 
        return StreamingResponse(async_generator(response), media_type='text/event-stream')
        
    return response

@app.get("/health")
async def health():
    return {"status": 1}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
