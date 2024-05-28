#!/bin/bash
conda activate train-env
python ./gen_dataset_from_text_ali.py -f $1 -t $2
conda deactivate
conda activate llm-env
