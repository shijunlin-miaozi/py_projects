'''
- 2 methods for context manager: class and function decorator
- context manager below is for measuring execution time for a code block
'''

import time

class CatchTime:
    def __enter__(self):
        self.t = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.t = time.time() - self.t
        print(f'execution time is: {self.t: .2f} secs')

with CatchTime():
    time.sleep(0.5)



from contextlib import contextmanager

@contextmanager
def catch_time():
    try:
        t = time.time()
        yield t
    finally:
        t = time.time() - t
        print(f'execution time is: {t: .2f} secs')

with catch_time():
    time.sleep(0.5)