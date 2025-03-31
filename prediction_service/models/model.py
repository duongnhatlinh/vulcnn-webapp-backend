import os
import tensorflow as tf
from tensorflow import keras

def load_model(model_path):
    """
    Load a pre-trained VulCNN model
    
    Args:
        model_path (str): Path to the model file (.h5)
        
    Returns:
        keras.Model: Loaded model or None if failed
    """
    try:
        print(f"Loading VulCNN model from {model_path}")
        
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return None
        
        # Load Keras model
        model = keras.models.load_model(model_path)
        
        print("VulCNN model loaded successfully")
        return model
    
    except Exception as e:
        print(f"Error loading VulCNN model: {str(e)}")
        return None

def create_vulcnn_model(input_shape, hidden_size=128):
    """
    Create a new VulCNN model architecture
    
    Args:
        input_shape (tuple): Input shape of the model
        hidden_size (int): Size of the hidden layers
        
    Returns:
        keras.Model: Created model
    """
    # Define filter sizes and number of filters
    filter_sizes = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    num_filters = 32
    
    # Input layer
    inputs = keras.layers.Input(shape=input_shape)
    
    # Convolutional layers
    conv_layers = []
    for filter_size in filter_sizes:
        conv = keras.layers.Conv2D(
            filters=num_filters,
            kernel_size=(filter_size, hidden_size),
            activation='relu'
        )(inputs)
        conv = keras.layers.Squeeze(axis=3)(conv)
        conv = keras.layers.MaxPool1D(pool_size=conv.shape[1])(conv)
        conv = keras.layers.Flatten()(conv)
        conv_layers.append(conv)
    
    # Concatenate all convolutional outputs
    concat = keras.layers.Concatenate()(conv_layers)
    
    # Dropout for regularization
    dropout = keras.layers.Dropout(0.1)(concat)
    
    # Output layer
    outputs = keras.layers.Dense(2, activation='softmax')(dropout)
    
    # Create and compile model
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model