from ultralytics import YOLO
import cv2
import math
import time
import numpy as np
import os
import datetime


# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Find the index of the "Integration2" part in the path
integration2_index = current_file_path.find("Integration2")

# Extract up to the end of "Integration2\\" (note the addition to include the folder name itself)
default_path = current_file_path[:integration2_index] + "Integration2\\"

roi_margin = 1
object_detection_margin = 100
fire_threshold1 = 20
fire_threshold2 = 5
fire_threshold3 = 25



fire_detected = False
keepScanning = True
count = 0
image_counter = 0

prev_value1=0
prev_value2=0
prev_count1=0
prev_count2=0
test1 = False
test2 = False

lower_fire1 = np.array([0, 50, 180])  # Adjust these values based on the specific color characteristics of fire (default)
upper_fire1 = np.array([20, 200, 255])

lower_fire2 = np.array([0, 0, 200])  # Adjust these values based on the specific color characteristics of fire
upper_fire2 = np.array([20, 50, 255])

camera_urls = []
ip_to_node = {}

# # Open the text file and read lines
# with open('camera_urls_and_nodes.txt', 'r') as file:
#     for line in file:
#         # Split the line into URL and node name
#         parts = line.strip("\n").split(",")
#         camera_urls.append(parts[0])
#         ip_to_node[parts[0]]=parts[1]

# print(camera_urls)
# print(ip_to_node)

# Open the text file and read lines
with open('camera_urls_and_nodes.txt', 'r') as file:
    for line in file:
        # Split the line into URL and node name
        parts = line.strip().split(",")
        # Check if the URL is numeric and convert to int if true
        url = parts[0]
        if url.isdigit():
            url = int(url)  # Convert URL to integer if it's numeric
        # Append URL to the list
        camera_urls.append(url)
        # Add URL and node name to the dictionary
        ip_to_node[url] = parts[1]

print(camera_urls)
print(ip_to_node)


# Function to process the bounding box area
def process_roi(roi, confidence, roi_for_object):

    global prev_value1
    global prev_count1
    global prev_value2
    global prev_count2
    global test1
    global test2

     # Add your processing logic here
    roi = cv2.GaussianBlur(roi, (1, 1), 0)
    # Convert the ROI to the HSV color space
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

 

    # Create masks using the inRange function
    mask1 = cv2.inRange(hsv_roi, lower_fire1, upper_fire1)
    mask2 = cv2.inRange(hsv_roi, lower_fire2, upper_fire2)

    # Apply masks to the ROI
    result1 = cv2.bitwise_and(roi, roi, mask=mask1)
    result2 = cv2.bitwise_and(roi, roi, mask=mask2)

    # Calculate the percentage of pixels within the color range
    total_pixels = np.prod(roi.shape[:2])
    color_percentage1 = (cv2.countNonZero(mask1) / total_pixels) * 100
    color_percentage2 = (cv2.countNonZero(mask2) / total_pixels) * 100

    # Verify fire based on color percentage
    if ( (color_percentage1 > fire_threshold1 or color_percentage2 > fire_threshold2) and confidence > fire_threshold3):
        if color_percentage1 > prev_value1:
            prev_value1=color_percentage1
            prev_count1=prev_count1+1
            test1 = True
        if color_percentage2 > prev_value2:
            prev_value2=color_percentage2
            prev_count2=prev_count2+1
            test2 = True
        if  (test1 or test2):
            if prev_count1 > 2 or prev_count2 > 2:
            # if prev_count1 > 5 or prev_count2 > 10:
                print("Fire verified!")
                print("Percentage value 1: ", color_percentage1)
                print("Percentage value 2: ", color_percentage2)
                print("confidence: ", confidence)
                print("prev count: ",prev_count1)
                print("prev count: ",prev_count2)

                # Display the original ROI and the segmented results
                cv2.imshow('Original ROI', roi)
                cv2.imwrite(os.path.join(f'{default_path}images','original_ROI_.jpg'), roi)
                cv2.imshow('Segmented Fire 1', result1)
                #cv2.imwrite(os.path.join(f'{default_path}images','segmented1_ROI_.jpg'),result1)
                cv2.imshow('Segmented Fire 2', result2)
                #cv2.imwrite(os.path.join(f'{default_path}images','segmented2_ROI_.jpg'),result2)
                cv2.imshow('HSV Image', hsv_roi)
                #cv2.imwrite(os.path.join(f'{default_path}images','hsv_ROI_.jpg'),hsv_roi)
                cv2.imshow('Object That Caught Fire', roi_for_object)
                cv2.imwrite(os.path.join(f'{default_path}images','Object_ROI_.jpg'),roi_for_object)

                # Wait for a key press and then close the windows
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                return True  # Return True to indicate successful fire verification
        else:
            return False
        
    else:
        print("Potential false positive.")
        return False  # Return False to indicate false positive

# Initialize YOLO model
model = YOLO('last.pt')
classnames = ['fire']

while keepScanning:
    camera_url = camera_urls[count % len(camera_urls)]
    cap = cv2.VideoCapture(camera_url)

    fps = cap.get(cv2.CAP_PROP_FPS)
    start_time = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.resize(frame, (640, 640))
        result = model(frame, stream=True)

        for info in result:
            boxes = info.boxes
            
            for box in boxes:
                confidence = box.conf[0]
                confidence = math.ceil(confidence * 100)
                Class = int(box.cls[0])
                if confidence > 20 and classnames[Class] == 'fire':
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    original_frame = frame
                    # Draw bounding box on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                    cv2.putText(frame, f'{confidence}%', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Increase the ROI size while ensuring it doesn't go beyond image boundaries 
                    x1 = max(0, x1 - roi_margin)
                    y1 = max(0, y1 - roi_margin)
                    x2 = min(frame.shape[1], x2 + roi_margin)
                    y2 = min(frame.shape[0], y2 + roi_margin)

                    # ROI for object detection of instance segmentation
                    a1 = max(0, x1 - object_detection_margin)
                    b1 = max(0, y1 - object_detection_margin)
                    a2 = min(original_frame.shape[1], x2 + object_detection_margin)
                    b2 = min(original_frame.shape[0], y2 + object_detection_margin)
                    roi_for_object = original_frame[b1:b2, a1:a2]


                    # Extract the region of interest (ROI) from the frame
                    roi = frame[y1:y2, x1:x2]
                    fire_verified = process_roi(roi,confidence,roi_for_object)

                    if fire_verified:
                        fire_detected = True
                        FireCaughtAt = camera_urls[count % len(camera_urls)]
                        test = ip_to_node[FireCaughtAt]
                        print("Fire caught at ", test)
                        
                        f1 = open(f"{default_path}assets\\Safestpath\\fire_room.txt", "w")
                        f1.write(test)
                        f1.close()
                        keepScanning = False
                        break
        cv2.imshow('frame', frame)
        cv2.imwrite(os.path.join(f'{default_path}images','original_frame.jpg'), original_frame)

        if fire_detected:
            f = open("summary.txt", "w")
            f.write("Fire Caught At "+test)
            now = datetime.datetime.now()
            f.write("\nTime Stamp Of Detection "+str(now))
            f.close()
            break

        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:  # Switch cameras every 10 seconds
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            keepScanning = False
            break

    cap.release()
    cv2.destroyAllWindows()

    count += 1




