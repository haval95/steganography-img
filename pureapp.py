import numpy as np
from PIL import Image

MARKER = "1010101010101010"  # Reserved pattern as the marker


def text_to_binary(text):
    return "".join(format(ord(char), "08b") for char in text)


def binary_to_text(biarny):
    return "".join(chr(int(biarny[i : i + 8], 2)) for i in range(0, len(biarny), 8))


# Check if the message can be embedded in the image
def check_fitness(message, pixels):
    message_length = len(message)
    if message_length > pixels:
        raise ValueError("Message is too large to be embedded in the image.")


def encode_image(cover_image_path, secret_message, stego_image_path):
    # IMG
    cover_image = Image.open(cover_image_path)
    width, height = cover_image.size

    binary_message = text_to_binary(secret_message)

    # END
    binary_message += MARKER

    # CHECK
    check_fitness(binary_message, width * height * 3)

    # Convert the cover image to a NumPy array for faster processing
    img_array = np.array(cover_image)

    # Flatten the cover image array to a 1D array
    img_flat = img_array.flatten()

    # msg to LSB
    for inedx, bit in enumerate(binary_message):
        bit_value = int(bit)
        # pixel
        pixel_value = img_flat[inedx]

        # Change last bit
        modified_value = (pixel_value & 0xFE) | bit_value
        # reset the pixel
        img_flat[inedx] = modified_value

    # changing back to a 2 d img
    stego_array = img_flat.reshape(height, width, -1)

    # Create the stego image from the NumPy array
    stego_image = Image.fromarray(stego_array.astype("uint8"))

    # Save the stego image
    stego_image.save(stego_image_path)
    print("Message embedded successfully.")


def decode_image(stego_image_path):
    # Open the stego image
    stego_image = Image.open(stego_image_path)

    # Convert the stego image to a NumPy array for faster processing
    stego_array = np.array(stego_image)

    # Flatten the stego image array to a 1D array
    stego_flat = stego_array.flatten()

    # Extract the LSBs from the image data until the marker is found
    binary_message = ""
    for i, pixel in enumerate(stego_flat):
        # Extract the LSB of the pixel value
        bit = str(pixel & 1)

        # Append the bit to the binary message
        binary_message += bit

        # Check if the marker is found
        if binary_message.endswith(MARKER):
            # Remove the marker from the binary message
            binary_message = binary_message[: -len(MARKER)]
            break

    # Convert binary message to characters
    message = binary_to_text(binary_message)

    return message


# Example usage:
cover_image_path = "nature.png"
secret_message = "HELLO MY NAMES IS HAVAL AND THIS IS MY CODE HELLO MY NAMES IS HAVAL AND THIS IS MY CODEHELLO MY NAMES IS HAVAL AND THIS IS MY CODEHELLO MY NAMES IS HAVAL AND THIS IS MY CODEHELLO MY NAMES IS HAVAL AND THIS IS MY CODE HELLO MY NAMES IS HAVAL AND THIS IS MY CODE HELLO MY NAMES IS HAVAL AND THIS IS MY CODE HELLO MY NAMES IS HAVAL AND THIS IS MY CODEHELLO MY NAMES IS HAVAL AND THIS IS MY CODEHELLO MY NAMES IS HAVAL AND THIS IS MY CODEHELLO MY NAMES IS HAVAL AND THIS IS MY CODE"
stego_image_path = "stego_image.png"

# Encode the secret message into the cover image
encode_image(cover_image_path, secret_message, stego_image_path)

# Decode the secret message from the stego image
decoded_message = decode_image(stego_image_path)
print("Decoded message:", decoded_message)
