import hashlib

with open('synthetic_dataset.csv', 'rb') as f:
    print(hashlib.md5(f.read()).hexdigest())
