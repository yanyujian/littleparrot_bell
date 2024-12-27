import subprocess
import platform

def openExcelFile(file_path):
    system_name = platform.system()
    
    if system_name == "Windows":
        # 'start' is a Windows command; 'shell=True' is required to invoke it
        subprocess.Popen(["start", file_path], shell=True)
    elif system_name == "Darwin":
        # macOS uses 'open'
        subprocess.Popen(["open", file_path])
    else:
        # Linux/Unix-like uses 'xdg-open'
        subprocess.Popen(["xdg-open", file_path])

