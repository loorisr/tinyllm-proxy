# TinyLLM Proxy
## Dead simple LLM proxy

Simple alternative to [LiteLLM Proxy](https://docs.litellm.ai/docs/simple_proxy). 151 Mo vs 1.8 Go

Forward requests of `/chat/completions` and `/v1/chat/completions` to the desired model.

It centralizes the API key and can use the model names your want.

## Usage

Configure `models.yaml` with the list of your models/API endpoint/API keys. 

With the following example, when receiving a request with model `reasoning`, it will forward the request to `gemini-2.0-flash-thinking-exp-01-21`  

````yaml
mistral-small-latest:
  api_key: "mykey"
  endpoint: "https://api.mistral.ai/v1"
  model_name: "mistral/mistral-small-latest"

reasoning:
  api_key: "mykey"
  model_name: "gemini/gemini-2.0-flash-thinking-exp-01-21"

default:
  model_name: "gemini-2.0-flash"
````