import pandas as pd
import json

# Read the JSON file
df = pd.read_json('footway_cs_dataset.json')

# Alternative if you have the JSON as a string or need to load from file:
# with open('your_file.json', 'r') as file:
#     data = json.load(file)
#     df = pd.DataFrame(data)

# Get unique values from category column
unique_categories = df['category'].unique()

print("Unique categories:")
print(unique_categories)

# You can also get the count of unique categories
print(f"\nNumber of unique categories: {len(unique_categories)}")

# If you want to see the unique categories as a list
unique_categories_list = df['category'].unique().tolist()
print(f"\nUnique categories as list: {unique_categories_list}")