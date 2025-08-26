import engine as ui
import pygame

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

# Radio demo (grouped)
r1 = ui.Radio(
    f1,
    (5, 120),
    group_gid=0,
    checked=True,
    on_change=lambda v: print('Radio1 change ->', v)
)

r2 = ui.Radio(
    f1,
    (30, 120),
    group_gid=0,
    checked=False,
    on_change=lambda v: print('Radio2 change ->', v)
)

# Ungrouped radio (toggle-like)
r3 = ui.Radio(
    f1,
    (5, 150),
    group_gid=None,
    checked=False,
    on_change=lambda v: print('Radio3 toggle ->', v)
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

# Slider demo
slider = ui.Slider(
    f2,
    (20, 220),
    size=(240, 28),
    min_value=0,
    max_value=100,
    value=25,
    on_change=lambda v: print('Slider value', v)
)

# Segmented control demo
seg = ui.SegmentedControl(
    f2,
    (20, 260),
    segments=['One', 'Two', 'Three'],
    size=(260, 30),
    selected=0,
    on_change=lambda i, label: print('Segment selected', i, label)
)

# Icon button demo (simple colored square as icon)
icon_surf = pygame.Surface((14,14))
icon_surf.fill((40,110,200))
ib = ui.IconButton(
    f2,
    (300, 20),
    icon_surf,
    size=(36,36),
    on_click=lambda btn: print('IconButton clicked')
)

# Progress bar
progress = ui.ProgressBar(
    f2,
    (20, 300),
    size=(240, 20),
    value=50
)

@window.event('draw')
def frame(frame):
    progress.value += 0.1
    if progress.value >= 100:
        progress.value = 0
    print(progress.value)


window.mainloop()
