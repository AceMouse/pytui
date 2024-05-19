import os
import sys
class Tui:
    def _b_place_cursor(self, col:int, row:int):
        self._place_cursor_abs(col+self.col_offset, row+self.row_offset)

    def _place_cursor_abs(self, col:int, row:int):
        self._queue += [f"{self._CSI}{row};{col}H"]

    def _place_text(self, text:str, col:int, row:int):
        self._b_place_cursor(col, row)
        self._queue += [text]

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

    def _correct_dims(self, col, row, width, height):
        t_cols, t_rows = os.get_terminal_size()
        width  = min(width,  t_cols-(col+self.col_offset),self.max_width -(col+self.col_offset))
        height = min(height, t_rows-(row+self.row_offset),self.max_height-(row+self.row_offset))
        return width, height

    def clear_box(self, col:int = 0, row:int = 0, width:int = 10000, height: int = 10000):
        if width == 0 or height == 0:
            return
        width, height = self._correct_dims(col, row, width, height)
        if width <= 0 or height <= 0:
            return
        col += 1
        row += 1
        for i in range(height):
            self._place_text(' '*width, col, row+i)
        self._flush()

    def clear_line(self, col:int = 0, row:int = 0):
        self.clear_box(col, row, height=1)
        self._flush()

    def place_text(self, text:str, col:int = 0, row:int = 0, width:int = 10000, height:int = 10000):
        if width == 0 or height == 0:
            return
        width, height = self._correct_dims(col, row, width, height)
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
        for i,text in enumerate(self._split_text_before_every_nth(trunkated + padding, width, allow_overflow=True)): 
            self._place_text(text, col, row+i)
        self._flush()

    def place_cursor(self, col:int=0, row:int=0):
        col, row = self._correct_dims(0,0,col,row)
        self._b_place_cursor(col+1, row+1) 
        self._flush()

    def _flush(self, force:bool=False): 
        if force or (not self.buffered):
            if self.return_on_flush:
                self._queue = [f"{self._CSI}s"] + self._queue + [f"{self._CSI}u"]

            sys.stdout.write(''.join(self._queue))
            sys.stdout.flush()
            self._queue = []

    def flush(self):
        self._flush(True)

    def clear(self):
        self.clear_box(0,0)
        self._flush()

    def hide_cursor(self, hide:bool):
        self._queue += [f"{self._CSI}?25l" if hide else f"{self._CSI}?25h"]
        self._flush()

    def __init__(self,buffered:bool = False, hide_cursor:bool = True, col_offset=0, row_offset=0, max_width=10000, max_height=10000, default_cursor_pos=None, return_on_flush=True):
        self._queue = []
        self._CSI = '\033['
        self.buffered = buffered
        self.max_width = max_width
        self.max_height = max_height
        self.col_offset = col_offset
        self.row_offset = row_offset
        if default_cursor_pos is not None:
            self.return_on_flush = False
            self._place_cursor_abs(*default_cursor_pos)
            self.flush()
        self.return_on_flush = return_on_flush
        self.hide_cursor(hide_cursor)


def test():
    import time 
    tui = Tui()
    tui.clear()
    tui.place_text("1234567", 3, 3, width = 3, height = 1)
    time.sleep(1)
    tui.buffered = True 
    tui.place_text("1234567890123456789", 3, 3, width = 15, height = 1)
    time.sleep(1)
    tui.place_text("123", 3, 3, width = 10, height = 1)
    tui.flush()
    tui.buffered = False
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
