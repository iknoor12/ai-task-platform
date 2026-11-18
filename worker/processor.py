def process_task(input_text, operation):

    if operation == "uppercase":

        result = input_text.upper()

    elif operation == "lowercase":

        result = input_text.lower()

    elif operation == "reverse":

        result = input_text[::-1]

    elif operation == "word_count":

        result = len(input_text.split())

    else:

        raise ValueError(f"Unsupported operation: {operation}")

    return result
