from PIL import Image

# Open the PNG image
img = Image.open('utils/updater.png')

# Convert to ICO and save it
img.save('updater.ico', format='ICO')