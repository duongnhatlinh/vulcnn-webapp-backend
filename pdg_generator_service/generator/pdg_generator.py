import networkx as nx
import os
import json

def generate_pdg_from_file(joern_data, output_path):
    """
    Generate a Program Dependency Graph (PDG) from Joern analysis data
    
    Args:
        joern_data (dict): Joern analysis result
        output_path (str): Where to save the PDG
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not joern_data:
            return False
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Combine PDGs from all methods
        combined_pdg = nx.DiGraph()
        
        for method_data in joern_data:
            method_name = method_data[0]
            nodes = method_data[1]
            edges = method_data[2]
            
            # Add nodes with attributes
            for node in nodes:
                node_id = node.get('id') or node.get('_id')
                if not node_id:
                    continue
                
                # Extract code if available
                code = node.get('code', '')
                lineNumber = node.get('lineNumber', -1)
                
                # Add node with attributes
                combined_pdg.add_node(
                    str(node_id),
                    label=f"{method_name}:{lineNumber}",
                    code=code,
                    method=method_name,
                    line=lineNumber
                )
            
            # Add edges
            for edge in edges:
                src = edge.get('outNode') or edge.get('_outNode')
                dst = edge.get('inNode') or edge.get('_inNode')
                if not src or not dst:
                    continue
                
                edge_type = edge.get('edgeType', 'UNKNOWN')
                combined_pdg.add_edge(str(src), str(dst), type=edge_type)
        
        # Write PDG to DOT file
        nx.drawing.nx_pydot.write_dot(combined_pdg, output_path)
        
        return True
    
    except Exception as e:
        print(f"Error generating PDG: {str(e)}")
        return False