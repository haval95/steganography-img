def text_to_binary(text):
    binary_code = "".join(format(ord(char), "08b") for char in text)
    return binary_code


def binary_to_text(biarny):
    return "".join(chr(int(biarny[i : i + 8], 2)) for i in range(0, len(biarny), 8))


# Check if the message can be embedded in the image
def check_fitness(message, pixels):
    message_length = len(message)
    if message_length > pixels:
        raise ValueError("Message is too large to be embedded in the image.")
