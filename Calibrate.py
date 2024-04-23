import numpy as np
import cv2
def calibrate(tray_img_path):
    """Using a empty tray image (tray in black), and the known size of the tray, 
    this function will return a mask of the tray. This mask will be used to mask 
    the tray in the images to be processed. The mask is a circle with the same size 
    as the tray.

    Args:
        tray_img_path (str): file path to the empty tray image

    Returns:
        plate_mask (np.array): a binary mask of the tray
    """
    img = cv2.imread(tray_img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 100,255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    M=cv2.moments(contour)
    if M['m00']!=0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
    center =(cx,cy)
    min_sum = np.inf
    upper_leftmost = None
    for point in contour:
        x, y = point[0]
        if x+y<min_sum:
            min_sum = x + y
            upper_leftmost = (x, y)

    distance = np.sqrt((upper_leftmost[0] - center[0]) ** 2 + (upper_leftmost[1] - center[1]) ** 2)

    # center to upper most is half of the diagonal of the square
    distance_in_cm = np.sqrt(242)/2
    scaling_factor = distance/distance_in_cm


    # The radius for the mask circle in pixels
    radius_in_pixels = scaling_factor * 4
    
    # Create a mask with a 4.5cm radius circle
    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    cv2_mask = np.uint8(mask)*255
    #mask in binary, so work with binary as well
    cv2.circle(cv2_mask, center, int(radius_in_pixels), 255, -1)  # Draw the circle in white (255)
    #save cv2_mask in the same folder as np.array
    np.save('mask.npy', cv2_mask)
    np.save('center.npy', center)
    np.save('scaling_factor.npy', scaling_factor)
    return cv2_mask, center, scaling_factor

def crop_img_using_mask(mask_path, img_path):
    """Crop the image using the mask. The mask is a circle with the similar size of LB plate.
    Since mask is binary, the image will be converted into grayscale first

    Args:
        mask_path (str): file path to the mask
        img_path (str): file path to the image to be cropped

    Returns:
        cropped_img (np.array): the cropped image
    """
    mask = np.load(mask_path)
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.bitwise_and(gray, gray, mask=mask)
    return img