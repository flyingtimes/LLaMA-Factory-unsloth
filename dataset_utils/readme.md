## 使用的conda环境
```
conda create -n dataset python=3.10
conda install -c conda-forge poppler
conda activate dataset
```

## 总体思路

从pdf提取文本
将文本拆分成不同的类别的内容
填入json
根据json构建问答对
填入dataset