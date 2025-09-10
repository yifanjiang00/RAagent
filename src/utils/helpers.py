def format_output(data):
    """
    Formats the output data for better readability.
    
    Parameters:
    data (dict or list): The data to be formatted.

    Returns:
    str: A formatted string representation of the data.
    """
    if isinstance(data, dict):
        return "\n".join(f"{key}: {value}" for key, value in data.items())
    elif isinstance(data, list):
        return "\n".join(str(item) for item in data)
    else:
        return str(data)