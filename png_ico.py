from PIL import Image

# Open the PNG image
img = Image.open('tasker.png')

# Convert to ICO and save it
img.save('tasker.ico', format='ICO')