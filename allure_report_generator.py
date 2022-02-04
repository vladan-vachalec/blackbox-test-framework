import os
import platform
import subprocess

if __name__ == "__main__":
    bin = 'allure.bat' if platform.system() == 'Windows' else 'allure'
    if os.path.isdir('allure_reports'):
        subprocess.call(
            [os.path.join('allure_binaries', 'allure-2.9.0', 'bin', bin), "generate", "--clean", "allure_reports"])
