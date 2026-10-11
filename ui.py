import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import file_io
import controller as ctl
from controller import CompilerController

APP_TITLE = "CMSC 129 - PE02 Lexical Analyzer"
SOURCE_TYPES = [("IO source files", "*" + file_io.SOURCE_EXT), ("All files", "*.*")]
TOKEN_TYPES = [("Token files", "*" + file_io.TOKEN_EXT), ("All files", "*.*")]
MONO = ("Courier", 12)


class CompilerUI:
    def __init__(self, root: tk.Tk, controller: CompilerController):
        self.root = root
        self.controller = controller
        self._build()
        self._bind_shortcuts()
        self._refresh_title()
        root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _build(self) -> None:
        self.root.geometry("1000x700")
        self.root.minsize(700, 500)

        toolbar = ttk.Frame(self.root, padding=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        actions = [
            (ctl.NEW_FILE, self.new_file),
            (ctl.OPEN_FILE, self.open_file),
            (ctl.COMPILE_CODE, self.compile_code),
            (ctl.SHOW_TOKENIZED_CODE, self.show_tokenized_code),
            (ctl.EXIT, self.exit_app),
        ]
        for label, command in actions:
            ttk.Button(toolbar, text=label, command=command).pack(side=tk.LEFT, padx=2)

        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=ctl.NEW_FILE, command=self.new_file)
        file_menu.add_command(label=ctl.OPEN_FILE, command=self.open_file)
        file_menu.add_command(label="Save File", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label=ctl.EXIT, command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label=ctl.COMPILE_CODE, command=self.compile_code)
        run_menu.add_command(
            label=ctl.SHOW_TOKENIZED_CODE, command=self.show_tokenized_code
        )
        menubar.add_cascade(label="Run", menu=run_menu)
        self.root.config(menu=menubar)

        vertical = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        vertical.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        horizontal = ttk.PanedWindow(vertical, orient=tk.HORIZONTAL)
        vertical.add(horizontal, weight=3)

        editor_frame = ttk.LabelFrame(horizontal, text="Editor", padding=2)
        self.editor = self._scrolled_text(editor_frame, undo=True)
        horizontal.add(editor_frame, weight=3)

        table_frame = ttk.LabelFrame(horizontal, text="Table of Variables", padding=2)
        self.variable_table = ttk.Treeview(
            table_frame, columns=("name", "type"), show="headings"
        )
        self.variable_table.heading("name", text="Variable Name")
        self.variable_table.heading("type", text="Type")
        self.variable_table.column("name", width=140)
        self.variable_table.column("type", width=80)
        table_scroll = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.variable_table.yview
        )
        self.variable_table.configure(yscrollcommand=table_scroll.set)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.variable_table.pack(fill=tk.BOTH, expand=True)
        horizontal.add(table_frame, weight=1)

        console_frame = ttk.LabelFrame(vertical, text="Console", padding=2)
        self.console = self._scrolled_text(console_frame, height=8, state=tk.DISABLED)
        self.console.tag_configure("error", foreground="red")
        self.console.tag_configure("ok", foreground="dark green")
        vertical.add(console_frame, weight=1)

    def _scrolled_text(self, parent, **kwargs) -> tk.Text:
        text = tk.Text(parent, wrap=tk.NONE, font=MONO, **kwargs)
        yscroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text.yview)
        xscroll = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def _bind_shortcuts(self) -> None:
        mod = (
            "Command"
            if self.root.tk.call("tk", "windowingsystem") == "aqua"
            else "Control"
        )
        self.root.bind(f"<{mod}-n>", lambda _: self.new_file())
        self.root.bind(f"<{mod}-o>", lambda _: self.open_file())
        self.root.bind(f"<{mod}-s>", lambda _: self.save_file())
        self.root.bind("<F5>", lambda _: self.compile_code())
        self.root.bind("<F6>", lambda _: self.show_tokenized_code())

    def _refresh_title(self) -> None:
        path = self.controller.source_path
        name = os.path.basename(path) if path else "Untitled"
        self.root.title(f"{name} - {APP_TITLE}")

    def _editor_source(self) -> str:
        return self.editor.get("1.0", "end-1c")

    def _set_editor(self, content: str) -> None:
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.editor.edit_reset()
        self.editor.edit_modified(False)

    def _log(self, message: str, tag: str = "") -> None:
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, message + "\n", tag)
        self.console.see(tk.END)
        self.console.configure(state=tk.DISABLED)

    def _clear_console(self) -> None:
        self.console.configure(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.configure(state=tk.DISABLED)

    def _set_variables(self, variables) -> None:
        self.variable_table.delete(*self.variable_table.get_children())
        for name, var_type in variables:
            self.variable_table.insert("", tk.END, values=(name, var_type))

    def _confirm_discard(self) -> bool:
        if not self.editor.edit_modified():
            return True
        return messagebox.askyesno(
            "Unsaved changes", "Discard unsaved changes in the editor?"
        )

    def new_file(self) -> None:
        if not self._confirm_discard():
            return
        self._set_editor(self.controller.new_file())
        self._clear_console()
        self._set_variables([])
        self._refresh_title()
        self._log("New file created.")

    def open_file(self) -> None:
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(title="Open .io file", filetypes=SOURCE_TYPES)
        if not path:
            return
        try:
            source = self.controller.open_file(path)
        except file_io.FileIOError as e:
            messagebox.showerror(ctl.OPEN_FILE, str(e))
            return
        self._set_editor(source)
        self._clear_console()
        self._set_variables([])
        self._refresh_title()
        self._log(f"Opened {path}")

    def save_file(self) -> None:
        path = self.controller.source_path
        if path is None:
            path = filedialog.asksaveasfilename(
                title="Save .io file",
                defaultextension=file_io.SOURCE_EXT,
                filetypes=SOURCE_TYPES,
            )
            if not path:
                return
        try:
            saved = self.controller.save_file(self._editor_source(), path)
        except file_io.FileIOError as e:
            messagebox.showerror("Save File", str(e))
            return
        self.editor.edit_modified(False)
        self._refresh_title()
        self._log(f"Saved {saved}")

    def compile_code(self) -> None:
        tkn_path = self.controller.default_tkn_path()
        if tkn_path is None:
            tkn_path = filedialog.asksaveasfilename(
                title="Save tokenized output as",
                defaultextension=file_io.TOKEN_EXT,
                filetypes=TOKEN_TYPES,
                initialfile="untitled" + file_io.TOKEN_EXT,
            )
            if not tkn_path:
                return
        try:
            result = self.controller.compile_code(self._editor_source(), tkn_path)
        except file_io.FileIOError as e:
            messagebox.showerror(ctl.COMPILE_CODE, str(e))
            return

        self._clear_console()
        self._log(f"Compiled {len(result.tokens)} token(s).")
        for error in result.errors:
            self._log(error, "error")
        if result.errors:
            self._log(f"{len(result.errors)} lexical error(s) found.", "error")
        else:
            self._log("No lexical errors found.", "ok")
        self._log(f"Tokenized code saved to {result.tkn_path}")
        self._set_variables(result.variables)

    def show_tokenized_code(self) -> None:
        try:
            content = self.controller.show_tokenized_code()
        except file_io.FileIOError as e:
            messagebox.showerror(ctl.SHOW_TOKENIZED_CODE, str(e))
            return
        if content is None:
            messagebox.showinfo(
                ctl.SHOW_TOKENIZED_CODE, "Compile the code first to generate tokens."
            )
            return

        window = tk.Toplevel(self.root)
        title = os.path.basename(self.controller.tkn_path or "Tokenized Code")
        window.title(title)
        window.geometry("600x500")
        frame = ttk.Frame(window, padding=4)
        frame.pack(fill=tk.BOTH, expand=True)
        text = self._scrolled_text(frame)
        text.insert("1.0", content)
        text.configure(state=tk.DISABLED)

    def exit_app(self) -> None:
        if self.editor.edit_modified():
            if not messagebox.askyesno(ctl.EXIT, "Discard unsaved changes and exit?"):
                return
        self.root.destroy()


def run() -> None:
    root = tk.Tk()
    CompilerUI(root, CompilerController())
    root.mainloop()
