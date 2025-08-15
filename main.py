import engine as ui

window = ui.Window()

buttons = 99999

window.title = f"UI-Engine-V2 - Performance Test ({buttons+1:,} buttons)"

for i in range(buttons):
    ui.Button(
        window,
        (5 + i // 37 * 29.33, 5 + i % 37 * 16),
        f"{i+1}",
        (27, 14),
        corner_radius=2,
        font=(None, 21)
    )

window.debug = True

window.mainloop()
