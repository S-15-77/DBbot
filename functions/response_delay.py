import time
def response_delay(result):
    for word in result.split(' '):
        yield word + ' '
        time.sleep(0.05)