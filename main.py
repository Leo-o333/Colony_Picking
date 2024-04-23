# from opts import get_opts
import Calibrate
import numpy as np
import cv2
from opts import get_opts
import random
import matplotlib.pyplot as plt
import csv
def calculate_intensity(img):
    """Calculate the intensity of the image. The intensity is the sum of the pixel values in the image.

    Args:
        img (np.array): the image to be processed

    Returns:
        intensity (float): the intensity of the image
    """
    pix_intensity = []
    for x in range(len(img)):
        for y in range(len(img[0])):
            if img[x][y] != 0:
                pix_intensity.append(img[x][y])
            
    std = np.std(pix_intensity)
    mean = np.mean(pix_intensity)
    return mean+2*std

def find_contours(img):
    """Find the contours in the cropped image

    Args:
        img (np.array): the cropped image to be processed

    Returns:
        contours (list): a list of contours
    """
    blr = cv2.medianBlur(img, 15)
    blur = cv2.GaussianBlur(blr, (5, 5), 0)
    plt.imsave('sanity_check.jpg', blur, cmap='gray')
    
    lower = calculate_intensity(blur)

    _, binary = cv2.threshold(blur, lower, 255,cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    filtered_contours = []
    contour_center=[]
    for contour in contours:
        # Calculate contour area and bounding rectangle
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate aspect ratio (width / height)
        aspect_ratio = float(w / h)
        actual_area = area/(w*h)
    
    
        # Filter out thin and long contours, you can adjust the thresholds
        if aspect_ratio >0.8 and actual_area>0.5 and area > 200 and area <=40000:
            # Example thresholds
            center=(x+w//2,y+h//2)
            point = [[x+w//2,y+h//2]]
            if point not in contour:
               
                temp = random.choice(contour)
                center = (temp[0][0],temp[0][1])

            contour_center.append(center)
            filtered_contours.append(contour)
    areas = [cv2.contourArea(contour) for contour in filtered_contours]

# Step 2: Create a dictionary to store contour areas and their indices
    area_dict = {i: area for i, area in enumerate(areas)}

# Step 3: Sort the dictionary based on the areas
    sorted_areas = sorted(area_dict.items(), key=lambda x: x[1], reverse=True)

# Step 4: Sort the points based on the areas of the contours
    sorted_points = [contour_center[index] for index, _ in sorted_areas]

    # filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > area_threshold and cv2.contourArea(cnt) < top_threshold]  # Change '>' to '<' to keep smaller areas
    # Create an empty image with the same dimensions as the original
    # new_image = np.zeros_like(binary)
    

    # # Draw the filtered contours onto the new image
    # cv2.drawContours(new_image, filtered_contours, -1, (255), thickness=cv2.FILLED)
    # plt.imshow(img)

    # for center in contour_center:
    #     plt.scatter(center[0],center[1],c='r')
    # plt.show()
    
    if len(sorted_points)>4:
        points = sorted_points[:4]
        
        
        
    return filtered_contours, points

def main():
    args = get_opts()
    if args.Calibrate:
        mask,tray_center, scaling_factor = Calibrate.calibrate("pure_black.jpg")
        
    
    img1=Calibrate.crop_img_using_mask('mask.npy','p1.jpg')
    contours, points_in_pixel = find_contours(img1)
    #actual location of the bacteria colonies
    plate_center = (63.88, 42.5)
    center = np.load('center.npy')
    scaling_factor = np.load('scaling_factor.npy')
    
    #scaling factor is distance in pixel/distance in cm
    #scaling factor for distance in mm is scal/10
    scale_in_mm = scaling_factor/10
    points_on_960=[]
    for points in points_in_pixel:
        #calculate the distance in mm
        x = (points[0]-center[0])/scale_in_mm
        y = (points[1]-center[1])/scale_in_mm
        
        points_on_960.append((x,y))

    #save points information into csv
    headers = ['X','Y']
    with open('points.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for point in points_on_960:
            writer.writerow(point)
       
if __name__ == '__main__':
    main()