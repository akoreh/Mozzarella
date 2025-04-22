import tkinter
import tkinter.font as tkfont

from url import URL


class Browser:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.HSTEP, self.VSTEP = 13, 18
        self.scroll = 0

        self.window = tkinter.Tk()
        self.window.title("Mozzarella Browser 🧀")
        self.canvas = tkinter.Canvas(
            self.window, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()

        self.window.bind("<MouseWheel>", self._on_scroll)

        self.font = tkfont.Font(
            family="Cartograph CF",
            size=16,
            weight="normal",
            slant="italic",
        )

    def load(self, url: str):
        url = URL(url)
        body = url.request()

        text = self._lex(body)
        self.display_list = self._layout(text)
        self._draw()

    def _lex(self, body) -> str:
        text = ""
        inTag = False

        for c in body:
            if c == "<":
                inTag = True
            elif c == ">":
                inTag = False
            elif not inTag:
                text += c

        return text

    def _layout(self, text: str):
        display_list = []
        cursor_x, cursor_y = self.HSTEP, self.VSTEP

        for word in text.split():
            w = self.font.measure(word)

            cursor_x += self.HSTEP

            if cursor_x + w > self.WIDTH - self.HSTEP:
                cursor_y += self.font.metrics("linespace") * 1.25
                cursor_x = self.HSTEP

            display_list.append((cursor_x, cursor_y, word))

            cursor_x += w + self.font.measure(" ")

        return display_list

    def _draw(self):
        self.canvas.delete('all')

        for x, y, c in self.display_list:
            if y > self.scroll + self.HEIGHT:
                continue
            if y + self.VSTEP < self.scroll:
                continue

            self.canvas.create_text(
                x, y - self.scroll, text=c, font=self.font, anchor="nw")

    def _on_scroll(self, event):
        direction = event.delta

        if direction > 0:
            self.scroll = max(self.scroll - 20, 0)
        else:
            self.scroll += 20

        self._draw()


if __name__ == "__main__":
    import sys
    Browser().load(sys.argv[1])
    tkinter.mainloop()
