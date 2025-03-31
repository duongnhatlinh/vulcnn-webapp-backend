from flask import jsonify
from functools import wraps

def api_response(success=True, data=None, message=None, status_code=200, errors=None):
    """
    Standardize API response format
    
    Args:
        success (bool): Whether the request was successful
        data (dict): Response data
        message (str): Response message
        status_code (int): HTTP status code
        errors (dict): Error details
        
    Returns:
        tuple: Flask response with JSON data and status code
    """
    response = {
        'success': success
    }
    
    if data is not None:
        response['data'] = data
    
    if message is not None:
        response['message'] = message
    
    if errors is not None:
        response['errors'] = errors
    
    return jsonify(response), status_code

def paginated_response(items, page, per_page, total):
    """
    Create a paginated response
    
    Args:
        items (list): Items for current page
        page (int): Current page number
        per_page (int): Items per page
        total (int): Total number of items
        
    Returns:
        dict: Pagination data with items
    """
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }

def response_wrapper(f):
    """
    Decorator to wrap API responses in standard format
    
    Args:
        f: Function to wrap
        
    Returns:
        function: Wrapped function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            
            # If result is a tuple, it contains response data and status code
            if isinstance(result, tuple):
                data, status_code = result
            else:
                data = result
                status_code = 200
            
            # Make sure data is serializable
            if not isinstance(data, (dict, list)):
                data = {'result': data}
            
            return api_response(success=True, data=data, status_code=status_code)
        
        except Exception as e:
            # Log the error
            print(f"Error in {f.__name__}: {str(e)}")
            
            # Return error response
            return api_response(
                success=False,
                message=str(e),
                status_code=500
            )
    
    return decorated