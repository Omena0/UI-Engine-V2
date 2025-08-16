import engine as ui

window = ui.Window()

ui.Field(
    window,
    (0, 0),
    (None, 36),
    'hello'
)

window.debug = True

window.mainloop()
