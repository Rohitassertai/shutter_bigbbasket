# Python program to save a
# video using OpenCV


import cv2


# Create an object to read
# from camera
video = cv2.VideoCapture('rtsp://admin:bb%4012345@192.168.2.9:554/h265/main/ch32/main/av_stream')

# We need to check if camera
# is opened previously or not
if (video.isOpened() == False):
	print("Error reading video file")

# We need to set resolutions.
# so, convert them from float to integer.
frame_width = int(video.get(3))
frame_height = int(video.get(4))

size = (frame_width, frame_height)

# Below VideoWriter object will create
# a frame of above defined The output
# is stored in 'filename.avi' file.
result = cv2.VideoWriter('./filename.mp4',cv2.VideoWriter_fourcc(*'mp4v'),25, size)
frame_nu = 0	
while(True):
	ret, frame = video.read()

	if ret == True:

		# Write the frame into the
		# file 'filename.avi'
		cv2.imwrite(f'./frames/frame_{frame_nu}.jpg',frame)
		result.write(frame)
		frame_nu=frame_nu+1
		print(frame_nu)
		# Display the frame
		# saved in the file
		# cv2.imshow('Frame', frame)

		# Press S on keyboard
		# to stop the process
		if cv2.waitKey(1) & 0xFF == ord('s'):
			break

	# Break the loop
	else:
		break

# When everything done, release
# the video capture and video
# write objects
video.release()
result.release()
	
# Closes all the frames
cv2.destroyAllWindows()

print("The video was successfully saved")
