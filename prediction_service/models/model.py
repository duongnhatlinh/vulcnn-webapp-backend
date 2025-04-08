import os
import torch
import numpy as np
from torch import nn
import torch.nn.functional as F

class TextCNN(nn.Module):
    """
    VulCNN model architecture as specified in the original implementation
    """
    def __init__(self, hidden_size=128):
        super(TextCNN, self).__init__()
        self.filter_sizes = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)           
        self.num_filters = 32                                        
        classifier_dropout = 0.1
        self.convs = nn.ModuleList(
            [nn.Conv2d(3, self.num_filters, (k, hidden_size)) for k in self.filter_sizes])
        self.dropout = nn.Dropout(classifier_dropout)
        num_classes = 2
        self.fc = nn.Linear(self.num_filters * len(self.filter_sizes), num_classes)

    def conv_and_pool(self, x, conv):
        x = F.relu(conv(x)).squeeze(3)
        x = F.max_pool1d(x, x.size(2)).squeeze(2)
        return x

    def forward(self, x):
        out = x.float()
        # out = out.unsqueeze(1)
        hidden_state = torch.cat([self.conv_and_pool(out, conv) for conv in self.convs], 1)
        out = self.dropout(hidden_state)
        out = self.fc(out)
        return out, hidden_state

def load_model(model_path, hidden_size=128):
    """
    Load a pre-trained VulCNN model
    
    Args:
        model_path (str): Path to the model file (.pt)
        hidden_size (int): Size of embedding vectors
        
    Returns:
        TextCNN: Loaded model or None if failed
    """
    try:
        print(f"Loading VulCNN model from {model_path}")
        print(os.getcwd())

        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return None
        
        # Initialize model
        model = TextCNN(hidden_size=hidden_size)
        
        # Load weights
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.to(device)
        model.eval()
        
        print("VulCNN model loaded successfully")
        return model
    
    except Exception as e:
        print(f"Error loading VulCNN model: {str(e)}")
        return None