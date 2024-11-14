"""Extract image embeddings for a list of image urls.

Example usage:
    python extract_img_embs.py
"""
import torch
from fromage import models, utils

from PIL import Image
import os
import requests
from io import BytesIO
import pickle as pkl
from tqdm import tdqm 


def extract_embeddings_for_urls(image_urls: list[str], emb_output_path: str, device: str = "cuda"):
    # Load model checkpoint.
    model = models.load_fromage("./VGloria/")
    model.eval()
    
    # Move model to the specified device
    model.to(device)

    visual_encoder = "openai/clip-vit-large-patch14"
    feature_extractor = utils.get_feature_extractor_for_model(
        visual_encoder, train=False
    )

    output_data = {"paths": [], "embeddings": []}
    with torch.no_grad():
        for img_url in tqdm(image_urls, mininterval=2):
            img = Image.open(BytesIO(requests.get(img_url).content))

            # Move image tensor to device
            img_tensor = utils.get_pixel_values_for_model(feature_extractor, img)
            img_tensor = img_tensor[None, ...].to(device).bfloat16()

            # Compute embeddings on the correct device
            img_emb = model.model.get_visual_embs(img_tensor, mode="retrieval")
            img_emb = img_emb[0, 0, :].cpu()
            output_data["paths"].append(img_url)
            output_data["embeddings"].append(img_emb)
    
    # Save embeddings to output path
    with open(emb_output_path, "wb") as f:
        pkl.dump(output_data, f)

if __name__ == "__main__":
    image_urls = []  # TODO: Replace with image urls
    p = './cc3m_embeddings.pkl'
    with open(p, 'rb') as wf:
          fromage_embs = pkl.load(wf)
          image_urls = fromage_embs['paths']
    if image_urls == []:
        raise ValueError("Please replace `image_urls` with a list of image urls.")

    extract_embeddings_for_urls(image_urls, "./VGlorIA_model/cc3m_embeddings.pkl")
