from sentence_transformers import SentenceTransformer
print('Loading model...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded, dim=', model.get_sentence_embedding_dimension())
