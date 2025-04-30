from PIL import Image

# Open the PNG image
img = Image.open('utils/new_icon.png')

# Convert to ICO and save it
img.save('favicon.ico', format='ICO')