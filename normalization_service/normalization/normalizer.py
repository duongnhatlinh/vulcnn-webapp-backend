import re

def normalize_source_code(source_code):
    """
    Normalize C/C++ source code.
    
    This first-pass normalization includes:
    - Removing comments
    - Removing string literals (replacing with empty strings)
    - Removing preprocessor directives (optional)
    - Normalizing whitespace
    
    Args:
        source_code (str): The source code to normalize
        
    Returns:
        str: Normalized source code
    """
    # Remove multi-line comments (/* ... */)
    source_code = re.sub(r'/\*[\s\S]*?\*/', '', source_code)
    
    # Remove single-line comments (// ...)
    source_code = re.sub(r'//.*?$', '', source_code, flags=re.MULTILINE)
    
    # Remove string literals (keep the quotes for syntax validity)
    source_code = re.sub(r'"(\\.|[^"\\])*"', '""', source_code)
    source_code = re.sub(r"'(\\.|[^'\\])*'", "''", source_code)
    
    # Replace tabs with spaces
    source_code = source_code.replace('\t', '    ')
    
    # Normalize line endings
    source_code = source_code.replace('\r\n', '\n')
    
    # Remove trailing whitespace
    source_code = '\n'.join(line.rstrip() for line in source_code.split('\n'))
    
    # Remove multiple empty lines
    source_code = re.sub(r'\n\s*\n\s*\n+', '\n\n', source_code)
    
    return source_code

def normalize_preprocessor(source_code):
    """
    Normalize preprocessor directives.
    This is an optional step that can be applied after basic normalization.
    
    Args:
        source_code (str): The source code to normalize
        
    Returns:
        str: Source code with normalized preprocessor directives
    """
    # Identify and remove #include directives
    source_code = re.sub(r'#include\s*<[^>]*>', '', source_code)
    source_code = re.sub(r'#include\s*"[^"]*"', '', source_code)
    
    # Remove other preprocessor directives
    source_code = re.sub(r'#\s*\w+.*?(?=\n|$)', '', source_code)
    
    # Clean up whitespace after removing directives
    source_code = re.sub(r'\n\s*\n\s*\n+', '\n\n', source_code)
    
    return source_code