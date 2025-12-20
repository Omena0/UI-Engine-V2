import engine as ui

with open('bee.txt') as f:
    text = f.read(6100).replace('\n', ' ')

window = ui.Window()

old_pos = (0,0)
@window.every(50)
def mouse_move():
    global old_pos
    pos = ui.pygame.mouse.get_pos()
    if pos == old_pos:
        return
    old_pos = pos

    print(pos)
    surf = ui.text.draw_text(
        text,
        (None, 15),
        (255,255,255),
        (0,0,0),
        width=pos[0],
        height=pos[1]
    )

    window._blits.clear()
    window.blit(surf, (0, 0))

window.debug = True

window.mainloop()
