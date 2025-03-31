import os
import sent2vec

def load_sent2vec_model(model_path):
    """
    Load a pre-trained Sent2Vec model
    
    Args:
        model_path (str): Path to the Sent2Vec model file
        
    Returns:
        sent2vec.Sent2vecModel: Loaded model or None if failed
    """
    try:
        print(f"Loading Sent2Vec model from {model_path}")
        
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return None
        
        model = sent2vec.Sent2vecModel()
        model.load_model(model_path)
        
        print("Sent2Vec model loaded successfully")
        return model
    
    except Exception as e:
        print(f"Error loading Sent2Vec model: {str(e)}")
        return None

def sentence_embedding(model, sentence):
    """
    Embed a sentence using the Sent2Vec model
    
    Args:
        model (sent2vec.Sent2vecModel): Loaded Sent2Vec model
        sentence (str): Sentence to embed
        
    Returns:
        numpy.ndarray: Embedding vector
    """
    try:
        # Preprocess sentence
        sentence = sentence.replace('\n', ' ')
        sentence = sentence.strip()
        
        # Skip empty sentences
        if not sentence:
            return None
        
        # Get embedding
        embedding = model.embed_sentence(sentence)
        
        # Return the first (and only) vector in the result
        return embedding[0]
    
    except Exception as e:
        print(f"Error generating sentence embedding: {str(e)}")
        return None

def release_model(model, model_path):
    """
    Release Sent2Vec model shared memory
    
    Args:
        model (sent2vec.Sent2vecModel): Loaded Sent2Vec model
        model_path (str): Path to the model file
    """
    try:
        if model:
            model.release_shared_mem(model_path)
            print("Sent2Vec model released")
    except Exception as e:
        print(f"Error releasing Sent2Vec model: {str(e)}")