import pandas as pd
import numpy as np

static_products = [
    {"product_id": 886029004, "thumbnail": "/products/886029004.jpg"},
    {"product_id": 252298006, "thumbnail": "/products/252298006.jpg"},
    {"product_id": 3, "thumbnail": "/products/4.jpg"},
    {"product_id": 5, "thumbnail": "/products/5.jpg"},
]

static_liked_feedback = [
    {"user_id": 2, "product_id": 886029004, "liked": True},
    {"user_id": 2, "product_id": 252298006, "liked": True},
    {"user_id": 2, "product_id": 3, "liked": True},
]

static_metadata = pd.read_csv('/path/to/metadata2.csv')
static_image_embeddings = np.load("/path/to/image_embeddings.npy")
static_images_path = static_metadata['image_path'].tolist()


def get_recommendations(user_id: int, top_k: int = 3):
    liked_feedback = [fb for fb in static_liked_feedback if fb["user_id"] == user_id and fb["liked"]]
    if not liked_feedback:
        return {"liked_images": [], "recommendations": []}

    liked_product_ids = [fb["product_id"] for fb in liked_feedback]
    products = [p for p in static_products if p["product_id"] in liked_product_ids]

    liked_images = []
    indices = []
    for product in products:
        thumbnail = product["thumbnail"]
        image_name = thumbnail.split('/')[-1]  # e.g., "886029004.jpg"
        matched_rows = static_metadata[static_metadata['image_path'].str.endswith(image_name)]
        if not matched_rows.empty:
            liked_images.append(matched_rows.iloc[0]['image_path'])
            indices.append(matched_rows.index[0])

    # print(liked_images)
    # print(indices)

    similar_idx_all_liked = []

    for index in indices:
        similarity_scores = static_image_embeddings[index].dot(static_image_embeddings.T)
        top_indices = np.argsort(similarity_scores)[::-1][:top_k]
        similar_idx_all_liked.extend(top_indices)
    
    similar_idx_all_liked = list(dict.fromkeys(similar_idx_all_liked))


    result_paths = [
        static_metadata.loc[idx, "image_path"].replace("/content/new/", "/products/") 
        for idx in similar_idx_all_liked
    ]
    
    # print(result_paths)

    if not similar_idx_all_liked:
        return {
            "recommendations": []
        }

    else:
        return {
            "liked_images": liked_images,
            "recommendations": result_paths
        }

if __name__ == "__main__":
    user_id = 2
    result = get_recommendations(user_id)
    print("Final Result:", result)