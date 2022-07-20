import mysql.connector
import boto3
from config_up import *
from botocore.exceptions import NoCredentialsError

query_last_intrusion_id = 'SELECT id FROM stats_intrusion ORDER BY id DESC LIMIT 1'
query_last_attendance_id = 'SELECT id FROM stats_attendance ORDER BY id DESC LIMIT 1'
query_push_intrusion = 'INSERT INTO stats_intrusion (date, time, intrusion_camera_id, image) ' \
                       'VALUES (%s, %s, %s, %s);'

query_push_attendance = 'INSERT INTO stats_attendance (date, time, attendance_camera_id, image) ' \
                       'VALUES (%s, %s, %s, %s);'

query_push_log = 'INSERT INTO log (event_date, event_time, event_tag, action, log_camera_id, id_reference) ' \
                 'VALUES (%s, %s, %s, %s, %s, %s);'

query_push_vehicle = 'INSERT INTO stats_vehicle (date, vehicle_camera_id, time, image, truck_in_time, truck_out_time, inward_outward, document) ' \
                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'

# query_push_shutter = 'INSERT INTO shutter (date,camera_id, open_time, close_time,image) ' \
#                      'VALUES (%s, %s, %s, %s, %s);'

# query_update_shutter = "UPDATE shutter SET close_time = %s  WHERE camera_id = %s and close_time = '00:00:00' and date = %s;"

query_push_shutter = 'INSERT INTO shutter_new (date_open,camera_id, time_open, time_close,image) ' \
                     'VALUES (%s, %s, %s, %s, %s);'

query_update_shutter = "UPDATE shutter_new SET time_close = %s, date_close = %s WHERE camera_id = %s and time_close = '00:00:00' and date_open = %s;"

query_close_all_shutter = "UPDATE shutter_new SET time_close = %s, date_close = %s WHERE time_close = '00:00:00'"

SHUTTER_OPEN = 'shutter open'
SHUTTER_CLOSE = 'shutter close'


def query_all_data(cursor, query, params=()):
    cursor.execute(query, params)
    print('query all data')
    data = cursor.lastrowid
    return data


def commit_and_close(mydb, cursor):
    mydb.commit()
    if mydb.is_connected():
        cursor.close()
        mydb.close()


def get_mydb_cursor():
    mydb = mysql.connector.connect(
        host=HOST,
        user="admin",
        password="seedworks123",
        port=PORT,
        database=DATABASE
    )
    cursor = mydb.cursor(buffered=True)
    return mydb, cursor


get_url = lambda s3_file_name: f'https://{BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{s3_file_name}'


def upload_to_aws(frame_path, bucket, s3_file_name):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(str(frame_path), bucket, s3_file_name)
        print("Upload Successful")
        return get_url(s3_file_name)
    except FileNotFoundError:
        print("The file was not found")
        return ''
       

    except NoCredentialsError:
        print("Credentials not available")
        return ''

def upload_file_to_s3(file,  st, bucket_name = 'bucket-big-basket',acl="public-read"):
    try:
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)
        Path_of_upload = "shutter/" + st
        print(Path_of_upload)

        s3.put_object(Bucket=bucket_name, Key = Path_of_upload, Body=file,ACL =acl)
        print("Upload Successful")
        return f'https://{BUCKET_NAME}.s3.ap-south-1.amazonaws.com/shutter/{st}'
    except:
        return "Failed"

# print(upload_to_aws("/home/rohit/Pictures/shutter.png",'bucket-big-basket','shutter.png'))
