prompt_template = """
I would like you to be able to extract upstream model information for a specific model from the Hugging Face model library.

The input content is the model name and model description

Your task is to identify which upstream model the model is fine-tuned from from the input model name & model description.
If you fail to find the upstream model of the input model, the upstream model is N/A.

```
Note that the model name will often imply information about the upstream model for that model
Please pay more attention to the information in the model name
For example:
if a model is named toxic-bert, the upstream model of that model is likely to be bert;
if a model is named t5-small-booksum, the upstream model of that model is likely to be t5-small;
if a model is named Multilingual-MiniLM-L12-H384, the upstream model of that model is likely to be MiniLM;
if a model is named Llama-2-7b-chat-hf, the upstream model of that model is likely to be Llama-2-7b;
if a model is named Llama-2-7b, that model is likely to be a base model whose upstream model is N/A.
if a model description is "FinTwitBERT-sentiment is a finetuned model for classifying the sentiment of financial tweets. 
It uses （https://huggingface.co/StephanAkkerman/FinTwitBERT） FinTwitBERT as a base model", 
the upstream model of that model is StephanAkkerman/FinTwitBERT
'''
If a model is named bge-reranker-large, the upstream model of that model must not be bge-reranker-base;
Note: Despite the similar naming, the 'large' variant could be based on a different architecture or a significantly modified version of the base model.
'''
'''
If a model is named Yi-34B, the upstream model of that model must not be Yi-6B;
Note: The relationship between these models is not clear based solely on naming. They may share a common foundational architecture, but the 34B variant likely has substantial advancements or differences.
'''
'''
If a model is named SPANBert, the upstream model of that model must not be SPANBert.
'''

Output format:
```
model_name:
upstream_model:
```
Model Name:{model_name}
Model Description:{model_description}
"""
