import re
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Download NLTK data (only runs once)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('punkt', quiet=True)
from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words('english'))

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in STOP_WORDS]
    words = [w for w in words if len(w) > 2]
    
    # Prefer nouns for much cleaner topic names
    try:
        tagged = nltk.pos_tag(words)
        nouns = [w for w, t in tagged if t.startswith('NN')]
        if len(nouns) > 0:
            words = nouns
    except Exception:
        pass
        
    return ' '.join(words)

def cluster_documents(doc_objects, n_clusters=5, custom_names=None):
    """
    doc_objects: list of dicts, e.g. [{"title": "Doc1", "text": "Content..."}, ...]
    returns rich structured data for the frontend mapping.
    """
    cleaned_docs = [preprocess(d.get('text', '')) for d in doc_objects]
    
    valid_indices = [i for i, d in enumerate(cleaned_docs) if len(d.strip()) > 0]
    cleaned_docs = [cleaned_docs[i] for i in valid_indices]
    original_docs = [doc_objects[i] for i in valid_indices]
    
    if len(cleaned_docs) < 2:
        return {'error': 'Not enough valid text content extracted to cluster.'}
        
    valid_custom_names = [n.strip() for n in custom_names if n.strip()] if custom_names else []

    vectorizer = TfidfVectorizer(max_features=300, ngram_range=(1, 2), min_df=1)
    pca = PCA(n_components=2, random_state=42)
    cluster_info = {}
    coords_list = []

    if valid_custom_names:
        # SUPERVISED MODE: Match documents to custom names using cosine similarity
        vectorizer.fit(cleaned_docs + valid_custom_names)
        tfidf_matrix = vectorizer.transform(cleaned_docs)
        custom_tfidf = vectorizer.transform(valid_custom_names)
        
        from sklearn.metrics.pairwise import cosine_similarity
        sim_matrix = cosine_similarity(tfidf_matrix, custom_tfidf) # shape: (n_docs, n_custom_names)
        
        labels = []
        confidences = []
        for i in range(len(cleaned_docs)):
            best_score = np.max(sim_matrix[i])
            if best_score > 0.01:
                labels.append(np.argmax(sim_matrix[i]))
                conf = int(best_score * 100)
                confidences.append(max(40, min(99, conf + 40)))
            else:
                labels.append(len(valid_custom_names)) # "Uncategorized"
                confidences.append(10)
                
        n_clusters = len(valid_custom_names) + 1
        
        for cluster_id in range(n_clusters):
            folder_name = valid_custom_names[cluster_id] if cluster_id < len(valid_custom_names) else "Uncategorized"
            cluster_doc_indices = np.where(np.array(labels) == cluster_id)[0]
            
            if len(cluster_doc_indices) == 0:
                if cluster_id < len(valid_custom_names):
                    cluster_info[cluster_id] = {'id': cluster_id, 'name': folder_name, 'keywords': [folder_name], 'docs': [], 'count': 0, 'avg_conf': 0}
                continue
                
            cluster_docs = []
            cluster_confs = []
            for idx in cluster_doc_indices:
                doc = original_docs[idx].copy()
                doc['confidence'] = confidences[idx]
                doc['cluster_id'] = cluster_id
                doc['path'] = original_docs[idx].get('path', doc['title'])
                cluster_docs.append(doc)
                cluster_confs.append(confidences[idx])
                
            cluster_info[cluster_id] = {
                'id': cluster_id,
                'name': folder_name.title(),
                'keywords': [folder_name],
                'docs': cluster_docs,
                'count': len(cluster_docs),
                'avg_conf': int(np.mean(cluster_confs)) if cluster_confs else 0
            }
            
        if tfidf_matrix.shape[1] < 2:
            coords_2d = np.zeros((tfidf_matrix.shape[0], 2))
        else:
            coords_2d = pca.fit_transform(tfidf_matrix.toarray())
            
        for i, idx in enumerate(valid_indices):
            coords_list.append({
                'x': float(coords_2d[i][0]) if not np.isnan(coords_2d[i][0]) else 0.0,
                'y': float(coords_2d[i][1]) if not np.isnan(coords_2d[i][1]) else 0.0,
                'cluster': int(labels[i]),
                'title': original_docs[i]['title'],
                'path': original_docs[i].get('path', original_docs[i]['title'])
            })
            
    else:
        # UNSUPERVISED K-MEANS MODE
        if len(cleaned_docs) < n_clusters:
            n_clusters = max(2, len(cleaned_docs))
            
        tfidf_matrix = vectorizer.fit_transform(cleaned_docs)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(tfidf_matrix)
        
        distances = kmeans.transform(tfidf_matrix)
        confidences = []
        for i in range(len(labels)):
            dist = distances[i, labels[i]]
            confidences.append(max(10, min(99, int((1 - dist) * 100))))
            
        feature_names = vectorizer.get_feature_names_out()
        
        for cluster_id in range(n_clusters):
            cluster_doc_indices = np.where(labels == cluster_id)[0]
            if len(cluster_doc_indices) == 0:
                cluster_info[cluster_id] = {'id': cluster_id, 'name': f"Folder {cluster_id+1}", 'keywords': [], 'docs': [], 'count': 0, 'avg_conf': 0}
                continue
                
            cluster_tfidf_avg = tfidf_matrix[cluster_doc_indices].toarray().mean(axis=0)
            top_word_indices = cluster_tfidf_avg.argsort()[-5:][::-1]
            keywords = [feature_names[i] for i in top_word_indices]
            
            # Simple and proper naming convention
            if keywords:
                main_topic = keywords[0].title()
                folder_name = f"{main_topic} Documents"
            else:
                folder_name = f"General Folder {cluster_id+1}"
                
            cluster_docs = []
            cluster_confs = []
            for idx in cluster_doc_indices:
                doc = original_docs[idx].copy()
                doc['confidence'] = confidences[idx]
                doc['cluster_id'] = cluster_id
                doc['path'] = original_docs[idx].get('path', doc['title'])
                cluster_docs.append(doc)
                cluster_confs.append(confidences[idx])
                
            cluster_info[cluster_id] = {
                'id': cluster_id,
                'name': folder_name,
                'keywords': keywords,
                'docs': cluster_docs,
                'count': len(cluster_docs),
                'avg_conf': int(np.mean(cluster_confs)) if cluster_confs else 0
            }
            
        if tfidf_matrix.shape[1] < 2:
            coords_2d = np.zeros((tfidf_matrix.shape[0], 2))
        else:
            coords_2d = pca.fit_transform(tfidf_matrix.toarray())
            
        for i, idx in enumerate(valid_indices):
            coords_list.append({
                'x': float(coords_2d[i][0]) if not np.isnan(coords_2d[i][0]) else 0.0,
                'y': float(coords_2d[i][1]) if not np.isnan(coords_2d[i][1]) else 0.0,
                'cluster': int(labels[i]),
                'title': original_docs[i]['title'],
                'path': original_docs[i].get('path', original_docs[i]['title'])
            })

    # Filter out empty Uncategorized
    final_cluster_info = {str(k): v for k, v in cluster_info.items() if v.get('count', 0) > 0 or int(k) < (len(valid_custom_names) if valid_custom_names else 0)}

    return {
        'n_clusters': len(final_cluster_info),
        'cluster_info': final_cluster_info,
        'coords': coords_list
    }
