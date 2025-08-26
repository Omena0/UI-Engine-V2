import engine as ui

window = ui.Window()

f1 = ui.Frame(
    window,
    (5,5),
    (window.size[0]//2-5, window.size[1]-10)
)

f2 = ui.Frame(
    window,
    (window.size[0]//2+5,5),
    (window.size[0]//2-10, window.size[1]-10)
)

theme_switcher = ui.Button(
    window,
    (window.size[0]-50, 5),
    "Theme",
    (45,45),
    on_click=lambda _: (ui.theme.swap_theme(window))
)

ui.Field(
    f1,
    (5, 5),
    (None, 30),
	"Enter text here",
    size = (200,100),
    multiline=True
)

# Toggle demo in the right frame
toggle = ui.Toggle(
    f2,
    (20, 20),
    value=False,
    on_change=lambda v: print('Toggle changed ->', v)
)

# also listen via event emitter
toggle.on('change', lambda v: print('Emitter change:', v))

# Dropdown demo
dd = ui.Dropdown(
    f2,
    (20, 80),
    size=(200, 36),
    options=['Option A', 'Option B', 'Option C'],
    selected=0,
    on_select=lambda i, v: print('Dropdown selected', i, v)
)

# Dropdown demo
dd2 = ui.Dropdown(
    f2,
    (20, 150),
    size=(200, 36),
    options=['Option A', 'Option B', 'Option C'],
    selected=0,
    on_select=lambda i, v: print('Dropdown2 selected', i, v)
)

window.mainloop()
