import engine as ui
import pygame
import random

# Fonts
font_small = (None, 14)
font_med = (None, 18)

# Create window
window = ui.Window()

# Top-level controls
theme_switcher = ui.Button(
    window,
    (window.size[0] - 80, 8),
    "Theme",
    (64, 28),
    on_click=lambda _: ui.theme.swap_theme(window),
)

# Create a TabFrame that automatically manages frames
left_tab = ui.TabFrame(window, (8, 8), (window.size[0] // 2 - 16, window.size[1] - 16), tab_count=3)

# Create a SegmentedButton for tab switching
seg_tabs = ui.SegmentedButton(
    window, 
    (left_tab.pos[0] + 8, left_tab.pos[1] + 8), 
    segments=["Form", "Controls", "Sliders"], 
    size=(left_tab.size[0] - 16, 34)
)

# Tab 0: Form controls
tab0 = left_tab[0]
lbl = ui.Label(tab0, (8, 8), "User Info", font_med)
name_field = ui.Field(tab0, (8, 36), font_small, "Your name", size=(280, 28))
email_field = ui.Field(tab0, (8, 72), font_small, "email@example.com", size=(280, 28))
addr_field = ui.Field(tab0, (8, 108), font_small, "Address line 1", size=(280, 28))
phone_field = ui.Field(tab0, (8, 144), font_small, "(555) 555-5555", size=(280, 28))
chk = ui.CheckBox(tab0, (8, 180), text='Newsletter signup', on_change=lambda v: print('Checkbox ->', v))
chk.checked = True

# Avatar (positioned to not overlap with fields)
avatar_surf = pygame.Surface((64, 64))
avatar_surf.fill((180, 180, 220))
avatar = ui.IconButton(tab0, (300, 36), avatar_surf, size=(64, 64), on_click=lambda b: print('Avatar clicked'))

# Form buttons
submit_btn = ui.Button(tab0, (8, 220), "Submit", (120, 32), on_click=lambda b: print('Form submitted'))
clear_btn = ui.Button(tab0, (140, 220), "Clear", (80, 32), on_click=lambda b: [
    setattr(name_field, 'value', ''), 
    setattr(email_field, 'value', ''),
    setattr(addr_field, 'value', ''),
    setattr(phone_field, 'value', '')
])

# Tab 1: Controls
tab1 = left_tab[1]
toggle = ui.Toggle(tab1, (8, 8), value=False, on_change=lambda v: print('Toggle ->', v))
toggle_lbl = ui.Label(tab1, (50, 15), "Enable notifications", font_small)

r1 = ui.Radio(tab1, (8, 48), group_gid=1, checked=True, on_change=lambda v: print('Radio A ->', v))
r1_lbl = ui.Label(tab1, (30, 52), "Option A", font_small)
r2 = ui.Radio(tab1, (120, 48), group_gid=1, checked=False, on_change=lambda v: print('Radio B ->', v))
r2_lbl = ui.Label(tab1, (142, 52), "Option B", font_small)

seg = ui.SegmentedButton(tab1, (8, 88), segments=["Alpha", "Beta", "Gamma"], size=(280, 30), on_change=lambda i, l: print('Seg ->', i, l))
chk2 = ui.CheckBox(tab1, (8, 128), text='Receive newsletter', on_change=lambda v: print('Newsletter ->', v))
toggle2 = ui.Toggle(tab1, (8, 160), value=True, on_change=lambda v: print('Toggle2 ->', v))
toggle2_lbl = ui.Label(tab1, (50, 167), "Dark mode", font_small)

# Tab 2: Sliders and progress
tab2 = left_tab[2]
slider_lbl1 = ui.Label(tab2, (8, 8), "Volume", font_small)
slider = ui.Slider(tab2, (8, 28), size=(280, 28), min_value=0, max_value=100, value=30, on_change=lambda v: print('Volume ->', v))

progress_lbl = ui.Label(tab2, (8, 68), "Progress", font_small)
progress = ui.ProgressBar(tab2, (8, 88), size=(280, 18), value=50)

slider_lbl2 = ui.Label(tab2, (8, 120), "Brightness", font_small)
slider2 = ui.Slider(tab2, (8, 140), size=(280, 28), min_value=0, max_value=1, value=0.5, on_change=lambda v: print('Brightness ->', v))

progress_lbl2 = ui.Label(tab2, (8, 180), "Loading", font_small)
progress2 = ui.ProgressBar(tab2, (8, 200), size=(280, 12), value=10)

# Wire segmented tabs to the TabFrame
def _seg_change(idx, label):
    try:
        left_tab.current = idx
    except Exception:
        pass

seg_tabs.on('change', _seg_change)

# Create a right-side frame with controls
right = ui.Frame(window, (window.size[0] // 2 + 8, 8), (window.size[0] // 2 - 16, window.size[1] - 16))
label = ui.Label(right, (8, 8), "Actions", font_med)
btn = ui.Button(right, (8, 40), "Do Thing", (120, 32), on_click=lambda b: print('Do Thing clicked'))

# Icon button
icon_surf = pygame.Surface((14, 14))
icon_surf.fill((40, 110, 200))
ib = ui.IconButton(right, (140, 40), icon_surf, size=(32, 32), on_click=lambda b: print('Icon clicked'))

# Dropdown
dd = ui.Dropdown(right, (8, 88), size=(200, 32), options=["One", "Two", "Three"], selected=0, on_select=lambda i, v: print('Dropdown ->', i, v))

# Status label
status = ui.Label(right, (8, 140), "Status: idle", font_small)

# Wire some interactions
btn.on('click', lambda *_: setattr(status, 'text', 'Status: busy'))

# Keyboard shortcuts for tab switching
def on_key(evt):
    if evt.type != pygame.KEYDOWN:
        return False
    if evt.key == pygame.K_1:
        left_tab.current = 0
        seg_tabs.selected = 0
        return True
    if evt.key == pygame.K_2:
        left_tab.current = 1
        seg_tabs.selected = 1
        return True
    if evt.key == pygame.K_3:
        left_tab.current = 2
        seg_tabs.selected = 2
        return True
    return False

window.event(pygame.KEYDOWN)(on_key)

# Animation for progress bars
@window.event('draw')
def frame(dt):
    # Occasional progress bump for demo
    progress.value  += 0.01
    progress2.value += 0.02
    if random.random() < 0.03:
        progress.value =  (progress.value  + random.random() * 6) % 100
        progress2.value = (progress2.value + random.random() * 3) % 100


window.mainloop()
