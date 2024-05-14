FROM nvcr.io/nvidia/pytorch:24.01-py3

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
RUN pip install -e .[deepspeed,metrics,bitsandbytes,qwen]
RUN pip install "unsloth[colab-new] @ git+https://gitclone.com/github.com/unslothai/unsloth.git"
RUN pip install xformers --no-deps "xformers<0.0.26"
VOLUME [ "/root/.cache/huggingface/", "/app/data", "/app/output" ]
EXPOSE 7860

CMD [ "llamafactory-cli", "webui" ]
