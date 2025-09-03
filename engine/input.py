import pygame
from typing import Any
from .text import get_caret_index_at_x
from .window import Window
import clipboard

def _prev_word_index(s: str, idx: int) -> int:
    if not s or idx <= 0:
        return 0
    j = idx
    # skip whitespace to the left
    while j > 0 and s[j-1].isspace():
        j -= 1
    # skip non-whitespace (the previous word)
    while j > 0 and not s[j-1].isspace():
        j -= 1
    return j

def _next_word_index(s: str, idx: int) -> int:
    if not s:
        return 0
    n = len(s)
    j = idx
    # skip current word chars
    while j < n and not s[j].isspace():
        j += 1
    # skip whitespace to the start of next word
    while j < n and s[j].isspace():
        j += 1
    return j


class InputManager:
    """Centralized input handling for Input components.

    Components should call `input_manager.handle_event(component, event)` from
    their `_event` method. The manager will mutate component attributes
    (like `_value`, `_caret`, `_sel_start`, `_sel_end`, `_composition`,
    `_dragging`) and call `component.render()` when needed. It will also call
    `component.emit('submit', value)` and `component.on_enter` as appropriate.
    """

    def __init__(self, component, multiline: bool = False):
        # placeholder for future shared state
        self.last_focus = None
        self.component = component
        self.multiline = multiline

    def handle_event(self, event: pygame.event.Event) -> bool:
        comp = self.component
        # Ensure component has expected attributes with sensible default types
        defaults = {
            '_value': '',
            '_caret': 0,
            '_sel_start': 0,
            '_sel_end': 0,
            '_sel_anchor': None,
            '_placeholder': '',
            '_focused': False,
        }
        for attr, val in defaults.items():
            if not hasattr(comp, attr):
                setattr(comp, attr, val)

        # Mouse caret placement / double click / dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            ax, ay = comp.absolute_pos
            rel_x = mx - ax
            rel_y = my - ay
            if 0 <= rel_x < comp.size[0] and 0 <= rel_y < comp.size[1]:
                # manage focus: use Window._input_focus so focus is shared across components
                try:
                    # find window for this component
                    w = getattr(comp, 'window', None)
                    if w is None:
                        w = getattr(comp, 'parent', None)
                        while w is not None and not isinstance(w, Window):
                            w = getattr(w, 'parent', None)
                    
                    # Use the window's set_input_focus method to manage focus properly
                    if isinstance(w, Window):
                        w.set_input_focus(comp)
                    else:
                        # Fallback if we can't find the window
                        setattr(comp, '_focused', True)
                except Exception:
                    # Fallback if anything goes wrong
                    setattr(comp, '_focused', True)

                if not isinstance(comp._font, pygame.font.Font):
                    from .text import get_font
                    font = get_font(*comp._font)
                else:
                    font = comp._font

                clicks = getattr(event, 'clicks', 1)
                if clicks >= 2:
                    s = comp._value
                    if not s:
                        return True
                    # For multiline, find the clicked line and compute word selection there
                    if getattr(comp, 'multiline', False):
                        lines = s.split('\n')
                        # Visual layout constants must match Field.render
                        padding_x = 10
                        padding_y = 8
                        margin = 12
                        line_spacing = 1.2
                        line_h = font.size('T')[1]
                        # compute content offset y as in Field.render
                        if getattr(comp, '_scroll_y', 0) > 0:
                            content_offset_y = padding_y - int(getattr(comp, '_scroll_y', 0)) - margin
                        else:
                            content_offset_y = padding_y
                        # determine clicked line index
                        y_in_text = rel_y - content_offset_y
                        li = int(y_in_text / (line_h * line_spacing)) if line_h > 0 else 0
                        li = max(0, min(li, len(lines) - 1))
                        line_text = lines[li]
                        # compute x relative to the drawn text same as Field
                        if getattr(comp, '_scroll_x', 0) > 0:
                            content_offset_x = padding_x - int(getattr(comp, '_scroll_x', 0)) - margin
                        else:
                            content_offset_x = padding_x - int(getattr(comp, '_scroll_x', 0))
                        x_in_line = rel_x - content_offset_x
                        idx_in_line = get_caret_index_at_x(line_text, font, x_in_line)
                        # map to overall index
                        base = sum(len(l) + 1 for l in lines[:li])
                        idx = max(0, min(base + idx_in_line, len(s)))
                    else:
                        idx = get_caret_index_at_x(s, font, rel_x)
                    if idx > 0 and idx == len(s):
                        idx -= 1
                    start = idx
                    while start > 0 and not s[start - 1].isspace():
                        start -= 1
                    end = idx

                    while end < len(s) and not s[end].isspace():
                        end += 1
                    comp._sel_start, comp._sel_end = start, end
                    comp._caret = end
                    # set anchor to the start of the double-click selection
                    comp._sel_anchor = start
                    comp.render()
                    return True

                comp._dragging = True
                comp._composition = ''
                # For multiline, determine clicked line and map x to that line
                if getattr(comp, 'multiline', False):
                    lines = comp._value.split('\n')
                    padding_x = 10
                    padding_y = 8
                    margin = 12
                    line_spacing = 1.2
                    line_h = font.size('T')[1]
                    if getattr(comp, '_scroll_y', 0) > 0:
                        content_offset_y = padding_y - int(getattr(comp, '_scroll_y', 0)) - margin
                    else:
                        content_offset_y = padding_y
                    y_in_text = rel_y - content_offset_y
                    li = int(y_in_text / (line_h * line_spacing)) if line_h > 0 else 0
                    li = max(0, min(li, len(lines) - 1))
                    if getattr(comp, '_scroll_x', 0) > 0:
                        content_offset_x = padding_x - int(getattr(comp, '_scroll_x', 0)) - margin
                    else:
                        content_offset_x = padding_x - int(getattr(comp, '_scroll_x', 0))
                    x_in_line = rel_x - content_offset_x
                    idx_in_line = get_caret_index_at_x(lines[li], font, x_in_line)
                    base = sum(len(l) + 1 for l in lines[:li])
                    comp._caret = max(0, min(base + idx_in_line, len(comp._value)))
                else:
                    comp._caret = get_caret_index_at_x(comp._value, font, rel_x)
                comp._sel_start = comp._sel_end = comp._caret
                # set the selection anchor at the caret when starting a drag/click
                comp._sel_anchor = comp._caret
                comp.render()
                return True

        # Keyboard handling
        if event.type == pygame.KEYDOWN:
            # Guard clause: only handle keyboard events if this field is focused
            if not getattr(comp, '_focused', False):
                return False
                
            # Select all (Ctrl+A)
            if event.key == pygame.K_a and (event.mod & pygame.KMOD_CTRL):
                comp._sel_start = 0
                comp._sel_end = len(comp._value)
                comp._caret = comp._sel_end
                comp._sel_anchor = 0
                comp.render()
                return True

            # Copy
            if event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL) and comp._sel_start != comp._sel_end:
                a, b = sorted((comp._sel_start, comp._sel_end))
                piece = comp._value[a:b]
                try:
                    clipboard.copy(piece)
                except Exception:
                    pass
                return True

            # Cut
            if event.key == pygame.K_x and (event.mod & pygame.KMOD_CTRL) and comp._sel_start != comp._sel_end:
                a, b = sorted((comp._sel_start, comp._sel_end))
                piece = comp._value[a:b]
                try:
                    clipboard.copy(piece)
                except Exception:
                    pass
                comp._value = comp._value[:a] + comp._value[b:]
                comp._caret = a
                comp._sel_start = comp._sel_end = comp._caret
                comp._sel_anchor = None
                comp.render()
                return True

            # Paste
            if event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                try:
                    txt = ''
                    try:
                        val = clipboard.paste()
                        txt = '' if val is None else str(val)
                    except Exception:
                        txt = ''

                    # insert even if empty string (user expects paste action)
                    if comp._sel_start != comp._sel_end:
                        a, b = sorted((comp._sel_start, comp._sel_end))
                        comp._value = comp._value[:a] + txt + comp._value[b:]
                        comp._caret = a + len(txt)
                    else:
                        comp._value = comp._value[:comp._caret] + txt + comp._value[comp._caret:]
                        comp._caret += len(txt)
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                    comp.render()
                    return True
                except Exception:
                    pass

            # Backspace
            if event.key == pygame.K_BACKSPACE:
                ctrl = bool(event.mod & pygame.KMOD_CTRL)
                if comp._sel_start != comp._sel_end:
                    a, b = sorted((comp._sel_start, comp._sel_end))
                    comp._value = comp._value[:a] + comp._value[b:]
                    comp._caret = a
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                    comp.render()
                    return True
                # Ctrl+Backspace: delete previous word
                if ctrl and comp._caret > 0:
                    new_pos = _prev_word_index(comp._value, comp._caret)
                    comp._value = comp._value[:new_pos] + comp._value[comp._caret:]
                    comp._caret = new_pos
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                    comp.render()
                    return True

                # normal backspace: delete single char to the left
                if not ctrl and comp._caret > 0:
                    comp._value = comp._value[:comp._caret - 1] + comp._value[comp._caret:]
                    comp._caret -= 1
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                    comp.render()
                    return True

            # Delete
            if event.key == pygame.K_DELETE:
                ctrl = bool(event.mod & pygame.KMOD_CTRL)
                # If there's a selection, delete it first
                if comp._sel_start != comp._sel_end:
                    a, b = sorted((comp._sel_start, comp._sel_end))
                    comp._value = comp._value[:a] + comp._value[b:]
                    comp._caret = a
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                    comp.render()
                    return True

                # Ctrl+Delete: delete to next word boundary
                if ctrl and comp._caret < len(comp._value):
                    new_pos = _next_word_index(comp._value, comp._caret)
                    comp._value = comp._value[:comp._caret] + comp._value[new_pos:]
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                    comp.render()
                    return True

                # Normal delete: delete single character after caret
                if comp._caret < len(comp._value):
                    comp._value = comp._value[:comp._caret] + comp._value[comp._caret + 1:]
                    comp._sel_start = comp._sel_end = comp._caret
                    comp.render()
                    return True

            # Left arrow
            if event.key == pygame.K_LEFT:
                ctrl = bool(event.mod & pygame.KMOD_CTRL)
                shift = bool(event.mod & pygame.KMOD_SHIFT)
                if ctrl:
                    new_pos = _prev_word_index(comp._value, comp._caret)
                else:
                    new_pos = max(0, comp._caret - 1)
                if shift:
                    # Use explicit selection anchor if present; otherwise start one at the caret
                    anchor = comp._sel_anchor if getattr(comp, '_sel_anchor', None) is not None else comp._caret
                    # coerce anchor to int to avoid None being present
                    if anchor is None:
                        anchor = comp._caret
                    comp._caret = new_pos
                    a, b = sorted((anchor, comp._caret))
                    comp._sel_start, comp._sel_end = a, b
                    # keep the anchor while shift-selecting
                    comp._sel_anchor = anchor
                else:
                    comp._caret = new_pos
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                comp.render()
                return True

            # Up arrow (move caret up one visual line)
            if event.key == pygame.K_UP and getattr(self, 'multiline', False):
                shift = bool(event.mod & pygame.KMOD_SHIFT)
                # compute current line and column
                lines = comp._value.split('\n')
                pos = max(0, min(comp._caret, len(comp._value)))
                li = 0
                col = 0
                for i, ln in enumerate(lines):
                    if pos <= len(ln):
                        li = i
                        col = pos
                        break
                    pos -= (len(ln) + 1)
                else:
                    li = len(lines) - 1
                    col = len(lines[-1])
                # move up a line keeping column if possible
                new_li = max(0, li - 1)
                new_col = min(col, len(lines[new_li]))
                new_pos = sum(len(l) + 1 for l in lines[:new_li]) + new_col
                if shift:
                    anchor = comp._sel_anchor if getattr(comp, '_sel_anchor', None) is not None else comp._caret
                    if anchor is None:
                        anchor = comp._caret
                    comp._caret = new_pos
                    a, b = sorted((anchor, comp._caret))
                    comp._sel_start, comp._sel_end = a, b
                    comp._sel_anchor = anchor
                else:
                    comp._caret = new_pos
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                comp.render()
                return True

            # Down arrow (move caret down one visual line)
            if event.key == pygame.K_DOWN and getattr(self, 'multiline', False):
                shift = bool(event.mod & pygame.KMOD_SHIFT)
                lines = comp._value.split('\n')
                pos = max(0, min(comp._caret, len(comp._value)))
                li = 0
                col = 0
                for i, ln in enumerate(lines):
                    if pos <= len(ln):
                        li = i
                        col = pos
                        break
                    pos -= (len(ln) + 1)
                else:
                    li = len(lines) - 1
                    col = len(lines[-1])
                new_li = min(len(lines) - 1, li + 1)
                new_col = min(col, len(lines[new_li]))
                new_pos = sum(len(l) + 1 for l in lines[:new_li]) + new_col
                if shift:
                    anchor = comp._sel_anchor if getattr(comp, '_sel_anchor', None) is not None else comp._caret
                    if anchor is None:
                        anchor = comp._caret
                    comp._caret = new_pos
                    a, b = sorted((anchor, comp._caret))
                    comp._sel_start, comp._sel_end = a, b
                    comp._sel_anchor = anchor
                else:
                    comp._caret = new_pos
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                comp.render()
                return True

            # Right arrow
            if event.key == pygame.K_RIGHT:
                ctrl = bool(event.mod & pygame.KMOD_CTRL)
                shift = bool(event.mod & pygame.KMOD_SHIFT)
                if ctrl:
                    new_pos = _next_word_index(comp._value, comp._caret)
                else:
                    new_pos = min(len(comp._value), comp._caret + 1)
                if shift:
                    anchor = comp._sel_anchor if getattr(comp, '_sel_anchor', None) is not None else comp._caret
                    if anchor is None:
                        anchor = comp._caret
                    comp._caret = new_pos
                    a, b = sorted((anchor, comp._caret))
                    comp._sel_start, comp._sel_end = a, b
                    comp._sel_anchor = anchor
                else:
                    comp._caret = new_pos
                    comp._sel_start = comp._sel_end = comp._caret
                    comp._sel_anchor = None
                comp.render()
                return True

            # Enter / submit
            if event.key == pygame.K_RETURN:
                if self.multiline:
                    ch = '\n'
                    if comp._sel_start != comp._sel_end:
                        a, b = sorted((comp._sel_start, comp._sel_end))
                        comp._value = comp._value[:a] + ch + comp._value[b:]
                        comp._caret = a + len(ch)
                        comp._sel_start = comp._sel_end = comp._caret
                        comp.render()
                        return True

                    comp._value = comp._value[:comp._caret] + ch + comp._value[comp._caret:]
                    comp._caret += len(ch)
                    comp._sel_start = comp._sel_end = comp._caret
                    comp.render()
                    return True

                if callable(getattr(comp, 'on_enter', None)):
                    try:
                        comp.on_enter(comp._value)
                    except Exception:
                        pass
                try:
                    comp.emit('submit', comp._value)
                except Exception:
                    pass
                return True

            # Printable chars: when pygame provides TEXTINPUT events, prefer
            # using TEXTINPUT for text insertion to handle IME and avoid
            # duplicate characters (KEYDOWN + TEXTINPUT). Fall back to
            # KEYDOWN insertion when TEXTINPUT is not available.
            if not hasattr(pygame, 'TEXTINPUT'):
                if ch := event.unicode:
                    if comp._sel_start != comp._sel_end:
                        a, b = sorted((comp._sel_start, comp._sel_end))
                        comp._value = comp._value[:a] + ch + comp._value[b:]
                        comp._caret = a + len(ch)
                        comp._sel_start = comp._sel_end = comp._caret
                        comp.render()
                        return True
                    comp._value = comp._value[:comp._caret] + ch + comp._value[comp._caret:]
                    comp._caret += len(ch)
                    comp._sel_start = comp._sel_end = comp._caret
                    comp.render()
                    return True

        # TEXTINPUT (IME)
        if event.type == pygame.TEXTINPUT:
            # Guard clause: only handle text input if this field is focused
            if not getattr(comp, '_focused', False):
                return False
                
            if txt := getattr(event, 'text', ''):
                if comp._sel_start != comp._sel_end:
                    a, b = sorted((comp._sel_start, comp._sel_end))
                    comp._value = comp._value[:a] + txt + comp._value[b:]
                    comp._caret = a + len(txt)
                else:
                    comp._value = comp._value[:comp._caret] + txt + comp._value[comp._caret:]
                    comp._caret += len(txt)
                comp._sel_start = comp._sel_end = comp._caret
                comp.render()
                return True

        # Mouse drag selection
        if event.type == pygame.MOUSEMOTION and getattr(comp, '_dragging', False):
            mx, my = event.pos
            ax, ay = comp.absolute_pos
            rel_x = mx - ax
            rel_y = my - ay
            if not isinstance(comp._font, pygame.font.Font):
                from .text import get_font
                font = get_font(*comp._font)
            else:
                font = comp._font
            rel_x = max(0, min(rel_x, comp.size[0] - 1))
            # Map mouse position to caret index; handle multiline consistently
            if getattr(comp, 'multiline', False):
                lines = comp._value.split('\n')
                # Match Field.render constants
                padding_x = 10
                padding_y = 8
                margin = 12
                line_spacing = 1.2
                line_h = font.size('T')[1]
                # content offsets as in Field.render
                if getattr(comp, '_scroll_y', 0) > 0:
                    content_offset_y = padding_y - int(getattr(comp, '_scroll_y', 0)) - margin
                else:
                    content_offset_y = padding_y
                if getattr(comp, '_scroll_x', 0) > 0:
                    content_offset_x = padding_x - int(getattr(comp, '_scroll_x', 0)) - margin
                else:
                    content_offset_x = padding_x - int(getattr(comp, '_scroll_x', 0))
                y_in_text = rel_y - content_offset_y
                li = int(y_in_text / (line_h * line_spacing)) if line_h > 0 else 0
                li = max(0, min(li, len(lines) - 1))
                x_in_line = rel_x - content_offset_x
                idx_in_line = get_caret_index_at_x(lines[li], font, x_in_line)
                base = sum(len(l) + 1 for l in lines[:li])
                idx = max(0, min(base + idx_in_line, len(comp._value)))
            else:
                idx = get_caret_index_at_x(comp._value, font, rel_x)
            comp._sel_end = idx
            comp._caret = idx
            comp.render()
            return True

        if event.type == pygame.MOUSEBUTTONUP and (event.button == 1 and getattr(comp, '_dragging', False)):
            comp._dragging = False
            return True

        # Mouse wheel scrolling: vertical scroll by default, horizontal when Shift is held
        if event.type == getattr(pygame, 'MOUSEWHEEL', None):
            # Only scroll if mouse is over the component and it is focused
            try:
                mx, my = pygame.mouse.get_pos()
                ax, ay = comp.absolute_pos
                rel_x = mx - ax
                rel_y = my - ay
                if not (0 <= rel_x < comp.size[0] and 0 <= rel_y < comp.size[1]):
                    return False
            except Exception:
                return False

            # Determine modifier: Shift for horizontal scroll
            shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
            # Sensitivity: multiply wheel.y by a pixel amount (lines -> px)
            step = 20
            if shift:
                # horizontal scroll
                new_x = int(getattr(comp, '_scroll_x', 0) - event.y * step)
                comp._scroll_x = max(0, new_x)
            else:
                # vertical scroll
                new_y = int(getattr(comp, '_scroll_y', 0) - event.y * step)
                # respect component's max_scroll_y if it exists, otherwise clamp to 0..inf
                max_y = getattr(comp, '_max_scroll_y', None)
                if max_y is not None:
                    comp._scroll_y = max(0, min(new_y, int(max_y)))
                else:
                    comp._scroll_y = max(0, new_y)
            # mark that the user manually scrolled; this should persist until
            # the user moves the caret or edits text so auto-scroll doesn't override
            try:
                comp._user_scrolled = True
            except Exception:
                pass
            try:
                comp.render()
            except Exception:
                pass
            return True

        # TEXTEDITING (IME composition)
        if event.type == getattr(pygame, 'TEXTEDITING', None):
            comp._composition = getattr(event, 'text', '') or ''
            comp.render()
            return True

        return False

