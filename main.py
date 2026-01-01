import tkinter as tk
import subprocess
import os
import sys
from tkinter import messagebox
from file_functions import new_file, open_file, save_file
import re

def window():
    root = tk.Tk()
    root.geometry("750x600")
    root.title("CodeShade I.D.E")

    usage_text = """
        CodeShade I.D.E

        A lightweight code editor built for focused programming.

        Supported Languages:
        - Python (.py)
        - C++ (.cpp)

        Features:
        - Syntax highlighting for Python and C++
        - Auto indentation and bracket pairing
        - Run Python and C++ code directly
        - File operations (New, Open, Save)

        Platform:
        - Windows only (uses cmd and g++)

        Notes:
        - Python must be installed and added to PATH
        - g++ compiler must be installed for C++ execution
    """

    current_file = None

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    scrollbar_y = tk.Scrollbar(root)
    scrollbar_y.pack(side="right", fill="y")

    scrollbar_x = tk.Scrollbar(root, orient="horizontal")
    scrollbar_x.pack(side="bottom", fill="x")

    top_bar = tk.Frame(root)
    top_bar.pack(side="top", fill="x")

    name_label = tk.Label(top_bar, text="Untitled File", anchor="w", padx=5, pady=5)
    name_label.pack(side="left")

    text_area = tk.Text(
        root,
        wrap="none",
        font=("SF Mono", 10),
        undo=True,
        xscrollcommand=scrollbar_x.set,
        yscrollcommand=scrollbar_y.set,
        bg="#1e1e2e",
        fg="#ffffff",
        insertbackground="#ffffff"
    )
    text_area.pack(fill="both", expand=True)

    scrollbar_y.config(command=text_area.yview)
    scrollbar_x.config(command=text_area.xview)

    pairs = {"(": ")", "{": "}", "[": "]", '"': '"', "'": "'"}

    def auto_close(event):
        if event.char in pairs:
            text_area.insert("insert", pairs[event.char])
            text_area.mark_set("insert", "insert-1c")

    text_area.bind("<Key>", auto_close)

    def auto_indent(event):
        cursor = text_area.index("insert")
        line_num = int(cursor.split(".")[0])
        line_text = text_area.get(f"{line_num}.0", f"{line_num}.end")
        indent = " " * (len(line_text) - len(line_text.lstrip()))

        if text_area.get("insert-1c", "insert") == "{":
            text_area.insert("insert", "\n" + indent + "    \n" + indent)
            text_area.mark_set("insert", f"{line_num+1}.{len(indent)+4}")
            return "break"

        if line_text.rstrip().endswith(":"):
            indent += "    "

        text_area.insert("insert", "\n" + indent)
        return "break"

    text_area.bind("<Return>", auto_indent)

    def insert_tab(event):
        text_area.insert("insert", "    ")
        return "break"

    text_area.bind("<Tab>", insert_tab)

    PYTHON_KEYWORDS = r'\b(input|print|False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|int|float|complex|bool|str|list|tuple|set|frozenset|dict|bytes|bytearray|memoryview|range|type|object|slice|staticmethod|classmethod|property|Exception|BaseException)\b'
    CPP_KEYWORDS = r'\b(include|alignas|alignof|and|and_eq|asm|atomic_cancel|atomic_commit|atomic_noexcept|auto|bitand|bitor|bool|break|case|catch|char|char8_t|char16_t|char32_t|class|compl|concept|const|consteval|constexpr|constinit|const_cast|continue|co_await|co_return|co_yield|decltype|default|delete|do|double|dynamic_cast|else|enum|explicit|export|extern|false|float|for|friend|goto|if|inline|int|long|mutable|namespace|new|noexcept|not|not_eq|nullptr|operator|or|or_eq|private|protected|public|register|reinterpret_cast|requires|return|short|signed|sizeof|static|static_assert|static_cast|struct|switch|template|this|thread_local|throw|true|try|typedef|typeid|typename|union|unsigned|using|virtual|void|volatile|wchar_t|while|xor|xor_eq)\b'

    def highlight_syntax(event=None):
        text_area.tag_remove("keyword", "1.0", "end")
        text_area.tag_remove("comment", "1.0", "end")
        text_area.tag_remove("string", "1.0", "end")

        content = text_area.get("1.0", "end-1c")
        file_ext = ".txt" if not current_file else os.path.splitext(current_file)[1]

        if file_ext == ".py":
            pattern = PYTHON_KEYWORDS
            comment_pattern = r"#.*"
            string_pattern = r"(\".*?\"|'.*?')"
        elif file_ext == ".cpp":
            pattern = CPP_KEYWORDS
            comment_pattern = r"//.*"
            string_pattern = r"(\".*?\")"
        else:
            return

        for match in re.finditer(pattern, content):
            text_area.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for match in re.finditer(comment_pattern, content):
            text_area.tag_add("comment", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        for match in re.finditer(string_pattern, content):
            text_area.tag_add("string", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    text_area.tag_config("keyword", foreground="#FF5555")
    text_area.tag_config("comment", foreground="#6A9955")
    text_area.tag_config("string", foreground="#CE9178")
    text_area.bind("<KeyRelease>", highlight_syntax)

    def run_code():
        nonlocal current_file
        file_path, filename = save_file(text_area, current_file)
        if not file_path:
            return

        current_file = file_path
        highlight_syntax()
        file_ext = os.path.splitext(current_file)[1]

        if file_ext == ".py":
            subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", sys.executable, current_file],
                shell=True
            )
        elif file_ext == ".cpp":
            exe_path = os.path.splitext(current_file)[0] + ".exe"
            compile_proc = subprocess.run(
                ["g++", current_file, "-o", exe_path],
                capture_output=True,
                text=True
            )
            if compile_proc.returncode != 0:
                messagebox.showerror("Compile Error", compile_proc.stderr)
                return
            subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", exe_path],
                shell=True
            )
        else:
            messagebox.showerror("Unsupported File", "Only Python and C++ files can be executed.")

    run_button = tk.Button(top_bar, text="Run", width=6, fg="green", command=run_code)
    run_button.pack(side="right", padx=5, pady=5)

    def new_cmd():
        nonlocal current_file
        current_file = new_file(text_area)
        name_label.config(text="Untitled File")
        highlight_syntax()

    def open_cmd():
        nonlocal current_file
        result = open_file(text_area)
        if result:
            current_file, filename = result
            name_label.config(text=filename)
            highlight_syntax()

    def save_cmd():
        nonlocal current_file
        result = save_file(text_area, current_file)
        if result:
            current_file, filename = result
            name_label.config(text=filename)
            highlight_syntax()

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="New", command=new_cmd)
    file_menu.add_command(label="Open", command=open_cmd)
    file_menu.add_command(label="Save", command=save_cmd)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.destroy)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Usage", command=lambda: messagebox.showinfo("Usage", usage_text))
    help_menu.add_command(
        label="Light Mode",
        command=lambda: messagebox.showinfo("No Way", "Real programmers code in the dark.")
    )

    root.mainloop()

if __name__ == "__main__":
    window()
