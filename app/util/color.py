def is_dark(hex_color):
    # Remove the '#' character if present
    hex_color = hex_color.lstrip('#')

    # Convert the hex color to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Calculate the luminance using the formula for relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    # Use a threshold to decide whether to use black or white text
    # The threshold of 0.5 is commonly used, but you can adjust it if necessary
    if luminance > 0.5:
        return True
    else:
        return False