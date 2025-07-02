# MLLM AiCar 서버

이 프로젝트는 자동차 내에서 MLLM 인공지능을 사용할 수 있도록 하는 시스템의 서버 코드입니다.

## Installation and start up

1. If you are using PDM,

    ```bash
    pdm install
    ```
    or using pip

    ```bash
    pdm install
    ```

2. Install [Ollama](https://ollama.com/download)
3. Pull ollama model
    ```bash
    ollama pull llama3.1:8b
    ```
4. Install [GraphViz](https://graphviz.org/download/)
5. (Windows) Install [C++ Build Tools](https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/)


## How to start

```bash
python -m mllm_server
```