import pygame

fontCache = {}
def get_font(font_name, size, bold=False, italic=False) -> pygame.font.Font:
    key = (font_name, size, bold, italic)
    if key not in fontCache:
        font = pygame.font.SysFont(font_name, size, bold=bold, italic=italic)
        fontCache[key] = font
    return fontCache[key]

# --- Added: default per-letter spacing + helpers ---
DEFAULT_LETTER_SPACING = 1  # px to insert between letters by default
MAX_LETTER_EXTRA = 2  # maximum extra px allowed per-letter-gap

# Caches for rendered surfaces to avoid re-rendering identical lines/words
LINE_RENDER_CACHE: dict = {}
WORD_RENDER_CACHE: dict = {}

# Toggle to enable/disable rendering caches (useful for testing/debugging or
# when memory usage must be minimized)
CACHE_ENABLED = True

# Cache for split_text results (layout) and for fully rendered justified surfaces
SPLIT_TEXT_CACHE: dict = {}
DRAW_JUSTIFIED_SURF_CACHE: dict = {}

def _font_id_key(font):
    return id(font) if isinstance(font, pygame.font.Font) else tuple(font)


# --- Text input helpers: caret measurement, hit-testing, and rendering ---
def measure_caret_x(text: str, font: pygame.font.Font, index: int) -> int:
    """Return x offset in pixels of caret positioned at `index` in `text`.

    Index 0 -> before first char. Index == len(text) -> after last char.
    Uses per-character widths plus DEFAULT_LETTER_SPACING between characters.
    """
    # Use the font's measured width for the substring up to `index` so the
    # caret matches exactly where the text is rendered (handles kerning).
    if not text or index <= 0:
        return 0
    # clamp index
    idx = max(0, min(index, len(text)))
    return font.size(text[:idx])[0]

def get_caret_index_at_x(text: str, font: pygame.font.Font, x: int) -> int:
    """Return the caret index corresponding to pixel x within the rendered text.

    Chooses the closest caret position between characters.
    """
    if x <= 0:
        return 0
    # Walk measuring substring widths to find the closest caret position.
    prev_w = 0
    for i in range(1, len(text) + 1):
        w = font.size(text[:i])[0]
        mid = (prev_w + w) / 2.0
        if x < mid:
            return i - 1
        prev_w = w
    return len(text)

def render_line_with_caret(surf: pygame.Surface, text: str, caret_index: int, font: pygame.font.Font, color, bg_color, x: int, y: int, caret_color=(30, 30, 32), caret_width=2, caret_visible=True):
    """Render a single-line `text` onto `surf` at (x,y) and draw caret at caret_index.

    Uses a single font.render for the full line for speed, computes caret x using
    `measure_caret_x` and draws a vertical rect as caret when `caret_visible`.
    """
    # Render the full line (fast)
    line_surf = font.render(text, True, color, bg_color)
    surf.blit(line_surf, (x, y))

    if caret_visible:
        # clamp caret_index to valid range (0..len(text)). If out-of-range,
        # avoid drawing a caret to prevent spurious geometry.
        if caret_index is None:
            return
        caret_index = max(0, min(caret_index, len(text)))
        cx = x + measure_caret_x(text, font, caret_index)
        ch = font.size(text)[1]
        caret_rect = pygame.Rect(int(cx), y, caret_width, ch)
        pygame.draw.rect(surf, caret_color, caret_rect)

def render_selection(surf: pygame.Surface, text: str, sel_start: int, sel_end: int, font: pygame.font.Font, sel_color, x: int, y: int, line_spacing: float = 1.2):
    """Render selection background between sel_start and sel_end.

    Supports selections spanning multiple lines (explicit newlines in `text`).
    Draws one rect per-line for the portion of the selection that falls on
    that line. `x,y` are the top-left coordinates where the text was drawn.
    """
    if sel_start == sel_end:
        return
    if sel_start > sel_end:
        sel_start, sel_end = sel_end, sel_start

    # Split lines and iterate to draw per-line selection rectangles.
    lines = text.split('\n')
    base = 0
    for i, line in enumerate(lines):
        line_start = base
        line_end = base + len(line)
        # selection overlap on this line (exclusive end)
        a = max(sel_start, line_start)
        b = min(sel_end, line_end)
        if a < b:
            # local indices within this line
            local_a = a - line_start
            local_b = b - line_start
            start_x = x + measure_caret_x(line, font, local_a)
            end_x = x + measure_caret_x(line, font, local_b)
            h = font.size(line)[1]
            y_line = int(y + i * h * line_spacing)
            rect = pygame.Rect(int(start_x), y_line, int(end_x - start_x), h)
            pygame.draw.rect(surf, sel_color, rect)
        # advance base for next line (account for newline char)
        base = line_end + 1

def _font_cache_key(font, color, bg_color):
    # font may be a pygame.font.Font instance or a tuple accepted by get_font
    font_id = id(font) if isinstance(font, pygame.font.Font) else tuple(font)
    return (font_id, tuple(color) if isinstance(color, (list, tuple)) else color, tuple(bg_color) if isinstance(bg_color, (list, tuple)) else bg_color)

def draw(text, font, color, bg_color=None, width=300, height=200, line_spacing=1.2):
    """Fast cached draw

    This renders each input line (split on explicit newlines) using a single
    font.render call per line and returns a Surface sized to (width, height).
    Uses a simple per-line cache to avoid re-rendering identical lines with the
    same font/color/bg.
    """
    if not isinstance(font, pygame.font.Font):
        font = get_font(*font)

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    y = 0
    fkey_base = _font_cache_key(font, color, bg_color)
    for raw_line in text.split('\n'):
        line_h = font.size(raw_line)[1]
        if y + int(line_h * line_spacing) > height:
            break

        cache_key = (raw_line, fkey_base)
        line_surf = LINE_RENDER_CACHE.get(cache_key) if CACHE_ENABLED else None
        if line_surf is None:
            # render the whole line at once (fast)
            line_surf = font.render(raw_line, True, color, bg_color)
            if CACHE_ENABLED:
                LINE_RENDER_CACHE[cache_key] = line_surf

        surf.blit(line_surf, (0, int(y)))
        y += int(line_h * line_spacing)

    return surf

def draw_justified(text, font, color, bg_color=None, width=300, height=200, line_spacing=1.2):
    """Draw with wrapping/justification using `split_text` to compute layout.

    This function caches rendered words and full lines (when no extra spacing
    adjustments are required) to reduce rendering overhead. Where letter-level
    spacing extras are present, it falls back to character rendering to preserve
    behavior.
    """
    if not isinstance(font, pygame.font.Font):
        font = get_font(*font)

    # Attempt to reuse a fully rendered surface for identical inputs
    cache_draw_key = (text, _font_id_key(font), tuple(color) if isinstance(color, (list, tuple)) else color,
                      tuple(bg_color) if isinstance(bg_color, (list, tuple)) else bg_color,
                      width, height, line_spacing)
    if CACHE_ENABLED:
        cached_surf = DRAW_JUSTIFIED_SURF_CACHE.get(cache_draw_key)
        if cached_surf is not None:
            return cached_surf.copy()

    # Cache the split_text/layout result to avoid recomputing layout every frame
    split_key = (text, _font_id_key(font), width)
    lines = SPLIT_TEXT_CACHE.get(split_key) if CACHE_ENABLED else None
    if lines is None:
        lines = split_text(text, font, width)
        if CACHE_ENABLED:
            SPLIT_TEXT_CACHE[split_key] = lines

    surf = pygame.Surface(get_total_size(lines, font, line_spacing), pygame.SRCALPHA)

    y = 0
    fkey_base = _font_cache_key(font, color, bg_color)
    for line, space_info, letter_spacings in lines:
        line_h = font.size(line)[1]
        if y + int(line_h * line_spacing) > height:
            break

        # If no special spacing, render the whole line as one surface (cacheable)
        if space_info == 0 and not letter_spacings:
            cache_key = (line, fkey_base)
            line_surf = LINE_RENDER_CACHE.get(cache_key) if CACHE_ENABLED else None
            if line_surf is None:
                line_surf = font.render(line, True, color, bg_color)
                if CACHE_ENABLED:
                    LINE_RENDER_CACHE[cache_key] = line_surf
            surf.blit(line_surf, (0, int(y)))
            y += int(line_h * line_spacing)
            continue

        # Handle justified cases
        if isinstance(space_info, tuple):
            if space_info[0] == 'words':
                _, per_space, remainder, letter_gap_extras = space_info
                words = line.split(' ')
                x = 0
                # consume per-letter extras across the words; if letter_gap_extras present,
                # we attempt to render whole words (cached). If per-letter extras exist for
                # a word, we fall back to render_word_per_char for that word only.
                letter_idx = 0
                for gi, w in enumerate(words):
                    if w:
                        n = max(len(w) - 1, 0)
                        extras_for_word = letter_gap_extras[letter_idx:letter_idx + n] if letter_gap_extras else []
                        if extras_for_word:
                            # fallback: preserve previous per-char rendering when needed
                            x = render_word_per_char(surf, w, x, int(y), font, color, bg_color, extras_for_word)
                        else:
                            # use cached whole-word surface
                            w_key = (w, fkey_base)
                            w_surf = WORD_RENDER_CACHE.get(w_key) if CACHE_ENABLED else None
                            if w_surf is None:
                                w_surf = font.render(w, True, color, bg_color)
                                if CACHE_ENABLED:
                                    WORD_RENDER_CACHE[w_key] = w_surf
                            surf.blit(w_surf, (x, int(y)))
                            x += w_surf.get_width()
                        letter_idx += n
                    if gi < len(words) - 1:
                        add = font.size(' ')[0] + per_space + (1 if gi < remainder else 0)
                        x += add
                y += int(line_h * line_spacing)
                continue
            elif space_info[0] == 'pad':
                _, extra = space_info
                # draw the word and advance by extra to match width
                if line:
                    # single-word line; letter_spacings may be present too but handled below
                    cache_key = (line, fkey_base)
                    line_surf = LINE_RENDER_CACHE.get(cache_key) if CACHE_ENABLED else None
                    if line_surf is None:
                        line_surf = font.render(line, True, color, bg_color)
                        if CACHE_ENABLED:
                            LINE_RENDER_CACHE[cache_key] = line_surf
                    surf.blit(line_surf, (0, int(y)))
                y += int(line_h * line_spacing)
                continue

        if letter_spacings:
            # single-word explicit letter_spacings: must render per-character to apply gaps
            x = 0
            gap_idx = 0
            for ch in line:
                ch_surf = font.render(ch, True, color, bg_color)
                surf.blit(ch_surf, (x, int(y)))
                x += ch_surf.get_width()
                if gap_idx < len(letter_spacings):
                    x += DEFAULT_LETTER_SPACING + letter_spacings[gap_idx]
                    gap_idx += 1
            y += int(line_h * line_spacing)
            continue

        # Fallback: render words whole (cached) and use single-space separation
        x = 0
        words = line.split(' ')
        for gi, w in enumerate(words):
            if w:
                w_key = (w, fkey_base)
                w_surf = WORD_RENDER_CACHE.get(w_key) if CACHE_ENABLED else None
                if w_surf is None:
                    w_surf = font.render(w, True, color, bg_color)
                    if CACHE_ENABLED:
                        WORD_RENDER_CACHE[w_key] = w_surf
                surf.blit(w_surf, (x, int(y)))
                x += w_surf.get_width()
            if gi < len(words) - 1:
                x += font.size(' ')[0]
        y += int(line_h * line_spacing)

    if CACHE_ENABLED:
        # store a copy or the surface itself; store a copy to avoid callers mutating it
        DRAW_JUSTIFIED_SURF_CACHE[cache_draw_key] = surf.copy()
        return DRAW_JUSTIFIED_SURF_CACHE[cache_draw_key].copy()
    return surf

# Justify utils
def split_text(text: str, font: pygame.font.Font, max_width: int, justify=True) -> list[tuple[str, int, list[int]]]:
    """
        Split text into lines that exactly fill max_width (except last line).
        Returns list of (line_string, space_info, letter_spacings)
          - space_info:
              0 -> normal (no extra)
              ('words', per_space_extra, remainder, letter_extra_list) -> distribute across word gaps
              ('pad', trailing_extra) -> pad after line (single-char case)
          - letter_spacings: list of ints for per-letter gap additions (used for single-word letter justification)
    """
    # build word list preserving explicit newlines
    words = []
    for part in text.split('\n'):
        words.extend(part.split(' '))
        words.append('\n')
    if words and words[-1] == '\n':
        words.pop()

    lines = []
    line_words = []

    def flush_line(is_last=False):
        if not line_words:
            lines.append(('', 0, []))
            return
        line = ' '.join(line_words)
        if is_last or not justify:
            lines.append((line, 0, []))
            return

        # compute base width: words widths + single spaces
        # <-- use measure_word_width to include default letter spacing inside words
        word_widths = [measure_word_width(w, font) for w in line_words]
        base_width = sum(word_widths)
        gaps = len(line_words) - 1
        space_w = font.size(' ')[0]
        base_width += gaps * space_w

        extra = max_width - base_width
        if extra < 0:
            # Shouldn't happen if packing is correct; fallback to no extra
            lines.append((line, 0, []))
            return

        if gaps > 0:
            # Split extra into 1/3 for letter gaps across the whole line and 2/3 for spaces between words.
            total_letter_extra = extra // 3
            total_space_extra = extra - total_letter_extra

            # cap total_letter_extra to available capacity (max per-gap)
            total_letter_gaps = sum(max(len(w) - 1, 0) for w in line_words)
            max_total_letter_capacity = total_letter_gaps * MAX_LETTER_EXTRA
            if total_letter_extra > max_total_letter_capacity:
                overflow = total_letter_extra - max_total_letter_capacity
                total_letter_extra = max_total_letter_capacity
                # push overflow into space extra so line still fits
                total_space_extra += overflow

            # distribute space extra across word gaps
            per_space = total_space_extra // gaps if gaps else 0
            remainder = total_space_extra % gaps if gaps else 0

            # build per-letter-gap extras across entire line (left-to-right)
            letter_gap_extras = []
            if total_letter_gaps > 0 and total_letter_extra > 0:
                per_letter = total_letter_extra // total_letter_gaps
                rem_letter = total_letter_extra % total_letter_gaps
                for i in range(total_letter_gaps):
                    val = per_letter + (1 if i < rem_letter else 0)
                    # safety cap (shouldn't exceed MAX_LETTER_EXTRA thanks to earlier cap)
                    if val > MAX_LETTER_EXTRA:
                        val = MAX_LETTER_EXTRA
                    letter_gap_extras.append(val)
            else:
                # no letter gaps or no letter-extra -> empty list
                letter_gap_extras = []

            # store per_space, remainder and the global per-letter-gap extras
            lines.append((line, ('words', per_space, remainder, letter_gap_extras), []))
            return

        else:
            # single word line: distribute across letter gaps
            single = line_words[0]
            letter_gaps = max(len(single) - 1, 0)
            if letter_gaps > 0:
                # cap total per-letter extra to the per-gap maximum
                max_total = letter_gaps * MAX_LETTER_EXTRA
                used_letter_extra = min(extra, max_total)
                per_letter = used_letter_extra // letter_gaps
                remainder = used_letter_extra % letter_gaps
                letter_spacings = [per_letter + (1 if i < remainder else 0) for i in range(letter_gaps)]
                # leftover (extra - used_letter_extra) is dropped (cannot be applied between letters)
                lines.append((line, 0, letter_spacings))
                return
            else:
                # single character: pad trailing extra
                lines.append((line, ('pad', extra), []))
                return

    def split_long_word(word):
        # split long word into chunks that each fit max_width
        start = 0
        L = len(word)
        while start < L:
            # binary search max end where substring fits
            low = start + 1
            high = L + 1
            fit = low
            while low < high:
                mid = (low + high) // 2
                # use measure_word_width on substring
                if measure_word_width(word[start:mid], font) <= max_width:
                    fit = mid
                    low = mid + 1
                else:
                    high = mid
            if fit == start:
                fit = start + 1  # force at least one char
            chunk = word[start:fit]
            lines.append((chunk, 0, []))
            start = fit

    i = 0
    while i < len(words):
        w = words[i]
        if w == '\n':
            flush_line(is_last=False)
            line_words = []
            i += 1
            continue

        # use measure_word_width for single word width
        w_width = measure_word_width(w, font)
        if w_width > max_width:
            # flush current and split long word
            if line_words:
                flush_line(is_last=False)
                line_words = []
            split_long_word(w)
            i += 1
            continue

        # try adding to current line - test using per-word measurement to avoid miscounting letter spacing across words
        test_words = line_words + [w] if line_words else [w]
        if measure_line_words_width(test_words, font) <= max_width:
            line_words.append(w)
            i += 1
            continue
        else:
            # cannot add w; try to move the previous line's last word to the next line
            # to avoid creating a line with very large extra spacing.
            if len(line_words) >= 2:
                last = line_words[-1]
                candidate_line = line_words[:-1]
                # check if putting (last + w) on the next line fits,
                # and the remaining candidate_line still fits as a line
                if measure_line_words_width([last, w], font) <= max_width and measure_line_words_width(candidate_line, font) <= max_width:
                    line_words = candidate_line
                    flush_line(is_last=False)
                    # start next line with the moved last word, then retry placing w
                    line_words = [last]
                    # do NOT increment i; next iteration will try to add w to [last]
                    continue

            # fallback: flush current line and retry w on next line
            flush_line(is_last=False)
            line_words = []
            # do NOT increment i
            continue

    # flush final (last) line - do not justify last line
    flush_line(is_last=True)
    return lines

def get_total_size(lines, font, line_spacing) -> tuple[int, int]:
    max_w = 0
    total_h = 0
    space_w = font.size(' ')[0]
    for line, space_info, letter_spacings in lines:
        if isinstance(space_info, tuple):
            if space_info[0] == 'words':
                _, per_space, remainder, letter_gap_extras = space_info
                words = line.split(' ')
                width = 0
                # consume letter_gap_extras across words' internal gaps
                idx = 0
                for gi, w in enumerate(words):
                    # base word width includes DEFAULT_LETTER_SPACING
                    width += measure_word_width(w, font)
                    # add per-letter extras for this word
                    n = max(len(w) - 1, 0)
                    if n > 0:
                        width += sum(letter_gap_extras[idx:idx + n]) if letter_gap_extras else 0
                        idx += n
                    if gi < len(words) - 1:
                        width += space_w + per_space + (1 if gi < remainder else 0)
                max_w = max(max_w, width)
            elif space_info[0] == 'pad':
                _, extra = space_info
                max_w = max(max_w, measure_word_width(line, font) + extra)
            else:
                max_w = max(max_w, measure_word_width(line, font))
        elif letter_spacings:
            width = sum(font.size(ch)[0] for ch in line)
            if len(line) >= 2:
                width += DEFAULT_LETTER_SPACING * (len(line) - 1)
            width += sum(letter_spacings)
            max_w = max(max_w, width)
        else:
            words = line.split(' ')
            max_w = max(max_w, measure_line_words_width(words, font))
        total_h += font.size(line)[1] * line_spacing
    return max_w, total_h

def measure_word_width(word: str, font: pygame.font.Font) -> int:
    """Measure width of a single word including DEFAULT_LETTER_SPACING between characters."""
    if not word:
        return 0
    if len(word) == 1:
        return font.size(word)[0]
    w = sum(font.size(ch)[0] for ch in word)
    w += DEFAULT_LETTER_SPACING * (len(word) - 1)
    return w

def measure_line_words_width(words: list, font: pygame.font.Font) -> int:
    """Measure width of a sequence of words (list), counting spaces between words but not adding extra spacing around spaces."""
    if not words:
        return 0
    space_w = font.size(' ')[0]
    return sum(measure_word_width(w, font) for w in words) + space_w * (len(words) - 1)

def render_word_per_char(surf: pygame.Surface, word: str, x: int, y: int, font: pygame.font.Font, color, bg_color, extras: list[int] | None = None):
    """Render a word character-by-character, applying DEFAULT_LETTER_SPACING between characters plus optional extras per-letter-gap."""
    extras = extras or []
    for i, ch in enumerate(word):
        ch_surf = font.render(ch, True, color, bg_color)
        surf.blit(ch_surf, (x, y))
        x += ch_surf.get_width()
        # add default inter-letter spacing plus any extra for this gap
        if i < len(word) - 1:
            x += DEFAULT_LETTER_SPACING
            if i < len(extras):
                x += extras[i]
    return x

