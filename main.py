import engine as ui

with open('bee.txt') as f:
    text = f.read(2048).replace('\n', ' ')

window = ui.Window()

@window.event('draw')
def draw(frame):
    pos = ui.pygame.mouse.get_pos()
    surf = ui.text.draw_text(
        text,
        (None, 36, True),
        (255,255,255),
        (0,0,0),
        width=pos[0],
        height=pos[1]
    )

    window.surface.blit(surf, (0, 0))

window.mainloop()
