import fcntl

class FileLock:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_handle = None

    def acquire(self):
        self.file_handle = open(self.file_path, 'w')
        fcntl.flock(self.file_handle, fcntl.LOCK_EX)

    def release(self):
        if self.file_handle:
            fcntl.flock(self.file_handle, fcntl.LOCK_UN)
            self.file_handle.close()