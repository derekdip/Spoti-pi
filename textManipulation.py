from fuzzywuzzy import fuzz
from collections import Counter

# Function to get similarity score
def get_similarity(str1, str2):
    return fuzz.ratio(str1, str2)

# Function to filter out outliers based on similarity
def filter_outliers(text_list, threshold=70):
    similar_texts = []
    for i in range(len(text_list)):
        similar_count = 0
        for j in range(len(text_list)):
            if i != j and get_similarity(text_list[i], text_list[j]) >= threshold:
                similar_count += 1
        # If text is similar to enough others (e.g., 50% similarity), it's not an outlier
        if similar_count >= len(text_list) // 2:  # 50% similarity
            similar_texts.append(text_list[i])
    return similar_texts

# Function to find the most representative text (average-like representation)
def get_most_representative_text(filtered_texts):
    if not filtered_texts:
        return None  # or return a default value like "No similar texts found"

    # Calculate the similarity score of each text to every other text
    similarity_scores = []
    for i in range(len(filtered_texts)):
        total_similarity = 0
        for j in range(len(filtered_texts)):
            if i != j:
                total_similarity += get_similarity(filtered_texts[i], filtered_texts[j])
        similarity_scores.append((filtered_texts[i], total_similarity))

    # Sort by total similarity score, and return the text with the highest score
    similarity_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by the second element (total similarity score)
    return similarity_scores[0][0]  # Return the text with the highest total similarity score

# Example usage
# samples = ["hello world", "hi there", "hello there", "greetings", "hello world!", "good morning"]
# filtered_samples = filter_outliers(samples, threshold=50)
# most_representative_text = get_most_representative_text(filtered_samples)

# print(f"The most representative text: {most_representative_text}")
