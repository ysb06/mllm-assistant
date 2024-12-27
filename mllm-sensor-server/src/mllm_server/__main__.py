import uvicorn

uvicorn.run("mllm_server.server:app", reload=True)