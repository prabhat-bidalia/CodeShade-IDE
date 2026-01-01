from tkinter import filedialog
from pathlib import Path

def new_file(text_area):
    text_area.delete("1.0", "end")
    return None

def open_file(text_area):
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=(
            ("Text Files", "*.txt"),
            ("Python Files", "*.py"),
            ("C++ Files", "*.cpp"),
            ("All Files", "*.*")
        )
    )
    if not file_path:
        return None

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        text_area.delete("1.0", "end")
        text_area.insert("1.0", file.read())

    return file_path, Path(file_path).name

def save_file(text_area, current_file):
    if current_file:
        with open(current_file, "w", encoding="utf-8") as file:
            file.write(text_area.get("1.0", "end-1c"))
        return current_file, Path(current_file).name

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=(
            ("Text File", "*.txt"),
            ("Python File", "*.py"),
            ("C++ File", "*.cpp"),
            ("All Files", "*.*")
        )
    )
    if not file_path:
        return None

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(text_area.get("1.0", "end-1c"))

    return file_path, Path(file_path).name
