from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> list:
    with torch.no_grad():
        embedding = model.encode(text, convert_to_tensor=True)
    return embedding.tolist()
