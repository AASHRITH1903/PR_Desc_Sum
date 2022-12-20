import json


dataset = json.load(open('dataset_filtered.json'))

keys = list(dataset.keys())

print(f"Size of the filtered dataset: {len(keys)}.")
