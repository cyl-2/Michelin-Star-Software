import random
import string

def get_random_password():
    random_char = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase) 
    password += random.choice(string.ascii_lowercase) + random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)

    for i in range(2):
        password += random.choice(random_char)

    password_list = list(password)
    # shuffle all characters to make it even more random
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password
