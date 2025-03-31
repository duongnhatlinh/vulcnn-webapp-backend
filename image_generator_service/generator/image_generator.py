import numpy as np
import networkx as nx
from generator.sent2vec_wrapper import sentence_embedding

def generate_image_representation(pdg, sent2vec_model, embedding_size=128):
    """
    Generate an image representation from a Program Dependency Graph
    
    Args:
        pdg (networkx.DiGraph): Program Dependency Graph
        sent2vec_model: Loaded Sent2Vec model
        embedding_size (int): Embedding vector size
        
    Returns:
        tuple: (degree_channel, closeness_channel, katz_channel) - the three channels of the image
    """
    try:
        # Extract code and labels from PDG
        labels_code = {}
        for node, attrs in pdg.nodes(data=True):
            # Extract code attribute
            code = attrs.get('code', '')
            if not code and 'label' in attrs:
                # Extract code from label if available
                label_text = attrs['label']
                if ',' in label_text:
                    code = label_text[label_text.index(',') + 1:].strip()
            
            if code:
                labels_code[node] = code
        
        # Calculate centrality measures
        degree_cen_dict = nx.degree_centrality(pdg)
        closeness_cen_dict = nx.closeness_centrality(pdg)
        
        # For directed graphs, convert to DiGraph for katz_centrality
        G = nx.DiGraph(pdg) if not isinstance(pdg, nx.DiGraph) else pdg
        try:
            katz_cen_dict = nx.katz_centrality(G)
        except Exception:
            # Fallback if katz_centrality fails (e.g., convergence issues)
            katz_cen_dict = {node: 0.5 for node in G.nodes()}
        
        # Initialize channels
        degree_channel = []
        closeness_channel = []
        katz_channel = []
        
        # Generate weighted embeddings for each node with code
        for node, code in labels_code.items():
            # Get embedding vector
            line_vec = sentence_embedding(sent2vec_model, code)
            
            # Skip if embedding failed
            if line_vec is None:
                continue
            
            line_vec = np.array(line_vec)
            
            # Apply centrality weights
            degree_cen = degree_cen_dict.get(node, 0.5)
            degree_channel.append(degree_cen * line_vec)
            
            closeness_cen = closeness_cen_dict.get(node, 0.5)
            closeness_channel.append(closeness_cen * line_vec)
            
            katz_cen = katz_cen_dict.get(node, 0.5)
            katz_channel.append(katz_cen * line_vec)
        
        # Handle empty channels (no valid code found)
        if not degree_channel:
            # Create a dummy channel with zeros
            dummy_vec = np.zeros(embedding_size)
            degree_channel = [dummy_vec]
            closeness_channel = [dummy_vec]
            katz_channel = [dummy_vec]
        
        return (degree_channel, closeness_channel, katz_channel)
    
    except Exception as e:
        print(f"Error generating image representation: {str(e)}")
        # Return empty channels
        dummy_vec = np.zeros(embedding_size)
        return ([dummy_vec], [dummy_vec], [dummy_vec])