def compute_single_digest(single_message, last_message):
        return (129 * single_message ^ last_message) % 256

def reverse_single_digest(single_digest, last_message):
    for i in xrange(256):
        if single_digest == compute_single_digest(i, last_message):
            return i

def answer(x):
    last_message = 0
    message = []
    for single_digest in x:
        single_message = reverse_single_digest(single_digest, last_message)
        last_message = single_message
        message.append(single_message)
    return message