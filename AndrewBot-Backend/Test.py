import re
from string import punctuation

def clean_product_name_input_string(input_string):
    # Replace '/' with a space
    # input_string = str(input_string).strip().replace("/", " ")
    print("input_string:", input_string)
    # Replace special characters with space if no leading/trailing spaces around them
    text = re.sub(r'(\S)([!"#$\'()*+,\-./:;<=>?@[\\\]^_`{|}~])(\S)', r'\1 \2 \3', input_string)
    print("text1:", text)
    # Remove special characters if they have leading or trailing spaces
    text = re.sub(r'(\s[!"#$\'()*+,\-./:;<=>?@[\\\]^_`{|}~]\s)', '', text)
    print("text2:", text)
    # Replace any remaining special characters with space
    text = re.sub(r'[!"#$\'()*+,\-./:;<=>?@[\\\]^_`{|}~]', ' ', text)
    print("text3:", text)
    # Remove extra spaces
    cleaned_string = re.sub(r'\s+', ' ', text).strip()
    print("cleaned_string1:", cleaned_string)
    # Remove all characters except letters, digits, spaces, '&', and '%'
    # cleaned_string = re.sub(r"[^a-zA-Z0-9&%\s]", "", input_string)
    # print("punctuation:", punctuation)
    return cleaned_string

import re

def clean_special_characters(text):
    # Remove special characters if they have leading spaces
    # text = re.sub(r'\s[!"#$\'()*+,\-./:;<=>?@[\\\]^_`{|}~]', ' ', text)
    # print("text1:", text)
    # # Remove special characters if they have trailing spaces
    # text = re.sub(r'[!"#$\'()*+,\-./:;<=>?@[\\\]^_`{|}~]\s', ' ', text)
    # print("text2:", text)
    text = re.sub(r"[^a-zA-Z0-9&%\s]", " ", text)
    print("text1:", text)
    # Remove extra spaces that might have been introduced
    text = re.sub(r'\s+', ' ', text).strip()
    print("text3:", text)
    return text

# Example usage
text = "Poha, Sabudana & Murmura"
cleaned_text = clean_special_characters(text)
print(cleaned_text)

# input_string = "1 To 1  Baking Flour - Gluten Free"
# print("cleaned string2:", clean_product_name_input_string(input_string))