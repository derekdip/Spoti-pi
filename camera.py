import cv2
import numpy as np
import pytesseract
from pyzbar.pyzbar import decode
from time import sleep

def get_average_bright_color(frame, container_points, brightness_threshold=180):
    # Calculate the bounding box of the container
    min_x = min(container_points, key=lambda point: point[0])[0]
    max_x = max(container_points, key=lambda point: point[0])[0]
    min_y = min(container_points, key=lambda point: point[1])[1]
    max_y = max(container_points, key=lambda point: point[1])[1]

    # Ensure the bounding box doesn't extend beyond the image dimensions
    min_x = max(min_x, 0)
    max_x = min(max_x, frame.shape[1])
    min_y = max(min_y, 0)
    max_y = min(max_y, frame.shape[0])

    # Extract the container area to sample the color
    container_area = frame[min_y:max_y, min_x:max_x]

    # Convert to grayscale to assess brightness
    try:
        gray_container_area = cv2.cvtColor(container_area, cv2.COLOR_BGR2GRAY)

        # Create a mask where the brightness is above the threshold
        bright_mask = gray_container_area > brightness_threshold

        # Apply the mask to the container area to keep only the bright regions
        bright_regions = container_area[bright_mask]

        if bright_regions.size == 0:
            return np.array([0, 0, 0])  # Return black if no bright regions found

        # Calculate the average color of the bright regions
        avg_bright_color = np.mean(bright_regions, axis=0).astype(int)
        return avg_bright_color
    except:
        return []


def dfs_find_container(frame, start_x, start_y, visited):
    """
    Use DFS to find the enclosing container around the QR code.
    This function searches for a white container on a darker background.
    """
    # Stack for DFS
    stack = [(start_x, start_y)]
    container_points = []

    while stack:
        x, y = stack.pop()

        if (x, y) in visited:
            continue

        # Mark the point as visited
        visited.add((x, y))

        # Add point to the container points list
        container_points.append((x, y))

        # Explore 4 directions (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy

            # Check if the next point is within the image and part of the white container (on dark background)
            if 0 <= nx < frame.shape[1] and 0 <= ny < frame.shape[0]:
                # If the pixel is white (or close to white) in grayscale
                if frame[ny, nx] > 200:  # 200 threshold to detect "white" regions
                    stack.append((nx, ny))

    return container_points

def scan_barcodes(cap:cv2.VideoCapture):

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        barcodes = decode(frame)

        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            x, y, w, h = barcode.rect.left, barcode.rect.top, barcode.rect.width, barcode.rect.height

            # Mask out the QR code area by making it white
            # frame[y:y + h, x:x + w] = 255  # Set the QR code area to white

            # Convert to grayscale for thresholding
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply adaptive thresholding (you can adjust blockSize and C for fine-tuning)
            _, thresholded = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

            # DFS to find the enclosing white container (start from a container area near the QR code)
            visited = set()
            container_points = dfs_find_container(thresholded, x, y, visited)

            # Find the bounding box of the container from the container points
            if container_points:
                min_x = min(container_points, key=lambda point: point[0])[0]
                max_x = max(container_points, key=lambda point: point[0])[0]
                min_y = min(container_points, key=lambda point: point[1])[1]
                max_y = max(container_points, key=lambda point: point[1])[1]

                # Ensure the bounding box doesn't extend beyond the image dimensions
                min_x = max(min_x, 0)
                max_x = min(max_x, frame.shape[1])
                min_y = max(min_y, 0)
                max_y = min(max_y, frame.shape[0])

                # Draw a rectangle around the enclosing white container
                #cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
                average_bight_color = get_average_bright_color(frame,container_points)
                if(len(average_bight_color)==0):
                    continue
                frame[y:y + h, x:x + w]= average_bight_color
                # Crop the container for OCR (everything inside the container)
                container = frame[min_y:max_y, min_x:max_x]

                # If the container is empty, skip the OCR step
                if container.size == 0:
                    print("Error: Container is empty.")
                    continue
                
                height, width = container.shape[:2]
                new_width = 1000  # Set a target width
                aspect_ratio = width / float(height)
                new_height = int(new_width / aspect_ratio)

                # Resize the image while maintaining the aspect ratio
                resized_img = cv2.resize(container, (new_width, new_height))
                # Optionally apply preprocessing techniques like thresholding
                gray_container = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
                gray_container = cv2.fastNlMeansDenoising(gray_container, None, 30, 7, 21)
                cv2.imwrite('grayscale_container.jpg', gray_container)

                thresh = cv2.adaptiveThreshold(gray_container, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV, 11, 2)
                cv2.imwrite('thresh.jpg', thresh)

                # Perform OCR on the container area
                text = pytesseract.image_to_string(thresh, config='--psm 6 --psm 3')
                print("-start-")
                print(text)
                print("-end-")
                # Display the OCR result on the frame
                cv2.putText(frame, f"OCR Text: {text}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                # cap.release()
                # cv2.destroyAllWindows()
                return text

        # Display the frame with barcode and OCR text
        cv2.imshow("Barcode Scanner with OCR", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # cap.release()
    # cv2.destroyAllWindows()
