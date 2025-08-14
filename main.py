import engine as ui

window = ui.Window()

for i in range(999):
    ui.Button(
        window,
        (5 + i // 37 * 29.33, 5 + i % 37 * 16),
        f"{i+1}",
        (27, 14),
        corner_radius=2,
        font=(None, 21)
    )


window.mainloop()
