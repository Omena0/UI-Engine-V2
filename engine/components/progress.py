from .base import ComponentBase
from .. import theme
import pygame
import math


class ProgressBar(ComponentBase):
    __slots__ = [
        "_size",
        "_value",
        "_max",
        "_ov_bg_color",
        "_ov_fg_color",
        "_ov_knob_color",
        "_corner_radius",
        "_progress_display",
        "_progress_target",
        "_progressive",
        "_progress_rate",
        "_min_progress_rate",
        "_progress_slowdown",
        "_last_tick",
        "_last_rendered_fill",
        "_last_rendered_fill_float",
        "_last_rendered_width",
        "_last_rendered_height",
        "_last_rendered_target",
        "_composite_surface",
        "_composite_dirty",
        "_last_child_count",
    ]

    def __init__(
        self,
        parent,
        pos,
        size=(200, 18),
        value=0,
        max_value=100,
        bg_color=None,
        fg_color=None,
        knob_color=None,
        corner_radius=4,
    ):
        # store overrides; resolve actual colors in render() so theme updates apply
        self._size = size
        self._value = float(value)
        self._max = float(max_value)
        self._ov_bg_color = bg_color
        self._ov_fg_color = fg_color
        self._ov_knob_color = knob_color
        self._corner_radius = corner_radius

        # progressive smoothing defaults
        self._progress_display = float(value)
        self._progress_target = float(value)

        self._progressive = False  # Disable progressive animation for render-on-change system
        # units per second base rate; actual rate will be divided by (1 + slowdown*distance)
        self._progress_rate = 10
        # minimum forward progress units per second when target > display
        self._min_progress_rate = 2.0

        # slowdown coefficient (higher => more slowdown when far away)
        self._progress_slowdown = 0.01
        self._last_tick = None
        self._last_rendered_fill = -1
        self._last_rendered_fill_float = -9999.0
        self._last_rendered_width = -1
        self._last_rendered_height = -1
        self._last_rendered_target = -9999.0

        super().__init__(parent, pos, self._size)

        @self.window.event('draw')
        def _handler(frame):
            dt_ms = self.window.dt
            dt = max(0.0, dt_ms / 1000.0)
            self._frame_progress_update(dt)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: float):
        v = max(0.0, min(round(v, 2), self._max))
        if v == self._value:
            return
        self._value = v
        # set target for progressive mode
        self._progress_target = float(self._value)
        # In render-on-change system, update display immediately if not progressive
        if not self._progressive:
            self._progress_display = float(self._value)
        self.emit("change", self._value)
        # ensure at least one render is scheduled
        self.render()

    # Resolved at render time so theme updates propagate immediately
    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get("progress_bg")

    @property
    def fg_color(self):
        return self._ov_fg_color if self._ov_fg_color is not None else theme.get("progress_fg")

    @property
    def knob_color(self):
        return self._ov_knob_color if self._ov_knob_color is not None else theme.get("progress_knob")

    @property
    def corner_radius(self):
        return self._corner_radius

    # progressive mode configuration helpers
    @property
    def progressive(self) -> bool:
        return self._progressive

    @progressive.setter
    def progressive(self, enabled: bool) -> None:
        """Enable/disable progressive smoothing. When enabled the visible
        progress will ease towards the target value over time.
        """
        self._progressive = enabled
        # reset timing so smoothing starts cleanly
        self._last_tick = None

    @property
    def progress_rate(self) -> float:
        """Base units-per-second rate used for smoothing."""
        return self._progress_rate

    @progress_rate.setter
    def progress_rate(self, v: float) -> None:
        self._progress_rate = v

    @property
    def progress_slowdown(self) -> float:
        """Slowdown coefficient (higher => more slowdown when far from target)."""
        return self._progress_slowdown

    @progress_slowdown.setter
    def progress_slowdown(self, v: float) -> None:
        self._progress_slowdown = v

    @property
    def min_progress_rate(self) -> float:
        """Minimum units-per-second forward drift when target is ahead."""
        return self._min_progress_rate

    @min_progress_rate.setter
    def min_progress_rate(self, v: float) -> None:
        self._min_progress_rate = max(0.0, v)

    def render(self) -> None:
        bg = self.bg_color or (230, 230, 230)
        fg = self.fg_color or (40, 110, 200)

        w, h = self.size
        surf = self.surface  # Cache surface reference

        # Skip transparent fill - draw background directly
        try:
            pygame.draw.rect(surf, bg, (0, 0, w, h), border_radius=self.corner_radius)
        except Exception:
            surf.fill(bg)

        # draw the current display fraction (may be updated by frame handler)
        frac = (self._progress_display / self._max) if self._max != 0 else 0.0
        if frac > 0:
            # Simplified rendering - just integer pixels for better performance
            fill_width = max(1, int(frac * w))
            if fill_width > 0:
                pygame.draw.rect(surf, fg, (0, 0, fill_width, h), border_radius=self.corner_radius)

        # build blits consistently with other components
        self.blits = [(surf, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

    def _frame_progress_update(self, dt: float) -> None:
        """Called every frame from the Window draw event handler. dt is seconds."""
        if not self._progressive:
            # ensure display stays in sync when progressive disabled
            self._progress_display = float(self._value)
            return

        # perform smoothing step using exponential easing so the visible value
        # smoothly approaches the target in a frame-rate independent way.
        dist = self._progress_target - self._progress_display
        if abs(dist) <= 1e-6:
            return

        # compute responsiveness: higher progress_rate => faster easing
        # apply slowdown based on proximity: when the display approaches the
        # target (small normalized distance) the slowdown factor increases so
        # the easing decelerates smoothly instead of stopping abruptly.
        try:
            norm_den = max(1.0, float(self._max))
        except Exception:
            norm_den = 1.0
        norm_dist = min(1.0, abs(dist) / norm_den)
        # slowdown factor grows as norm_dist -> 0 (near target)
        slowdown_factor = 1.0 + self._progress_slowdown * (1.0 - norm_dist)
        effective_rate = self._progress_rate / max(1e-6, slowdown_factor)
        time_constant = 1.0 / max(1e-6, effective_rate)
        # smoothing factor alpha = 1 - exp(-dt / time_constant)
        try:
            alpha = 1.0 - math.exp(-dt / time_constant)
        except Exception:
            alpha = min(1.0, max(0.0, self._progress_rate * dt))

        # apply easing (clamp to avoid overshoot)
        new_display = self._progress_display + dist * alpha

        # enforce a minimum forward rate so the bar keeps moving during long
        # pauses even when exponential alpha is tiny. Only apply when target
        # is ahead (we're moving forward).
        if dist > 0.0:
            # compute a minimum forward change but cap it to a fraction of the
            # remaining distance so we don't prevent natural deceleration.
            per_frame_min = self._min_progress_rate * dt
            cap = max(0.0, dist * 0.5)
            min_change = min(per_frame_min, cap)
            actual_change = new_display - self._progress_display
            if actual_change < min_change:
                # clamp to min_change but don't overshoot the target
                new_display = self._progress_display + min(min_change, dist)

        # if we're within one tiny unit, snap to target to avoid infinite tail
        if abs(self._progress_target - new_display) < 1e-3:
            new_display = float(self._progress_target)

        self._progress_display = new_display

        # determine whether to re-render: do so only when displayed fill
        # changes by >= 1.0 fractional pixels (avoid integer-rounding stutter)
        try:
            w, h = self.size
            float_fill = (
                (self._progress_display / self._max) * w
                if self._max != 0
                else 0.0
            )
        except Exception:
            float_fill = -9999.0

        # If we're still easing toward the target, render every frame so
        # the visual movement is smooth even if it lags behind the logical value.
        if abs(self._progress_target - self._progress_display) > 1e-6:
            try:
                self._extracted_from__frame_progress_update_58(float_fill)
            except Exception:
                pass
        elif abs(float_fill - (self._last_rendered_fill_float or -9999.0)) >= 0.5:
            try:
                self._extracted_from__frame_progress_update_58(float_fill)
            except Exception:
                pass

    # TODO Rename this here and in `_frame_progress_update`
    def _extracted_from__frame_progress_update_58(self, float_fill):
        self._last_rendered_fill_float = float_fill
        self._last_rendered_fill = int(max(0, float_fill))
        self.render()


__all__ = ["ProgressBar"]


