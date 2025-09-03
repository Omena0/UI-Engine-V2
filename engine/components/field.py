from ..text import get_font, draw, render_selection, measure_caret_x
from ..input import InputManager
from .base import ComponentBase
from .. import theme
import pygame
import time


class Field(ComponentBase):
    __slots__ = [
        '_value', '_font', '_color', '_bg_color', '_caret',
        '_sel_start', '_sel_end', '_placeholder', 'on_enter',
        '_caret_visible', '_last_blink', '_dragging', '_composition',
        '_focused', '_scroll_x', '_scroll_y', '_sel_anchor', '_user_scrolled',
        'input_manager', '_prev_caret', '_prev_value', '_max_scroll_y',
        '_composite_surface', '_composite_dirty', '_last_child_count'
    ]

    def __init__(
            self, parent, pos, font,
            value='',
            color=(250,250,250),
            bg_color=None,
            placeholder='',
            on_enter=None,
            size=None,
            multiline=False
        ):
        self._value = value
        self._font = font
        self._color = color
        self._bg_color = bg_color
        self._caret = len(value)
        self._sel_start = 0
        self._sel_end = 0
        self._placeholder = placeholder
        self.on_enter = on_enter

        # caret blink state
        self._caret_visible = True
        self._last_blink = time.time()

        # horizontal scroll offset so caret is always visible
        self._scroll_x = 0

        # vertical scroll offset for multiline fields
        self._scroll_y = 0

        # focus state
        self._focused = False

        # dragging state for mouse selection
        self._dragging = False

        # IME composition text (if any)
        self._composition = ''

        if size is None:
            size = (150, 50)

        if not isinstance(self._font, pygame.font.Font):
            self._font = get_font(*self._font)

        self.input_manager = InputManager(self, multiline)

        # time of last manual user scroll (wheel) to avoid auto-scroll fighting user
        self._user_scrolled = 0

        super().__init__(parent, pos, size)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self.render()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, f):
        self._font = f
        self.render()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        self._color = c
        self.render()

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, c):
        self._bg_color = c
        self.render()

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, p):
        self._placeholder = p
        self.render()

    @property
    def multiline(self):
        return self.input_manager.multiline

    @multiline.setter
    def multiline(self, v):
        self.input_manager.multiline = v


    def render(self):
        surf = self.surface

        # Ultra-simplified field styling for performance
        radius = 8
        padding_x = 10
        padding_y = 8

        bg_color_draw = theme.get('field_bg')
        effective_text_color = theme.get('field_text')
        border_col = theme.get('field_border')
        accent = theme.get('accent')

        focused = getattr(self, '_focused', False)

        # Single draw approach: just background with colored border based on focus
        if focused:
            final_border = accent or (80, 150, 255)
        else:
            final_border = border_col or (200, 200, 200)

        # One draw for border, one for background
        pygame.draw.rect(surf, final_border, (0, 0, *self.size), border_radius=radius)
        if focused:
            pygame.draw.rect(surf, bg_color_draw, (2, 2, self.size[0]-4, self.size[1]-4), border_radius=max(0, radius-2))
        else:
            pygame.draw.rect(surf, bg_color_draw, (1, 1, self.size[0]-2, self.size[1]-2), border_radius=max(0, radius-1))

        if not isinstance(self._font, pygame.font.Font):
            font = get_font(*self._font)
        else:
            font = self._font

    # determine text and color. Render placeholder separately so it does
    # not affect caret measurement/placement.
        placeholder_text = self._placeholder
        value_text = self._value

        # whether the field currently has no user-visible characters
        is_empty = (value_text == '')
        if self._bg_color is not None:
            value_color = self._color
        else:
            value_color = effective_text_color
            placeholder_color = (120, 120, 120)

        # choose caret color: accent when focused, else strong readable color
        caret_color = (80, 150, 255) if focused else effective_text_color

        # If empty and not focused, draw placeholder and skip caret/selection
        if is_empty and not focused and placeholder_text:
            ph_surf = font.render(placeholder_text, True, placeholder_color)
            surf.blit(ph_surf, (padding_x, padding_y))
            # finalize blits
            self.blits = [(self._surface, self.absolute_pos)]
            for child in self.children:
                text_x = padding_x - int(getattr(self, '_scroll_x', 0))
                child.render()
                self.blits.extend(child.blits)
            return

        # prepare text and ensure caret is visible by adjusting horizontal scroll
        text = value_text

        # caret blink toggle
        if time.time() - self._last_blink > 0.5:
            self._caret_visible = not self._caret_visible
            self._last_blink = time.time()

        if self.multiline:
            lines = text.split('\n')
            pos = max(0, min(self._caret, len(text)))
            line_index = 0
            col = 0
            for i, ln in enumerate(lines):
                if pos <= len(ln):
                    line_index = i
                    col = pos
                    line_text = ln
                    break
                pos -= (len(ln) + 1)
            else:
                line_index = len(lines) - 1
                line_text = lines[-1]
                col = len(line_text)
            caret_x = measure_caret_x(line_text, font, col)
            # compute caret position (line/column) and update horizontal scroll so caret is visible
            line_spacing = 1.2
            caret_y = int(line_index * font.size(line_text)[1] * line_spacing)
        else:
            caret_x = measure_caret_x(text, font, self._caret)
            caret_y = 0

        content_width = self.size[0] - padding_x * 2

        # compute widest line so we can clamp horizontal scroll
        lines_for_width = text.split('\n') if text else ['']
        try:
            max_line_w = max(font.size(ln)[0] for ln in lines_for_width)
        except Exception:
            max_line_w = content_width

        # Maximum scroll so the rightmost edge of text is at the middle of the content area
        max_scroll_x = max(0, int(max_line_w - content_width / 2))

        # Only auto-scroll to keep caret visible when the field is focused.
        # Prevents the field from appearing pre-scrolled on initial render.
        # If the user manually scrolled, keep that until the user moves the
        # caret or edits the text. Detect caret/value changes across renders
        # and clear the manual-scroll lock when a change is detected.
        if getattr(self, '_user_scrolled', False):
            prev_caret = getattr(self, '_prev_caret', None)
            prev_value = getattr(self, '_prev_value', None)
            if prev_caret != self._caret or prev_value != self._value:
                self._user_scrolled = False

        if focused and not getattr(self, '_user_scrolled', False):
            if caret_x - self._scroll_x < 0:
                self._scroll_x = max(0, caret_x - 8)
            elif caret_x - self._scroll_x > content_width:
                self._scroll_x = caret_x - content_width + 8
        # clamp horizontal scroll to sensible bounds
        self._scroll_x = max(0, min(int(getattr(self, '_scroll_x', 0)), max_scroll_x))

        # draw text shifted by scroll offset so caret is visible
        text_x = padding_x - int(self._scroll_x)

        # clip drawing to the inner content area to avoid drawing over rounded border
        content_height = max(1, self.size[1] - padding_y * 2)
        inner_rect = pygame.Rect(padding_x, padding_y, content_width, content_height)
        prev_clip = surf.get_clip()
        surf.set_clip(inner_rect)

        # margin so characters/lines slightly outside the content area are still rendered
        margin = 12
        # don't shift left when not scrolled; only apply horizontal margin when there's a scroll
        if getattr(self, '_scroll_x', 0) > 0:
            content_offset_x = text_x - margin
        else:
            content_offset_x = text_x

        # compute total text height so we request a draw surface tall enough to contain
        # the rendered lines (prevents bottom lines from being dropped when scrolled)
        if self.multiline:
            lines_all = text.split('\n') if text else ['']
            # line height using font metrics; use a consistent line spacing factor
            line_h = font.size('T')[1]
            line_spacing = 1.2
            total_text_height = int(len(lines_all) * line_h * line_spacing)
        else:
            total_text_height = font.size(text)[1] if text else font.size('T')[1]

    # render text using the fast cached draw function and blit it shifted by scroll
        # request a larger width/height so we can shift the blit and still keep pixels
        extra_h = font.size('T')[1] if hasattr(font, 'size') else 0
        # draw height should include visible content height, extra line gap and margins
        draw_height = max(content_height + int(extra_h) + margin * 2, total_text_height + margin * 2, content_height + int(getattr(self, '_scroll_y', 0)))
        # choose draw width large enough to contain the longest line so right-side
        # characters don't get dropped when scrolled.
        draw_width = max(content_width + margin * 2 + int(getattr(self, '_scroll_x', 0)), max_line_w + margin * 2)
        text_surf = draw(text, font, value_color, self._bg_color, width=draw_width, height=draw_height)

        # compute maximum vertical scroll so the user cannot scroll indefinitely.
        # We choose a max that allows the caret to be centered in the content area
        # when at the bottom: max_scroll_y = total_text_height - content_height/2
        try:
            max_scroll_y = max(0, int(total_text_height - (content_height // 2)))
        except Exception:
            max_scroll_y = max(0, int(getattr(self, '_scroll_y', 0)))
        # expose for input handlers to clamp wheel updates
        self._max_scroll_y = max_scroll_y

        # Vertical autoscroll: when multiline and focused, keep the caret
        # approximately in the middle of the content area unless the user
        # manually scrolled with the wheel. Compute desired scroll and clamp it.
        if self.multiline and focused and not getattr(self, '_user_scrolled', False):
            try:
                # character/line height and caret top/bottom in text coordinate space
                line_h = font.size('T')[1]
                caret_top = caret_y
                caret_bottom = caret_y + line_h
                # compute visible text area in text coordinates (relative to text origin)
                current_text_top = int(getattr(self, '_scroll_y', 0))
                visible_top = current_text_top
                visible_bottom = current_text_top + content_height
                # only autoscroll when caret is not fully visible
                if caret_bottom > visible_bottom:
                    # scroll the minimal amount so the caret_bottom is visible
                    delta = caret_bottom - visible_bottom
                    self._scroll_y = min(int(getattr(self, '_scroll_y', 0)) + int(delta), max_scroll_y)
                elif caret_top < visible_top:
                    # scroll up minimally so caret_top becomes visible
                    delta = visible_top - caret_top
                    self._scroll_y = max(int(getattr(self, '_scroll_y', 0)) - int(delta), 0)
            except Exception:
                pass

        # clamp current scroll to sensible bounds before using it
        self._scroll_y = max(0, min(int(getattr(self, '_scroll_y', 0)), max_scroll_y))

        # vertical content offset: apply scroll and a top margin when scrolled so
        # partially-visible lines render smoothly and are clipped by inner_rect
        if getattr(self, '_scroll_y', 0) > 0:
            content_offset_y = padding_y - int(getattr(self, '_scroll_y', 0)) - margin
        else:
            content_offset_y = padding_y

        # draw selection first using content offsets
        if self._sel_start != self._sel_end:
            render_selection(surf, text, self._sel_start, self._sel_end, font, (50, 100, 200), content_offset_x, content_offset_y, line_spacing=1.2)

        surf.blit(text_surf, (content_offset_x, content_offset_y))

        # draw caret on top of text when focused
        if self._caret_visible and focused:
            if self.multiline:
                # character height for caret; use the base line height
                ch = font.size(line_text)[1]
                caret_rect = pygame.Rect(int(content_offset_x + caret_x), int(content_offset_y + caret_y), 2, ch)
            else:
                ci = max(0, min(self._caret, len(text)))
                cx = measure_caret_x(text, font, ci)
                ch = font.size(text)[1]
                caret_rect = pygame.Rect(int(content_offset_x + cx), int(content_offset_y), 2, ch)
            pygame.draw.rect(surf, caret_color, caret_rect)

        # draw IME composition (underlined) at caret position if present
        if getattr(self, '_composition', None):
            comp = self._composition
            comp_surf = font.render(comp, True, (80, 80, 80))
            if self.multiline:
                # compute line index and index within the line
                lines = text.split('\n')
                pos = max(0, min(self._caret, len(text)))
                li = 0
                for li, ln in enumerate(lines):
                    if pos <= len(ln):
                        col = pos
                        line_text = ln
                        break
                    pos -= (len(ln) + 1)
                else:
                    li = len(lines) - 1
                    line_text = lines[-1]
                    col = len(line_text)
                cx = measure_caret_x(line_text, font, col)
                ly = int(li * font.size(line_text)[1] * 1.2)
                surf.blit(comp_surf, (int(content_offset_x + cx), int(content_offset_y + ly)))
                underline_rect = pygame.Rect(int(content_offset_x + cx), int(content_offset_y + ly + font.size(line_text)[1] - 2), comp_surf.get_width(), 2)
            else:
                cx = measure_caret_x(text, font, self._caret)
                surf.blit(comp_surf, (int(content_offset_x + cx), int(content_offset_y)))
                underline_rect = pygame.Rect(int(content_offset_x + cx), int(content_offset_y + font.size(text)[1] - 2), comp_surf.get_width(), 2)
            pygame.draw.rect(surf, (80, 80, 80), underline_rect)
        # restore clip so subsequent drawing isn't clipped
        surf.set_clip(prev_clip)

        # finalize blits
        self.blits = [(self._surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

        # remember caret/value for next render so we can detect user edits
        self._prev_caret = self._caret
        self._prev_value = self._value

    def _event(self, event: pygame.event.Event) -> bool:
        handled = False
        try:
            handled = self.input_manager.handle_event(event)
        except Exception:
            handled = False
        return True if handled else super()._event(event)


