import os
import shutil


class FileInterface:
    @staticmethod
    def write_file(path, content):
        with open(path, "w") as f:
            f.write(content)

    @staticmethod
    def copy_file(src, dest):
        shutil.copy2(src, dest)

    @staticmethod
    def create_directory_if_not_exists(directory):
        os.makedirs(directory, exist_ok=True)

    @staticmethod
    def get_directory(file_path):
        return os.path.dirname(file_path)
