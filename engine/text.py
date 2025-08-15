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

def measure_word_width(word: str, font: pygame.font.Font) -> int:
    """Measure width of a single word including DEFAULT_LETTER_SPACING between characters."""
    if not word:
        return 0
    if len(word) == 1:
        return font.size(word)[0]
    w = 0
    for ch in word:
        w += font.size(ch)[0]
    w += DEFAULT_LETTER_SPACING * (len(word) - 1)
    return w

def measure_line_words_width(words: list, font: pygame.font.Font) -> int:
    """Measure width of a sequence of words (list), counting spaces between words but not adding extra spacing around spaces."""
    if not words:
        return 0
    space_w = font.size(' ')[0]
    return sum(measure_word_width(w, font) for w in words) + space_w * (len(words) - 1)

def render_word_per_char(surf: pygame.Surface, word: str, x: int, y: int, font: pygame.font.Font, color, bg_color, extras: list[int] = None):
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
# --- end added helpers ---

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
        if line_words:
            test_words = line_words + [w]
        else:
            test_words = [w]
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
            # single-word explicit letter_spacings: include default + explicit extras
            width = 0
            for ch in line:
                width += font.size(ch)[0]
            if len(line) >= 2:
                width += DEFAULT_LETTER_SPACING * (len(line) - 1)
            width += sum(letter_spacings)
            max_w = max(max_w, width)
        else:
            words = line.split(' ')
            max_w = max(max_w, measure_line_words_width(words, font))
        total_h += font.size(line)[1] * line_spacing
    return max_w, total_h

def draw_text(text, font, color, bg_color=None, width=300, height=200, line_spacing=1.2):
    if not isinstance(font, pygame.font.Font):
        font = get_font(*font)

    lines = split_text(text, font, width)
    surf = pygame.Surface(get_total_size(lines, font, line_spacing), pygame.SRCALPHA)

    y = 0
    for line, space_info, letter_spacings in lines:
        line_h = font.size(line)[1]
        if y + line_h * line_spacing > height:
            break

        if isinstance(space_info, tuple):
            if space_info[0] == 'words':
                _, per_space, remainder, letter_gap_extras = space_info
                words = line.split(' ')
                x = 0
                # consume per-letter extras across the words
                letter_idx = 0
                for gi, w in enumerate(words):
                    if w:
                        n = max(len(w) - 1, 0)
                        extras_for_word = letter_gap_extras[letter_idx:letter_idx + n] if letter_gap_extras else []
                        x = render_word_per_char(surf, w, x, y, font, color, bg_color, extras_for_word)
                        letter_idx += n
                    if gi < len(words) - 1:
                        # apply the extra space between words
                        add = font.size(' ')[0] + per_space + (1 if gi < remainder else 0)
                        x += add
                y += line_h * line_spacing
                continue
            elif space_info[0] == 'pad':
                _, extra = space_info
                # draw the word and advance by extra to match width
                if line:
                    render_word_per_char(surf, line, 0, y, font, color, bg_color)
                y += line_h * line_spacing
                continue

        if letter_spacings:
            x = 0
            gap_idx = 0
            for idx, ch in enumerate(line):
                ch_surf = font.render(ch, True, color, bg_color)
                surf.blit(ch_surf, (x, y))
                x += ch_surf.get_width()
                if gap_idx < len(letter_spacings):
                    # default spacing plus explicit extra for this gap
                    x += DEFAULT_LETTER_SPACING + letter_spacings[gap_idx]
                    gap_idx += 1
            y += line_h * line_spacing
            continue

        # normal rendering: render words per-character to include DEFAULT_LETTER_SPACING
        x = 0
        words = line.split(' ')
        for gi, w in enumerate(words):
            if w:
                x = render_word_per_char(surf, w, x, y, font, color, bg_color)
            if gi < len(words) - 1:
                x += font.size(' ')[0]
        y += line_h * line_spacing

    return surf
