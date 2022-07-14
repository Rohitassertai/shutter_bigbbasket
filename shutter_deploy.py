import cv2 
import time
from datetime import datetime
# from utils_up import *
from utils_up import query_update_shutter,query_push_shutter, query_all_data, get_mydb_cursor, commit_and_close,upload_file_to_s3
from config_up import BUCKET_NAME, SECONDS_GAP_BEFORE_INTRUSION, FPS_INTRUSION
import numpy as np

def start_input(link):
	capOpened = False
	while True:
		
		if capOpened is False:
			cap,capOpened,fps = init_capture(link)
		else:
			frame,capOpened = update_frame(cap,capOpened,fps)

			return frame

def init_capture(streamLink):
	print('initalizing',streamLink)
	cap = cv2.VideoCapture(streamLink)
	capOpened = cap.isOpened()
	cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
	# fps = max(cap.get(cv2.CAP_PROP_FPS)%100, 0) or 30.0
	# frames = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 0) or float('inf')
	return cap,capOpened

def update_frame(cap,capOpened,offset=0):
	# print('updating')
	while capOpened:
		ret, frame = cap.read()
		if ret is False:
			capOpened = False

		return frame,capOpened

def read(frame):
	try:
		frame = frame.copy()
	except:
		frame = np.zeros(shape=(640,640,3))
	
	return frame


def insert_data_shutter(frame_date, frame_time,close_time, camera_id, image_url):
    mydb, cursor = get_mydb_cursor()
    params = (frame_date, camera_id,frame_time, close_time ,image_url)
    _ = query_all_data(cursor, query_push_shutter, params)
    mydb.commit()
    if mydb.is_connected():
        cursor.close()
        mydb.close()

def update_shutter_closed(close_time,camera_id,date):
	mydb, cursor = get_mydb_cursor()
	params = (close_time,camera_id,date)
	_ = query_all_data(cursor, query_update_shutter, params)
	mydb.commit()
	if mydb.is_connected():
	    cursor.close()
	    mydb.close()

	return 'updating close time'


def display():

	
	template = cv2.imread('./template.jpg',0)
	w, h = template.shape[::-1]
	data = []
	streamLinks = ['rtsp://admin:bb%4012345@192.168.2.9:554/h265/main/ch32/main/av_stream']
				   # '/home/rohit/Videos/test_shutter']
				   # '/home/rohit/Videos/test_shutter']
				   # '/home/rohit/Videos/test_shutter',
				   # '/home/rohit/Videos/test_shutter',
				   # '/home/rohit/Videos/test_shutter',
				   # '/home/rohit/Videos/test_shutter']
	upload_check = []
	time_limit = []
	last_upload = []
	shutter_closed = []
	for i in range(len(streamLinks)):
		upload_check.append(False)
		time_limit.append(0)
		last_upload.append(float('-inf'))
		shutter_closed.append(0)
	print(upload_check)
	# streamLinks = ["rtsp://admin:Adani%40123@172.16.0.49:554/Streaming/Channels/601/",
	# 			   "rtsp://admin:Adani%40123@172.16.0.49:554/Streaming/Channels/201/",
	# 			   "rtsp://admin:Adani%40123@172.16.0.49:554/Streaming/Channels/401/",
	# 			   "rtsp://admin:Adani%40123@172.16.0.49:554/Streaming/Channels/501/"]
	

	for i in streamLinks:
		cap,capOpened=init_capture(i)
		# print(i,frames)
		list = [cap,capOpened]
		data.append(list)

	print(data)
	# result = cv2.VideoWriter('shutter.avi', 
	#                          cv2.VideoWriter_fourcc(*'MJPG'),
	#                          25, (1920,1080))
	while True:
		
		final = []
		for i in data:
			index_var = data.index(i)
			
			if i[1]:
				
				try:	
					frame,capOpened = update_frame(i[0],i[1])
					
					frame_copy = frame.copy()
					frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
					frame = frame[114:538,685:1146]
					res = cv2.matchTemplate(frame,template,cv2.TM_CCOEFF_NORMED)
					min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
					top_left = max_loc
					top_left = (686 + top_left[0], 114 + top_left[1])
					bottom_right = (top_left[0] + w, top_left[1] + h)
					# print(top_left[1])
					cv2.rectangle(frame_copy,top_left, bottom_right, 255, 2)
					if top_left[1] > 114 + 45:
						cv2.rectangle(frame_copy,top_left, bottom_right, 255, 2)
						shutter_closed[index_var] +=1
						print(f'closed {index_var}',shutter_closed[index_var])
						if upload_check[index_var] == True and shutter_closed[index_var] > 500:

							now = datetime.now()
							time_1 = now.strftime("%H%M%S")
							print(update_shutter_closed(time_1,f'1_{index_var}',now.strftime("%Y-%m-%d")))
							upload_check[index_var] = False
					else:
						shutter_closed[index_var] = 0
						font = cv2.FONT_HERSHEY_SIMPLEX
						org = (50, 50)
						fontScale = 1
						color = (0, 0, 255)
						thickness = 2
						cv2.putText(frame_copy, 'Door Open', org, font, 
						           fontScale, color, thickness, cv2.LINE_AA)
						# image_string = cv2.imencode('shutter1.jpg', frame_copy)[1].tostring()
						# cv2.imwrite('shutter1.jpg',frame_copy)
						if upload_check[index_var] == False:
							now = datetime.now()
							time_1 = now.strftime("%H%M%S")
							date = now.strftime("%Y%m%d")
							im_id = str(str(date)+str(time_1))
							frame_to_upload = cv2.resize(frame_copy, (900, 600), cv2.INTER_CUBIC)
							img_encode = cv2.imencode('.jpg', frame_to_upload)[1]
							data_encode = np.array(img_encode)
							str_encode = data_encode.tostring()
							# url = upload_to_aws('/home/rohit/yolov5 latest/yolov5/shutter1.jpg','bucket-big-basket','shutter1.jpg')
							url = upload_file_to_s3(str_encode,im_id+'.jpg')
							print(url)
							upload_check[index_var] =True
							insert_data_shutter(now.strftime("%Y-%m-%d"),now.strftime("%H:%M:%S"),'00:00:00',f'1_{index_var}',str(url))
					
					# result.write(frame_copy)
					frame_copy = cv2.resize(frame_copy,(1600,900),cv2.INTER_AREA)
# 					cv2.imshow(str(index_var),frame_copy)
					
					# print(streamLinks[index_var])
				except:
					print('#'*50)
					print('#'*50)
					print('#'*50)
					print('Nonetype Error',index_var)
					print('#'*50)
					print('#'*50)
					index_var = data.index(i)
					print(index_var)
					cap,capOpened=init_capture(streamLinks[index_var])
					data[index_var] = [cap,capOpened]
					print('fixed',index_var)
		# for i in final:
		# 	ind = final.index(i)

		if cv2.waitKey(1) & 0xFF == ord('q'):
		    # result.release()

		    break

# now = datetime.now()
# time_1 = now.strftime("%H%M%S")
# date = now.strftime("%Y%m%d")
# im_id = str(str(date)+str(time_1))
# frame_copy = cv2.imread('fire.jpg')
# frame_to_upload = cv2.resize(frame_copy, (900, 600), cv2.INTER_CUBIC)
# img_encode = cv2.imencode('.jpg', frame_to_upload)[1]
# data_encode = np.array(img_encode)
# str_encode = data_encode.tostring()
# # url = upload_to_aws('/home/rohit/yolov5 latest/yolov5/shutter1.jpg','bucket-big-basket','shutter1.jpg')
# url = upload_file_to_s3(str_encode,im_id+'.jpg')
# print(url)
display()
