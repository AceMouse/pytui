import os
class Tui:
    def _place_text(self, text:str, col:int, row:int):
        self._queue += [f"{self._CMD}{row};{col}H{text}"]
        if not self._buf:
            self.flush()

    def _split_text_every_nth(self, text:str, n:int) -> list[str]:
        return [text[i:i+n] for i in range(0, len(text), n)]

    def _correct_wh(self, col, row, width, height):
        t_cols, t_rows = os.get_terminal_size()
        width = min(width, t_cols-col)
        height = min(height, t_rows-row)
        return width, height

    def clear_box(self, col:int, row:int, width:int = 10000, height: int = 10000):
        if width == 0 or height == 0:
            return
        width, height = self._correct_wh(col, row, width, height)
        if width <= 0 or height <= 0:
            return
        col += 1
        row += 1
        for i in range(height):
            self._place_text(' '*width, col, row+1)

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
        max_len = -1
        max_len = width*height
        trunkated = text 
        if len(text)>max_len:
            post = ''
            if max_len >= 10:
                post = '...'
            t_len = max_len - len(post)
            trunkated = text[:t_len] + post 
        padding = ' '*(max_len-len(trunkated))
        for i,text in enumerate(self._split_text_every_nth(trunkated + padding, width)): 
            self._place_text(text, col, row+i)
                
    def flush(self):
        print(''.join(self._queue), flush=True)
        _queue = []

    def clear(self):
        self._queue = [f"{self._CMD}1;1H{self._CMD}0J"]
        if not self._buf:
            self.flush()

    def test(self):
        import time 
        self.clear()
        self.place_text("1234567", 3, 3, width = 3, height = 1)
        time.sleep(1)
        self.set_buffered(True)
        self.place_text("1234567890123456789", 3, 3, width = 15, height = 1)
        time.sleep(1)
        self.place_text("123", 3, 3, width = 10, height = 1)
        self.flush()
        self.set_buffered(False)
        self.place_text("1234567890123456789", 4, 4, width = 2)
        self.place_text("1234567890123456789", 7, 7, width = 3, height = 3)

    def __init__(self,buffered = False):
        self._buf = buffered
        self._queue = []
        self._CMD = '\033['


if __name__ == "__main__":
    t = Tui()
    t.test()
