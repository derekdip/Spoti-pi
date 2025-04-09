import cv2
from browserInterface import logIn, search, endSession
from camera import  scan_barcodes
import time
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz
from collections import Counter
from textManipulation import get_most_representative_text, get_similarity, filter_outliers
spell = SpellChecker()
def correct_text(text):
    # Replace '5' with 's', '1' with 'l', and '!' with 'l'
    text = text.replace('5', 's')
    text = text.replace('1', 'li')
    text = text.replace('!', 'li')
    text = text.replace('9', 'g')
    text = text.replace('0', 'o')
    return text


def run_for_5_seconds(cap):
    start_time = time.time()  # Get the current time
    while time.time() - start_time < 7:  # Run the loop until 5 seconds have passed
        scannedText = scan_barcodes(cap)
        scannedText = scannedText.replace('\n', ' ')
        text = correct_text(scannedText)
        words = text.split()
        corrected_words = [spell.correction(word) for word in words]
        corrected_text = " ".join(corrected_words)

        samples.append(corrected_text)
        # Your loop logic here (e.g., print or perform any task)
        print("Running...")  # Example task in the loop
    # Filter out outliers
    filtered_samples = [sample for sample in samples if sample.strip() != ""]
    print(filtered_samples)
    filtered_texts = filter_outliers(filtered_samples,threshold=50)

    # Get the most common (average-like) text
    average_text = get_most_representative_text(filtered_texts)
    print(average_text)
    print("5 seconds have passed!")
    return average_text

#search("hello my name is 637 hi] ][] jm \n jlkj j")
logIn()
#start_camera()
cap = cv2.VideoCapture(0)
while True:
    samples = []
    #user_input = input("Enter a number (enter 0 to exit): ")
    
    # # Check if the user entered '0'
    # if user_input == '0':
    #     print("Exiting the loop.")
    #     break
    result_from_scans =run_for_5_seconds(cap)
    if(result_from_scans=="" or result_from_scans==None):
        continue
    search(result_from_scans)
    time.sleep(5)
    
    # Otherwise, process the input (you can replace this with your desired logic)
    #print(f"You entered: {user_input}")



print(samples)
