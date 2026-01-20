# Introduction
This repository implemented an offline voice assistant for providing construction workers with onsite operating instructions. We developed an AI agent which is integrated with three tools: "photography", "retrieving", and "showing reference". It is powered by two lightweight LLMs and can be deployed on a smartphone, without relying on any cloud computing platforms.
# Run the benchmark on windows computer
1. Clone our repository
    ```pwsh
    git clone https://github.com/Yan-Xiangjun/onsite.git
    ```
2. Download llama.cpp b7502 from [here](https://github.com/ggml-org/llama.cpp/releases/download/b7502/llama-b7502-bin-win-cuda-12.4-x64.zip) and unzip it.
3. Download NVIDIA CUDA Runtime from [here](https://github.com/ggml-org/llama.cpp/releases/download/b7502/cudart-llama-bin-win-cuda-12.4-x64.zip) and unzip it. Then, move all the files to the `llama-b7502-bin-win-cuda-12.4-x64` folder.
4. Move the `llama-b7502-bin-win-cuda-12.4-x64` folder to the `onsite` folder.
5. Install basic python packages:
    ```bash
    pip install requests pyyaml pandas openpyxl
    ```
6. Download `Qwen3VL-4B-Instruct-Q4_K_M.gguf` and `mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf` from `https://www.modelscope.cn/models/Qwen/Qwen3-VL-4B-Instruct-GGUF/files`. Then, put them into the `onsite/models/qwen3-vl/` folder and copy the `Qwen3VL-4B-Instruct-Q4_K_M.gguf` to the `onsite/models/` folder.
7. If this is your first time running the benchmark, please open create_cache.py, uncomment line 13 and comment out line 14. Then, execute `create_cache.py` to generate cache for the document.
8. Execute `start.py` to start the server.
9. Execute `benchmark.py`. The results will be put in the `benchmark` file.
10. You can open `onsite/benchmark/show_all_ref.py`, uncomment line 9 and comment out line 10. Then, execute `show_all_ref.py` to visualize all the bounding boxes.

# Deploy the copilot on a smartphone
## Installation requirements
You will need an Android phone to run this agent. A high-performance SoC such as the Snapdragon 8 Elite Gen 5 is recommended to achieve faster running speed.
## Installation steps
### Part 1: Prepare APPs
1. Download Termux from [here](https://github.com/termux/termux-app/releases/download/v0.118.1/termux-app_v0.118.1+github-debug_arm64-v8a.apk) and install it on your phone.

2. Download Termux-API from [here]() and install it on your phone.

3. Go to the "Settings" on your phone and give Termux-API permission to access camera and microphone. Furthermore, Termux should be allowed to run in the background completely. Otherwise, when you open the Web frontend, since Termux goes into the background, Android's power-saving strategy may automatically reduce the performance of Termux, causing severe lag. If your phone has a floating window function, it is recommended that you place Termux in a bubble to alleviate this problem as much as possible.

### Part 2: Prepare Linux environment for Termux

Open Termux. At this point, you will enter a terminal. Then:

1. Execute the following command to update software packages. If Termux asks you to enter an option while updating, please enter `N`.
    ```bash
    pkg upgrade
    ```
2. Install basic Linux packages:
    ```bash
    apt install -y build-essential cmake binutils git wget ninja libandroid-spawn python python-pip unzip tur-repo
    ```
3. Install other packages:
    ```bash
    apt install -y sox llvm-14 portaudio
    ```

### Part 3: Prepare Python packages

1. (Optional) Set a mirror repository of Pypi to speed up download. For example, to use USTC open source software mirror, execute this command:
    ```bash
    pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/simple
    ```
2. Add tur repository:
    ```bash
    pip config set global.extra-index-url https://termux-user-repository.github.io/pypi/
    ```
2. Install basic python packages:
    ```bash
    pip install setuptools wheel packaging pyproject_metadata cython
    ```
4. Install some pre-built Python packages by apt:
    ```bash
    apt install -y python-onnxruntime python-torchaudio python-pillow
    apt install -y python-scipy 
    ```
5. Install some pre-built Python packages from tur:
    ```bash
    pip install numpy==1.26.4
    pip install scikit-learn==1.6.1
    ```
6. Build Python packages:
    ```bash
    LDFLAGS=-llog pip install sentencepiece==0.2.1
    LLVM_CONFIG=$PREFIX/opt/libllvm-14/bin/llvm-config pip install llvmlite==0.42.0
    pip install numba==0.59.0 --no-build-isolation
    pip install pyaudio --no-build-isolation
    ```
7. Clone funasr:
    ```bash
    git clone https://github.com/Yan-Xiangjun/FunASR.git && cd FunASR/runtime/python/onnxruntime
    ```
8. Build funasr_onnx. Please replace `xx` with the actual Python version on your phone.
    ```bash
    LDFLAGS=-lpython3.xx pip install -e ./ && cd ~
    ```
9. Install other necessary Python packages:
    ```bash
    pip install openwakeword==0.4.0 silero-vad flask flask-cors
    ```

### Part 4: Prepare llama.cpp

1. Download the source code of llama.cpp, and unzip it:
    ```bash
    cd ~ && wget https://github.com/ggml-org/llama.cpp/archive/refs/tags/b7502.zip
    unzip b7502.zip
    ```
2. Build llama.cpp
    ```bash
    cd llama.cpp-b7502 && cmake -B build
    cmake --build build --config Release
    ```

### Part 5: Deploy our agent
1. Clone our repository
    ```bash
    cd ~ && git clone https://github.com/Yan-Xiangjun/onsite.git
    ```
2. Download `Qwen3VL-4B-Instruct-Q4_K_M.gguf` and `mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf` from `https://www.modelscope.cn/models/Qwen/Qwen3-VL-4B-Instruct-GGUF/files`. Then, put them into the `onsite/models/qwen3-vl/` folder and copy the `Qwen3VL-4B-Instruct-Q4_K_M.gguf` to the `onsite/models/` folder.

### Part 6: Use the agent
1. Execute `start.py` to start the server.

2. If this is your first time using this App, please press and hold the leftmost edge of your screen and drag it to the right. At this point, a sidebar will appear on the left. Click on the "NEW SESSION" button within it to enter a new terminal. Execute the following command to generate cache for the files in the "documents" folder:
    ```bash
    python ./create_cache.py
    ```
3. Use your browser to open localhost:8000. At this point, you can start chatting with the agent.

## Reference
1. https://github.com/termux/termux-packages/discussions/19126
2. https://mirrors.ustc.edu.cn/help/pypi.html
3. https://zhuanlan.zhihu.com/p/690429761
4. https://github.com/modelscope/FunASR/tree/main/runtime/python/onnxruntime


