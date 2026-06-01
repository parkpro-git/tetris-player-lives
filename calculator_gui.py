import tkinter as tk
import math

FONT_DISPLAY = ("Consolas", 28, "bold")
FONT_EXPR    = ("Consolas", 13)
FONT_BTN     = ("Consolas", 16, "bold")

BG       = "#1e1e2e"
DISP_BG  = "#181825"
BTN_NUM  = "#313244"
BTN_OP   = "#45475a"
BTN_EQ   = "#89b4fa"
BTN_CLR  = "#f38ba8"
BTN_FUNC = "#a6e3a1"
FG       = "#cdd6f4"
FG_EQ    = "#1e1e2e"
HOVER    = "#585b70"

BUTTONS = [
    ("C",   1, 0, BTN_CLR),  ("±",  1, 1, BTN_OP),  ("%",  1, 2, BTN_OP),  ("÷",  1, 3, BTN_OP),
    ("7",   2, 0, BTN_NUM),  ("8",  2, 1, BTN_NUM),  ("9",  2, 2, BTN_NUM), ("×",  2, 3, BTN_OP),
    ("4",   3, 0, BTN_NUM),  ("5",  3, 1, BTN_NUM),  ("6",  3, 2, BTN_NUM), ("−",  3, 3, BTN_OP),
    ("1",   4, 0, BTN_NUM),  ("2",  4, 1, BTN_NUM),  ("3",  4, 2, BTN_NUM), ("+",  4, 3, BTN_OP),
    ("√",   5, 0, BTN_FUNC), ("0",  5, 1, BTN_NUM),  (".",  5, 2, BTN_NUM), ("=",  5, 3, BTN_EQ),
]


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("계산기")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._expr   = ""   # raw expression
        self._result = ""   # last evaluated result
        self._new    = True # next digit starts fresh after =

        self._build_ui()
        self._bind_keys()

    # ----------------------------------------------------------------- UI
    def _build_ui(self):
        # Expression label (top, small)
        self._expr_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self._expr_var,
                 font=FONT_EXPR, bg=DISP_BG, fg="#6c7086",
                 anchor="e", width=16, padx=12, pady=4
                 ).grid(row=0, column=0, columnspan=4, sticky="ew")

        # Main display
        self._disp_var = tk.StringVar(value="0")
        tk.Label(self, textvariable=self._disp_var,
                 font=FONT_DISPLAY, bg=DISP_BG, fg=FG,
                 anchor="e", width=16, padx=12, pady=10
                 ).grid(row=1, column=0, columnspan=4, sticky="ew")

        # Buttons
        for (text, row, col, color) in BUTTONS:
            fg = FG_EQ if color == BTN_EQ else FG
            btn = tk.Button(
                self, text=text, font=FONT_BTN,
                bg=color, fg=fg, activebackground=HOVER, activeforeground=FG,
                relief="flat", borderwidth=0, padx=0, pady=18,
                command=lambda t=text: self._on_btn(t)
            )
            btn.grid(row=row + 1, column=col, sticky="nsew", padx=2, pady=2)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=HOVER))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

        for i in range(4):
            self.columnconfigure(i, weight=1, minsize=80)
        for i in range(2, 8):
            self.rowconfigure(i, weight=1, minsize=60)

    def _bind_keys(self):
        self.bind("<Key>", self._on_key)
        self.bind("<Return>",    lambda e: self._on_btn("="))
        self.bind("<BackSpace>", lambda e: self._backspace())

    def _on_key(self, e):
        ch = e.char
        if ch in "0123456789.":
            self._on_btn(ch)
        elif ch in "+-*%":
            self._on_btn(ch)
        elif ch == "/":
            self._on_btn("÷")
        elif ch in ("\r", "\n"):
            self._on_btn("=")
        elif ch.lower() == "c":
            self._on_btn("C")

    # --------------------------------------------------------------- logic
    def _on_btn(self, t: str):
        if t == "C":
            self._expr = ""
            self._disp_var.set("0")
            self._expr_var.set("")
            self._new = True
            return

        if t == "=":
            self._evaluate()
            return

        if t == "±":
            cur = self._disp_var.get()
            try:
                val = -float(cur)
                self._disp_var.set(self._fmt(val))
                if self._expr:
                    # replace last number in expr
                    self._expr = self._expr[:-len(cur)] + self._fmt(val)
            except ValueError:
                pass
            return

        if t == "√":
            cur = self._disp_var.get()
            try:
                val = math.sqrt(float(cur))
                self._expr_var.set(f"√({cur})")
                self._disp_var.set(self._fmt(val))
                self._expr = self._fmt(val)
                self._new = True
            except ValueError:
                self._disp_var.set("오류")
                self._expr = ""
                self._new = True
            return

        # Map display symbols to Python operators
        op_map = {"÷": "/", "×": "*", "−": "-"}
        raw = op_map.get(t, t)

        if t in ("÷", "×", "−", "+", "-", "*", "/", "%"):
            if self._expr and self._expr[-1] in "+-*/":
                self._expr = self._expr[:-1]  # replace last op
            self._expr += raw
            self._expr_var.set(self._expr)
            self._new = True
            return

        # Digit or dot
        if self._new:
            self._disp_var.set("")
            self._new = False

        cur = self._disp_var.get()
        if t == "." and "." in cur:
            return
        if cur == "0" and t != ".":
            cur = ""
        cur += t
        self._disp_var.set(cur)
        self._expr += t
        self._expr_var.set(self._expr)

    def _evaluate(self):
        expr = self._expr.strip()
        if not expr:
            return
        try:
            result = eval(expr, {"__builtins__": {}}, {})  # safe: no builtins
            self._expr_var.set(expr + " =")
            self._disp_var.set(self._fmt(result))
            self._expr = self._fmt(result)
            self._new = True
        except ZeroDivisionError:
            self._disp_var.set("0으로 나눌 수 없음")
            self._expr = ""
            self._new = True
        except Exception:
            self._disp_var.set("오류")
            self._expr = ""
            self._new = True

    @staticmethod
    def _fmt(val) -> str:
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return f"{val:.10g}"

    def _backspace(self):
        cur = self._disp_var.get()
        if len(cur) > 1:
            self._disp_var.set(cur[:-1])
            self._expr = self._expr[:-1]
        else:
            self._disp_var.set("0")
            self._expr = self._expr[:-1] if self._expr else ""
        self._expr_var.set(self._expr)


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
