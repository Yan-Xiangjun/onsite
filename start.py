import subprocess
import time
import sys


def run_servers():

    if sys.platform == 'win32':
        server_path = r'.\llama-b7502-bin-win-cuda-12.4-x64\llama-server.exe'
        llama_cmd = rf'{server_path} --models-preset .\models\preset.ini --no-webui > .\log\server1.log 2>&1'
        llama_proc = subprocess.Popen(llama_cmd, shell=True)
        lst = [llama_proc]
    else:
        server_path = r'~/llama.cpp-b7502/build/bin/llama-server'
        llama_cmd = f'{server_path} --models-preset ./models/preset.ini --no-webui > ./log/server1.log 2>&1'
        llama_proc = subprocess.Popen(llama_cmd, shell=True)
        flask_proc = subprocess.Popen("python main.py", shell=True)
        lst = [flask_proc, llama_proc]

    print("服务器已启动。按 Ctrl+C 退出...")

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        print("\n关闭LLM服务...")
    finally:
        for t in lst:
            t.terminate()
            t.wait()
        print("服务器已关闭。")


if __name__ == "__main__":
    run_servers()
