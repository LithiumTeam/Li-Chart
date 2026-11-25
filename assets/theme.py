import tkinter as tk

BG = '#1e1e2e'
FG = '#cdd6f4'
BTN_BG = '#313244'
BTN_FG = '#cdd6f4'
ACCENT = '#89b4fa'
SELECT_BG = '#45475a'
MUTED = '#6c7086'

def _theme_options(widget, **options):
    for option, value in options.items():
        try:
            widget.configure(**{option: value})
        except tk.TclError:
            pass

def apply(widget):
    _theme_options(
        widget,
        bg=BG,
        fg=FG,
        highlightbackground=BG,
        highlightcolor=ACCENT,
    )

    # cursor + selection colors for editable widgets
    if isinstance(widget, (tk.Text, tk.Entry)):
        _theme_options(
            widget,
            insertbackground=FG,
            selectbackground=SELECT_BG,
            selectforeground=FG,
            disabledforeground=MUTED,
        )

    # ScrolledText: theme the parts that don't inherit the widget colors
    # - Python < 3.14: the inner Text widget lives in `widget.text`
    inner = getattr(widget, 'text', None)
    if isinstance(inner, tk.Text):
        _theme_options(
            inner,
            bg=BG,
            fg=FG,
            insertbackground=FG,
            selectbackground=SELECT_BG,
            selectforeground=FG,
            highlightbackground=BG,
            highlightcolor=ACCENT,
        )

    # - Python >= 3.14: the Text is packed inside `widget.frame`
    frame = getattr(widget, 'frame', None)
    if isinstance(frame, tk.Frame):
        frame.configure(bg=BG)

    # - the vertical scrollbar
    vbar = getattr(widget, 'vbar', None)
    if isinstance(vbar, tk.Scrollbar):
        _theme_options(
            vbar,
            bg=SELECT_BG,
            troughcolor=BG,
            activebackground=ACCENT,
            elementborderwidth=0,
            highlightthickness=0,
            bd=0,
        )

def button_style(widget):
    widget.configure(bg=BTN_BG, fg=BTN_FG, activebackground=SELECT_BG, activeforeground=FG)
