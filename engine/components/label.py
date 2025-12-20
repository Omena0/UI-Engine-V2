from .base import ComponentBase
from .. import theme
from .. import text


class Label(ComponentBase):
    __slots__ = ['_text', '_font', '_ov_color', '_ov_bg_color', '_size', '_line_spacing', '_wrap', '_composite_surface', '_composite_dirty', '_last_child_count']

    def __init__(
        self, parent, pos, text, font,
        color=None, bg_color=None,
        size=None, max_width=500, max_height=300,
        line_spacing=1.2, wrap=True
    ):
        self._text = text
        self._font = font
        # store overrides; resolve actual colors in render() so theme updates apply
        self._ov_color = color
        self._ov_bg_color = bg_color
        # allow explicit size override, else use legacy max_width/max_height
        self._size = size if size is not None else (max_width, max_height)
        self._line_spacing = line_spacing
        self._wrap = wrap

        super().__init__(parent, pos, self._size)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.render()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        self.render()

    @property
    def color(self):
        return self._ov_color if self._ov_color is not None else theme.get('label_text')

    @color.setter
    def color(self, value):
        self._ov_color = value
        self.render()

    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get('label_bg')

    @bg_color.setter
    def bg_color(self, value):
        self._ov_bg_color = value
        self.render()

    @property
    def line_spacing(self):
        return self._line_spacing

    @line_spacing.setter
    def line_spacing(self, value):
        self._line_spacing = value
        self.render()

    @property
    def wrap(self):
        return self._wrap

    @wrap.setter
    def wrap(self, value):
        self._wrap = value
        self.render()

    def render(self):
        if self._wrap:
            self._surface = text.draw_justified(
                self.text, self.font, self.color, self.bg_color,
                *self.size, self._line_spacing
            )

        else:
            self._surface = text.draw(
                self.text, self.font, self.color, self.bg_color,
                *self.size, self._line_spacing
            )

        self.blits = [(self._surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


