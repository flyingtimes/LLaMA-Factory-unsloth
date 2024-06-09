#!/bin/bash
# 检查是否有至少一个参数传递
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 parameter"
    exit 1
fi

case "$1" in
    extract)
        echo "start extracting..."
        python ./gen_dataset_from_text_ali.py -f $2 -t $3
        ;;
    train)
        echo "start trainning..."
        cat  selfreconition.jsonl output.jsonl  > data/all_data.jsonl
        python split.py
        mlx_lm.lora --model Qwen/Qwen1.5-32B-Chat --train --iter 7000 --data ./data --adapter-path ./adapters --max-seq-length 8192 --batch-size 4 --lora-layers 12
        mlx_lm.fuse --model Qwen/Qwen1.5-32B-Chat --adapter- ./adapters --save-path ../../$2 --de-quantize >quantize.log
        python ../../llama.cpp/convert-hf-to-gguf.py ../../$2 >>quantize.log
        ../../llama.cpp/quantize ../../$2/ggml-model-f16.gguf ../../$2/ggml-model-q4_0.gguf q4_0 >>quantize.log
        ;;
    retrain)
        echo "start trainning..."
        #conda activate llm-env
        #cat  selfreconition.jsonl > data/train.jsonl
        #cat  selfreconition.jsonl output.jsonl  > data/all_data.jsonl
        #python split.py
        #mlx_lm.lora --model Qwen/Qwen1.5-32B-Chat --train --iter 10000 --data ./data --resume-adapter-file ./adapters/adapters.safetensors --max-seq-length 8192 --batch-size 4 --lora-layers 12
        mlx_lm.fuse --model Qwen/Qwen1.5-32B-Chat --adapter-path ./adapters --save-path ../../$2 --de-quantize
        python ../../llama.cpp/convert-hf-to-gguf.py ../../$2 
        ../../llama.cpp/quantize ../../$2/ggml-model-f16.gguf ../../$2/ggml-model-q4_0.gguf q4_0       
        ;;
    chat)
        echo "chatting..."
        ../../llama.cpp/main -m ../../$2/ggml-model-q4_0.gguf -c 512 -b 1024 -n 256 --keep 48  --repeat-penalty 1.0 --in-suffix "<|im_end|>\nassistant" -cnv --color -i  -f ../../llama.cpp/prompts/chat-with-qwen.txt
        ;;
    copy)
        echo "copy model to lm-studio"
        mkdir /Users/clark/.cache/lm-studio/models/clarkchan/$2
        cp ../../$2/ggml-model-f16.gguf /Users/clark/.cache/lm-studio/models/clarkchan/$2/ggml-model-f16.gguf
        cp ../../$2/ggml-model-q4_0.gguf /Users/clark/.cache/lm-studio/models/clarkchan/$2/ggml-model-q4_0.gguf
        ;;
esac
