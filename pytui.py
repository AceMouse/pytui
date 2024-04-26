import os
import sys
class Tui:
    def _place_text(self, text:str, col:int, row:int):
        self._queue += [f"{self._CMD}{row};{col}H{text}"]
        if not self._buf:
            self.flush()

    def _split_text_every_nth(self, text:str, n:int) -> list[str]:
        return [text[i:i+n] for i in range(0, len(text), n)]

    def _split_text_before_every_nth(self, text:str, n:int, ch:str = " ", allow_overflow:bool = True) -> list[str]:
        ret = []
        t_cols, _ = os.get_terminal_size()
        while text != "":
            if len(text) < n:
                ret += [text]
                return ret
            idx = text.find(ch)
            if idx == -1:
                if allow_overflow:
                    ret += [text]
                else:
                    ret += _split_text_every_nth(text, n)
                return ret 
            idx = text.rfind(ch,0,max(n,idx+1))
            if not allow_overflow:
                idx = min(n, idx)
            else:
                idx = min(t_cols, idx)
            cut = text[:idx]
            if idx < n:
                cut += (n-idx)*' '
            ret += [cut]
            text = text[idx+1:]
        return ret 

    def _correct_wh(self, col, row, width, height):
        t_cols, t_rows = os.get_terminal_size()
        width = min(width, t_cols-col)
        height = min(height, t_rows-row)
        return width, height

    def clear_box(self, col:int = 0, row:int = 0, width:int = 10000, height: int = 10000):
        if width == 0 or height == 0:
            return
        width, height = self._correct_wh(col, row, width, height)
        if width <= 0 or height <= 0:
            return
        col += 1
        row += 1
        for i in range(height):
            self._place_text(' '*width, col, row+i)

    def set_buffered(self, buffered:bool):
        self._buf = buffered

    def clear_line(self, col:int = 0, row:int = 0):
        self._place_text(f"{self._CMD}0K", col+1, row+1)

    def place_text(self, text:str, col:int = 0, row:int = 0, width:int = 10000, height:int = 10000):
        if width == 0 or height == 0:
            return
        width, height = self._correct_wh(col, row, width, height)
        if width <= 0 or height <= 0:
            return
        col += 1
        row += 1
        max_len = width*height
        trunkated = ''.join(self._split_text_before_every_nth(text, width, allow_overflow=True)) 
        if len(text)>max_len:
            post = ''
            if max_len >= 10:
                post = '...'
            t_len = max_len - len(post)
            trunkated = text[:t_len] + post 
        padding = ' '*(max_len-len(trunkated))
        old_buf = self._buf
        self.set_buffered(True)
#        for i,text in enumerate(self._split_text_every_nth(trunkated + padding, width)): 
        for i,text in enumerate(self._split_text_before_every_nth(trunkated + padding, width, allow_overflow=True)): 
            self._place_text(text, col, row+i)
        if not old_buf:
            self.flush()
        self.set_buffered(old_buf)

                
    def flush(self):
        sys.stdout.write(''.join(self._queue))
        sys.stdout.flush()
        _queue = []

    def clear(self):
        self._queue = [f"{self._CMD}1;1H{self._CMD}0J"]
        if not self._buf:
            self.flush()

    def hide_cursor(self, hide:bool):
        sys.stdout.write(f"{self._CMD}?25l" if hide else f"{self._CMD}?25h")
        sys.stdout.flush()

    def __init__(self,buffered:bool = False, hide_cursor:bool = True):
        self._buf = buffered
        self._queue = []
        self._CMD = '\033['
        self.hide_cursor(hide_cursor)


def test():
    import time 
    tui = Tui()
    tui.clear()
    tui.place_text("1234567", 3, 3, width = 3, height = 1)
    time.sleep(1)
    tui.set_buffered(True)
    tui.place_text("1234567890123456789", 3, 3, width = 15, height = 1)
    time.sleep(1)
    tui.place_text("123", 3, 3, width = 10, height = 1)
    tui.flush()
    tui.set_buffered(False)
    tui.place_text("1234567890123456789", 4, 4, width = 2)
    tui.place_text("1234567890123456789", 7, 7, width = 3, height = 3)
    time.sleep(1)
    tui.clear()
    [print(x) for x in tui._split_text_before_every_nth("123 567 9", 6, allow_overflow=True)]
    [print(x) for x in tui._split_text_before_every_nth("123567 9", 6, allow_overflow=True)]
    [print(x) for x in tui._split_text_before_every_nth("1235679", 6, allow_overflow=True)]
    [print(x) for x in tui._split_text_before_every_nth("12234566667 12227011 4 17098 01479 047189 704911704 87 01842 70481 70431", 6, allow_overflow=True)]

if __name__ == "__main__":
    test()
