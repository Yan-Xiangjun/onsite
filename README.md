## Introduction
This repository implemented an offline voice assistant for providing construction workers with onsite operating instructions. We developed an AI agent which is integrated with three tools: "photography", "retrieving", and "showing reference". It is powered by two lightweight LLMs and can be deployed on a smartphone, without relying on any cloud computing platforms.
<table>
<tr>
<td align="center">
<img src="./demo/plank.gif" alt="GIF 1" style="width: 200px;"/>
<br>Floor laying
</td>
<td align="center">
<img src="./demo/block.gif" alt="GIF 2" style="width: 200px;"/>
<br>Block masonry
</td>
<td align="center">
<img src="./demo/rebar.gif" alt="GIF 3" style="width: 200px;"/>
<br>Rebar tying
</td>
</tr>
</table>
## Installation requirements
You will need an Android phone to run this agent. A high-performance SoC such as the Snapdragon 8 Gen 3 or the Snapdragon 8 Elite is recommended to achieve faster running speed.
## Installation steps
### Part 1: Prepare APPs
1. Download Termux from [here](https://github.com/termux/termux-app/releases/download/v0.118.1/termux-app_v0.118.1+github-debug_arm64-v8a.apk) and install it on your phone.

2. Download Termux-API from [here]() and install it on your phone.

3. Go to the "Settings" on your phone and give Termux-API permission to access camera and microphone. Furthermore, Termux should be allowed to run in the background completely. Otherwise, when you open the Web frontend, since Termux goes into the background, Android's power-saving strategy may automatically reduce the performance of Termux, causing severe lag.

### Part 2: Prepare Linux environment for Termux

Open Termux. At this point, you will enter a terminal. Then:

1. Execute the following command to update software packages. If Termux asks you to enter an option while updating, please enter `N`.
    ```bash
    pkg upgrade
    ```
2. Install basic Linux packages:
    ```bash
    apt install -y build-essential cmake binutils git wget ninja libandroid-spawn python python-pip unrar unzip rust tur-repo
    ```
3. Install other packages:
    ```bash
    apt install -y sox llvm-14 portaudio
    ```
4. (Optional) Set a mirror repository of Rust Crates to speed up download. For example, to use USTC open source software mirror, execute these commands:
    ```bash
    mkdir -vp ${CARGO_HOME:-$HOME/.cargo}

    cat << EOF | tee -a ${CARGO_HOME:-$HOME/.cargo}/config.toml
    [source.crates-io]
    replace-with = 'ustc'

    [source.ustc]
    registry = "sparse+https://mirrors.ustc.edu.cn/crates.io-index/"

    [registries.ustc]
    index = "sparse+https://mirrors.ustc.edu.cn/crates.io-index/"
    EOF
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
5. Install huggingface-hub
    ```bash
    pip install huggingface-hub==0.30.1
    ```
6. Install some pre-built Python packages from tur:
    ```bash
    pip install numpy==1.26.4
    pip install scikit-learn==1.6.1
    pip install pydantic-core==2.33.0 tokenizers==0.21.1
    ```
7. Build Python packages:
    ```bash
    LDFLAGS=-llog pip install sentencepiece==0.2.0
    pip install safetensors==0.5.3
    LLVM_CONFIG=$PREFIX/opt/libllvm-14/bin/llvm-config pip install llvmlite==0.42.0
    pip install numba==0.59.0
    pip install pyaudio --no-build-isolation
    ```
8. Clone funasr:
    ```bash
    git clone https://github.com/alibaba/FunASR.git && cd FunASR/runtime/python/onnxruntime
    ```
9. Run `nano setup.py`, replace `onnx` in the `install_requires` list with `jieba`, press `Ctrl+X`, then press `Y`, and finally press `Enter`.
10. Build funasr_onnx. Please replace `xx` with the actual Python version on your phone.
    ```bash
    LDFLAGS=-lpython3.xx pip install -e ./ && cd ~
    ```
11. Install other necessary Python packages:
    ```bash
    pip install openwakeword==0.4.0 silero-vad flask flask-cors openai==1.72.0 num2words pydantic==2.11.0 transformers==4.50.3
    ```

### Part 4: Prepare llama.cpp

1. Download the source code of llama.cpp, and unzip it:
    ```bash
    cd ~ && wget https://github.com/ggml-org/llama.cpp/archive/refs/tags/b5009.zip
    unzip b5009.zip
    ```
2. Build llama.cpp
    ```bash
    cd llama.cpp-b5009 && cmake -B build
    cmake --build build --config Release --target llama-qwen2vl-cli llama-server
    ```


### Part 5: Deploy our agent
1. Clone our repository
    ```bash
    cd ~ && git clone https://github.com/Yan-Xiangjun/onsite.git
    ```
2. Download the model.zip and unzip it
    ```bash
    cd ~/on_site/model
    wget https://github.com/Yan-Xiangjun/onsite/releases/download/v0.1/model.part1.rar
    wget https://github.com/Yan-Xiangjun/onsite/releases/download/v0.1/model.part2.rar
    wget https://github.com/Yan-Xiangjun/onsite/releases/download/v0.1/model.part3.rar
    unrar x model.part1.rar
    ```
3. Run the following commands, then press `Ctrl+D` to exit Termux and restart it
    ```bash
    echo "export KMP_DUPLICATE_LIB_OK=TRUE" >> ~/.bashrc
    echo "export onsite_test=0" >> ~/.bashrc
    echo "terminal-onclick-url-open=true" >> ~/.termux/termux.properties
    ```
### Part 6: Use the agent
1. Start the llama.cpp server
    ```bash
    cd ~/on_site && bash ./startggml.sh
    ```
2. Press and hold the leftmost edge of your screen and drag it to the right. At this point, a sidebar will appear on the left. Click on the "NEW SESSION" button within it to enter a new terminal. After that, leave your phone idle for a while to cool it down.
3. If this is your first time using this App, please execute the following command to generate cache for the files in the "documents" folder:
    ```bash
    python ./create_cache.py
    ```
4. Go to the "Settings" on your phone and allow Termux-API to start automatically. Because Android may revoke the auto-start permission without notifying the user, please remember to check whether this permission still exists before each run.
5. Run `python main.py` to start the Webserver. You will see an IP address "127.0.0.1:8000". Click it and a webpage will pop up. At this point, you can start chatting with the agent.

## Reference
1. https://github.com/termux/termux-packages/discussions/19126
2. https://mirrors.ustc.edu.cn/help/crates.io-index.html
3. https://mirrors.ustc.edu.cn/help/pypi.html
4. https://zhuanlan.zhihu.com/p/690429761
5. https://github.com/modelscope/FunASR/tree/main/runtime/python/onnxruntime
6. https://www.modelscope.cn/models/Qwen/Qwen2-VL-2B-Instruct
7. https://www.modelscope.cn/models/bartowski/google_gemma-3-4b-it-GGUF


