# MLLM AiCar 서버

이 프로젝트는 자동차 내에서 MLLM 인공지능을 사용할 수 있도록 하는 시스템의 서버 코드입니다.

## Installation and start up

1. Install [GraphViz](https://graphviz.org/download/)
    ```bash
    sudo apt install graphviz graphviz-dev
    ```
2. (Windows) Install [C++ Build Tools](https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/)

3. If you are using PDM,

    ```bash
    pdm install
    ```
    or using pip

    ```bash
    pip install .
    ```

4. Install [Ollama](https://ollama.com/download)

5. Pull ollama model
    ```bash
    ollama pull llama3.1:8b
    ```
    ```bash
    ollama pull gpt-oss:20b
    ```

## How to start

```bash
python -m mllm_server
```