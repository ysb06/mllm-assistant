import uvicorn

uvicorn.run("mllm_server.server:fastapi_app", reload=True)