import base64

with open('cats.jpg', 'rb') as pic:
    pic_encoded = base64.b64encode(pic.read())
    print(type(pic_encoded))
    print(pic_encoded)



    with open('cats_rebuild.jpg', 'wb') as rebuild:
        image = base64.b64decode(pic_encoded)
        rebuild.write(image)




