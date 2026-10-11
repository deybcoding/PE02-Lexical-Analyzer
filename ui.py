import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import file_io
import controller as ctl
from controller import CompilerController

IDE_NAME = "IOL IDE"
SOURCE_TYPES = [("IOL source files", "*" + file_io.SOURCE_EXT), ("All files", "*.*")]
TOKEN_TYPES = [("Token files", "*" + file_io.TOKEN_EXT), ("All files", "*.*")]
MONO = ("Courier", 12)


class CompilerUI:
    def __init__(self, root: tk.Tk, controller: CompilerController):
        self.root = root
        self.controller = controller
        self.mod = (
            "Command" if root.tk.call("tk", "windowingsystem") == "aqua" else "Control"
        )
        self._build()
        self._bind_shortcuts()
        self._refresh_title()
        root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _build(self) -> None:
        self.root.geometry("1000x700")
        self.root.minsize(700, 500)

        toolbar = ttk.Frame(self.root, padding=4)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        self.file_actions = [
            (ctl.NEW_FILE, self.new_file, f"<{self.mod}-n>", f"{self.mod}+N"),
            (ctl.OPEN_FILE, self.open_file, f"<{self.mod}-o>", f"{self.mod}+O"),
            (ctl.SAVE_FILE, self.save_file, f"<{self.mod}-s>", f"{self.mod}+S"),
            (
                ctl.SAVE_FILE_AS,
                self.save_file_as,
                f"<{self.mod}-Shift-S>",
                f"{self.mod}+Shift+S",
            ),
        ]
        self.compile_actions = [
            (ctl.COMPILE_CODE, self.compile_code, "<F5>", "F5"),
            (ctl.SHOW_TOKENIZED_CODE, self.show_tokenized_code, "<F6>", "F6"),
        ]
        for label, command, _, _ in self.file_actions + self.compile_actions:
            ttk.Button(toolbar, text=label, command=command).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text=ctl.EXIT, command=self.exit_app).pack(
            side=tk.RIGHT, padx=2
        )

        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        for label, command, _, accel in self.file_actions:
            file_menu.add_command(label=label, command=command, accelerator=accel)
        file_menu.add_separator()
        file_menu.add_command(label=ctl.EXIT, command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)
        compile_menu = tk.Menu(menubar, tearoff=0)
        for label, command, _, accel in self.compile_actions:
            compile_menu.add_command(label=label, command=command, accelerator=accel)
        menubar.add_cascade(label="Compile", menu=compile_menu)
        self.root.config(menu=menubar)

        vertical = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        vertical.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        horizontal = ttk.PanedWindow(vertical, orient=tk.HORIZONTAL)
        vertical.add(horizontal, weight=3)

        self.tabs = ttk.Notebook(horizontal)
        editor_frame = ttk.Frame(self.tabs, padding=2)
        self.editor = self._scrolled_text(editor_frame, undo=True)
        self.editor.bind("<<Modified>>", lambda _: self._refresh_title())
        self.tabs.add(editor_frame, text=self.controller.file_name)
        self.tokens_frame = ttk.Frame(self.tabs, padding=2)
        self.tokens_view = self._scrolled_text(self.tokens_frame, state=tk.DISABLED)
        self.tabs.add(self.tokens_frame, text="Tokenized Code")
        horizontal.add(self.tabs, weight=3)

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
        for _, command, sequence, _ in self.file_actions + self.compile_actions:
            self.root.bind(sequence, lambda _, c=command: c())

    def _refresh_title(self) -> None:
        name = self.controller.file_name
        dirty = "*" if self.editor.edit_modified() else ""
        self.tabs.tab(0, text=f"{name}{dirty}")
        self.root.title(f"{IDE_NAME} - {name}{dirty}")

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

    def _set_tokens_view(self, content: str) -> None:
        self.tokens_view.configure(state=tk.NORMAL)
        self.tokens_view.delete("1.0", tk.END)
        self.tokens_view.insert("1.0", content)
        self.tokens_view.configure(state=tk.DISABLED)

    def _reset_outputs(self) -> None:
        self._clear_console()
        self._set_variables([])
        self._set_tokens_view("")
        self.tabs.select(0)

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
        self._reset_outputs()
        self._refresh_title()
        self._log("New file created.")

    def open_file(self) -> None:
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            title="Open .iol file", filetypes=SOURCE_TYPES
        )
        if not path:
            return
        try:
            source = self.controller.open_file(path)
        except file_io.FileIOError as e:
            messagebox.showerror(ctl.OPEN_FILE, str(e))
            return
        self._set_editor(source)
        self._reset_outputs()
        self._refresh_title()
        self._log(f"Opened {path}")

    def _after_save(self, saved: str) -> None:
        self.editor.edit_modified(False)
        self._refresh_title()
        self._log(f"Saved {saved}")

    def save_file(self) -> None:
        try:
            saved = self.controller.save_file(self._editor_source())
        except file_io.FileIOError as e:
            messagebox.showerror(ctl.SAVE_FILE, str(e))
            return
        self._after_save(saved)

    def save_file_as(self) -> None:
        current = self.controller.source_path or self.controller.default_path
        path = filedialog.asksaveasfilename(
            title="Save .iol file as",
            defaultextension=file_io.SOURCE_EXT,
            filetypes=SOURCE_TYPES,
            initialdir=os.path.dirname(current) if current else None,
            initialfile=self.controller.file_name,
        )
        if not path:
            return
        try:
            saved = self.controller.save_file_as(self._editor_source(), path)
        except file_io.FileIOError as e:
            messagebox.showerror(ctl.SAVE_FILE_AS, str(e))
            return
        self._after_save(saved)

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
        self._log(result.summary, "error" if result.has_errors else "ok")
        self._log(f"Tokenized code saved to {result.tkn_path}")
        self._set_variables(result.variables)
        self._set_tokens_view(result.tokenized_code)

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
        self._set_tokens_view(content)
        self.tabs.select(self.tokens_frame)

    def exit_app(self) -> None:
        if self.editor.edit_modified():
            if not messagebox.askyesno(ctl.EXIT, "Discard unsaved changes and exit?"):
                return
        self.root.destroy()


def run() -> None:
    root = tk.Tk()
    CompilerUI(root, CompilerController(work_dir=os.getcwd()))
    root.mainloop()
