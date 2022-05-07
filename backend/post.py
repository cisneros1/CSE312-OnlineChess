from request import Request
import database as db

from generate_response import send_200, send_303
from filepaths import file_paths


def handle_messages(self, received_data: bytes):
    print("---> POST ENTERED")
    
    image_uploaded = False
    message_uploaded = False
    message = ""
    image_location = ""    
    # Parse the entire request and write the bytes to a file
    

    if 'form-data; name="message"' in str(received_data):
        message_uploaded = True
        
    if 'image/jpeg' in str(received_data):
        image_uploaded = True

    if image_uploaded or message_uploaded:
        id = int(db.get_next_chat_id())
        message: str = message_parse(self, received_data)

        if image_uploaded:
            image_location = "/root/user_images/usersimg_by(" + str(id) + ").jpg"
            save_image(self, received_data, image_location)

        username = ("User" + str(id))
        store(id, username, message, image_location)
    else:
        print("There was no image or message found in POST Request")
        
    
    send_303(self, "http://localhost:8080/")
    
    
def store(id: int, username: str, message: str, image_location: str):
    chat_dict = {"_id": id, "username": username,"message": message, "image_location": image_location}
    db.store_message(chat_dict)


# method to get image bytes and save image to file
def save_image(self, received_data: bytes, image_location: str):
    image_as_bytes: bytes = Request(received_data).body
    print(str(image_as_bytes))
    # take second half
    image_as_bytes = image_as_bytes.split(b'Content-Type: image/jpeg\r\n\r\n')[1]

    # if this is present at end take bytes before
    if '-----------' in str(image_as_bytes):
        image_as_bytes = image_as_bytes.split(b'--------')[0]

    # now we have the full body
    with open(image_location, 'wb') as f:
        f.write(image_as_bytes)


def escape_html(received_data: bytes):
    message_list = received_data.split(b'Content-Disposition: form-data; name="message"\r\n\r\n')
    if len(message_list) > 1:
        message = message_list[1]
        print("body: " + str(message))
        message = (message.split(b'\r\n')[0]).decode()
        print("body: " + str(message))
    else:
        message = ""
        
    message = message.replace("&", "&amp;")
    message = message.replace("<", "&lt;")
    message = message.replace(">", "&gt;")
    
    print("Message after escaping: " + message)
    return message


