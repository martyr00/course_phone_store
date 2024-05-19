import os
from datetime import datetime

def get_telephone_image_upload_path(instance, filename):
    telephone_id = instance.telephone_id
    title = instance.title

    upload_path = os.path.join('telephone_images', str(telephone_id), (title + '.png'))
    return f"image/{upload_path}"


def get_user_image_upload_path(instance, filename):
    user_id = instance.user.id

    upload_path = os.path.join('user_images', str(user_id) + '.png', )
    return f"image/{upload_path}"


def write_error_to_file(request, err):
    try:
        with open('log', 'a') as file:
            file.write(f"__________________{request}_________________\n")
            file.write(f"error: {err}")
            file.write(f"time: {datetime.now()}")
            file.write(f"________________________________________\n")
            file.write("\n")
    except Exception as ex:
        print(f"Error with write to file: {ex}")
        print(f"Error request: {err}")


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
