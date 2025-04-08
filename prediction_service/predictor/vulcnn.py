import numpy as np
import torch

class VulCNN:
    """
    VulCNN vulnerability predictor
    
    This class wraps the VulCNN model and provides methods to predict
    vulnerabilities from image representations
    """
    
    def __init__(self, model):
        """
        Initialize the predictor with a trained model
        
        Args:
            model: Trained VulCNN model
        """
        self.model = model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def preprocess_image(self, image_data, max_len=100, hidden_size=128):
        """
        Preprocess image data for input to the model using the same
        method as in the original VulCNN implementation
        
        Args:
            image_data: Tuple of (degree_channel, closeness_channel, katz_channel)
            max_len: Maximum sequence length
            hidden_size: Size of embedding vectors
            
        Returns:
            torch.Tensor: Preprocessed image representation
        """
        # Unpack channels
        degree_channel, closeness_channel, katz_channel = image_data
        
        # Initialize empty array
        vectors = np.zeros(shape=(3, max_len, hidden_size))
        
        # Fill channels
        for j, channel in enumerate([degree_channel, closeness_channel, katz_channel]):
            for i in range(min(len(channel), max_len)):
                vectors[j][i] = channel[i]
        
        # Convert to torch tensor
        tensor = torch.tensor(vectors, dtype=torch.float32).unsqueeze(0).to(self.device)
        return tensor
    
    def predict(self, image_data):
        """
        Predict vulnerability from image representation
        
        Args:
            image_data: Tuple of (degree_channel, closeness_channel, katz_channel)
            
        Returns:
            dict: Prediction result
        """
        if not self.model:
            return {'error': 'Model not loaded'}
        
        # Preprocess image
        processed_image = self.preprocess_image(image_data)
        
        # Make prediction
        with torch.no_grad():
            outputs, _ = self.model(processed_image)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
        
        # Get class probabilities
        prob_not_vulnerable = probabilities[0][0].item()
        prob_vulnerable = probabilities[0][1].item()
        
        # Determine if vulnerable
        is_vulnerable = prob_vulnerable > 0.5
        
        # Prepare result
        result = {
            'is_vulnerable': bool(is_vulnerable),
            'confidence': float(max(prob_vulnerable, prob_not_vulnerable)),
            'vulnerability_probability': float(prob_vulnerable),
            'safe_probability': float(prob_not_vulnerable)
        }
        
        # Add vulnerability type if detected
        if is_vulnerable:
            # In a real implementation, you would have more sophisticated
            # type detection here, possibly using additional models or analysis
            # This is similar to the original code's placeholder implementation
            if prob_vulnerable > 0.9:
                result['vulnerability_type'] = 'buffer_overflow'
            elif prob_vulnerable > 0.8:
                result['vulnerability_type'] = 'format_string'
            elif prob_vulnerable > 0.7:
                result['vulnerability_type'] = 'integer_overflow'
            else:
                result['vulnerability_type'] = 'resource_leak'
            
            # Add function_name and line_number placeholders
            # In a real implementation, this would come from the PDG analysis
            result['function_name'] = 'unknown'
            result['line_number'] = 0
        
        return result