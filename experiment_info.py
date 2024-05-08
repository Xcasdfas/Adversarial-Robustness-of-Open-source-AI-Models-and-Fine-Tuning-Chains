dataset_names = {
    "sst2": {"default": "train"},
    "imdb": {"plain_text": "train"},
    "rotten_tomatoes": {"default": "train"},
    "amazon_polarity": {"amazon_polarity": "train"},
}

model_info = {
    # Chain 1
    "mrm8488/distilroberta-finetuned-tweets-hate-speech": {
        "num_labels": 2, "embedding_path": "roberta.embeddings.word_embeddings"
    },
    "hackathon-pln-es/detect-acoso-twitter-es": {
        "num_labels": 2, "embedding_path": "roberta.embeddings.word_embeddings"
    },
    # Chain 2
    "juliensimon/reviews-sentiment-analysis": {
        "num_labels": 2, "embedding_path": "distilbert.embeddings.word_embeddings"
    },
    "houssemmammeri/revsen-v1": {
        "num_labels": 2, "embedding_path": "distilbert.embeddings.word_embeddings"
    },
    # Chain 3
    "ProsusAI/finbert": {
        "num_labels": 3, "embedding_path": "bert.embeddings.word_embeddings"
    },
    "ziweichen/finbert-fomc": {
        "num_labels": 3, "embedding_path": "bert.embeddings.word_embeddings"
    },
    # Chain 4
    "ProsusAI/finbert": {
        "num_labels": 3, "embedding_path": "bert.embeddings.word_embeddings"
    },
    "kk08/cryptobert": {
        "num_labels": 2, "embedding_path": "bert.embeddings.word_embeddings"
    },
    # Chain 5
    "ProsusAI/finbert": {
        "num_labels": 3, "embedding_path": "bert.embeddings.word_embeddings"
    },
    "yiyanghkust/finbert-esg": {
        "num_labels": 4, "embedding_path": "bert.embeddings.word_embeddings"
    },
    # Chain 6
    "idea-ccnl/erlangshen-roberta-330m-sentiment": {
        "num_labels": 2, "embedding_path": "bert.embeddings.word_embeddings"
    },
    "tezign/erlangshen-sentiment-finetune": {
        "num_labels": 2, "embedding_path": "bert.embeddings.word_embeddings"
    },
    # Chain 7
    "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis": {
        "num_labels": 3, "embedding_path": "roberta.embeddings.word_embeddings"
    },
    "finscience/fs-distilroberta-fine-tuned": {
        "num_labels": 3, "embedding_path": "roberta.embeddings.word_embeddings"
    },
    # Chain 8
    "jarvisx17/japanese-sentiment-analysis": {
        "num_labels": 2, "embedding_path": "bert.embeddings.word_embeddings"
    },
    "minutillamolinara/bert-japanese_finetuned-sentiment-analysis": {
        "num_labels": 2, "embedding_path": "bert.embeddings.word_embeddings"
    },
    # Chain 9
    "hazqeel/electra-small-finetuned-malay-english": {
        "num_labels": 2, "embedding_path": "electra.embeddings.word_embeddings"
    },
    "hazqeel/electra-small-doa-finetuned-ms-en-v3": {
        "num_labels": 2, "embedding_path": "electra.embeddings.word_embeddings"
    },
    # Chain 10
    "gooohjy/suicidal-electra": {
        "num_labels": 2, "embedding_path": "electra.embeddings.word_embeddings"
    },
    "sentinet/suicidality": {
        "num_labels": 2, "embedding_path": "electra.embeddings.word_embeddings"
    },
    # M19
    "distilbert-base-uncased-finetuned-sst-2-english": {
        "num_labels": 2, "embedding_path": "distilbert.embeddings.word_embeddings"
    },
    # M20
    "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis": {
        "num_labels": 3, "embedding_path": "roberta.embeddings.word_embeddings"
    },
}

dataset_mappings = {
    "sst2": {
        "default": lambda x: {"x": x["sentence"], "y": 1 if x["label"] > 0.5 else 0}
    },
    "imdb": {
        "default": lambda x: {"x": x["text"], "y": 1 if x["label"] == 'pos' else 0}
    },
    "rotten_tomatoes": {
        "default": lambda x: {"x": x["text"], "y": 1 if x["label"] == 'pos' else 0}
    },
    "amazon_polarity": {
        "amazon_polarity": lambda x: {"x": x["content"], "y": 1 if x["label"] == 1 else 0}
    },
}
