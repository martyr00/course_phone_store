import os
from datetime import datetime, timedelta


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


def get_last_month():
    datetime_now = datetime.now()
    year = datetime_now.year
    month = datetime_now.month - 1
    if month == 0:
        year -= 1
        month = 12
    day = datetime_now.day

    new_datetime = datetime(year, month, day).strftime('%Y-%m-%d')
    return new_datetime

def get_dates_with_null_values(result, start_date, end_date):
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    all_dates = [start_date_obj + timedelta(days=x) for x in range((end_date_obj - start_date_obj).days + 1)]

    # Create a dictionary with all dates initialized to null
    result_dict = {date.strftime('%Y-%m-%d'): None for date in all_dates}

    # Update dictionary with values from the query result
    for entry in result:
        result_dict[entry['date'].strftime('%Y-%m-%d')] = entry['value']

    # Convert the dictionary back to the desired list format
    final_result = [{'date': date, 'value': value} for date, value in result_dict.items()]

    return final_result