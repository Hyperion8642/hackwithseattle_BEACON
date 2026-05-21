import os
import numpy as np
import plotly.express as px
from sklearn.manifold import TSNE
from qdrant_client import QdrantClient

# Using absolute path logic
QDRANT_LOCAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "qdrant_store")
QDRANT_COLLECTION = "the_book"

def visualize_embeddings_3d():
    print("Loading Qdrant database...")
    client = QdrantClient(path=QDRANT_LOCAL_PATH)
    
    # Scroll through all points
    records, _ = client.scroll(
        collection_name=QDRANT_COLLECTION,
        limit=1000,
        with_vectors=True,
        with_payload=True
    )
    
    if not records:
        print("No records found in database.")
        return
        
    print(f"Found {len(records)} chunks. Extracting embeddings...")
    
    vectors = []
    texts = []
    pages = []
    
    for record in records:
        vectors.append(record.vector)
        # Format text with HTML line breaks for Plotly tooltip
        raw_text = record.payload.get("text", "")
        # Break text into chunks of 60 chars for readability
        formatted_text = "<br>".join([raw_text[i:i+60] for i in range(0, len(raw_text), 60)])
        texts.append(formatted_text)
        pages.append(record.payload.get("page", 0))
        
    vectors = np.array(vectors)
    
    print("Reducing dimensions to 3D with t-SNE...")
    perplexity = min(30, len(vectors) - 1)
    
    # 3D projection
    tsne = TSNE(n_components=3, perplexity=perplexity, random_state=42, init='pca', learning_rate='auto')
    vectors_3d = tsne.fit_transform(vectors)
    
    print("Plotting Interactive 3D Chart...")
    fig = px.scatter_3d(
        x=vectors_3d[:, 0], 
        y=vectors_3d[:, 1], 
        z=vectors_3d[:, 2],
        color=pages,
        hover_name=texts,
        color_continuous_scale="Viridis",
        title="Interactive 3D Semantic Landscape of 'The Book'",
        labels={"color": "Page Number"}
    )
    
    fig.update_traces(marker=dict(size=6, opacity=0.8))
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=40))
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings_3d.html")
    fig.write_html(out_path)
    print(f"Visualization saved to {out_path}")

if __name__ == "__main__":
    visualize_embeddings_3d()
