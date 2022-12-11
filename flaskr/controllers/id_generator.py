import string, random

# This generates a unique name for our files so we don't have duplicates inside the blob storage.

def id_generator():
    chars = string.ascii_letters 
    size = 12
    return ''.join(random.choice(chars) for x in range(size))



