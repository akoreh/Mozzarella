import tkinter
import tkinter.font as tkfont

from url import URL
from text import Text
from tag import Tag

RETRO_STYLE = {
    "bg": "black",
    "fg": "#00FF00",
    "font": ("Courier New", 14),
    "entry_bg": "black",
    "entry_fg": "#00FF00",
    "button_bg": "#222",
    "button_fg": "#00FF00",
    "canvas_bg": "black",
    "canvas_text_fg": "#00FF00",
    "border_width": 2,
    "relief": "sunken",
}


class Browser:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.HSTEP, self.VSTEP = 13, 18
        self.scroll = 0

        self._initWindow()

        self.font = tkfont.Font(
            family="Cartograph CF",
            size=16,
            weight="normal",
            slant="italic",
        )

    def _initWindow(self):
        self.window = tkinter.Tk()
        self.window.title("Mozzarella 🧀")
        self.window.configure(bg=RETRO_STYLE["bg"])

        # URL bar
        self.url_var = tkinter.StringVar()
        self.url_entry = tkinter.Entry(self.window,
                                       textvariable=self.url_var,
                                       bg=RETRO_STYLE["entry_bg"],
                                       fg=RETRO_STYLE["entry_fg"],
                                       font=RETRO_STYLE["font"],
                                       # Cursor color
                                       insertbackground=RETRO_STYLE["fg"],
                                       bd=RETRO_STYLE["border_width"],
                                       relief=RETRO_STYLE["relief"])
        self.url_entry.pack(side=tkinter.TOP, fill=tkinter.X)
        self.load_button = tkinter.Button(self.window,
                                          text="Load",
                                          bg=RETRO_STYLE["button_bg"],
                                          fg=RETRO_STYLE["button_fg"],
                                          font=RETRO_STYLE["font"],
                                          bd=RETRO_STYLE["border_width"],
                                          relief=RETRO_STYLE["relief"],
                                          command=self._load)
        self.load_button.pack(side=tkinter.TOP, fill=tkinter.X)

        self.canvas = tkinter.Canvas(
            self.window, width=self.WIDTH, height=self.HEIGHT, bg=RETRO_STYLE["canvas_bg"])
        self.canvas.pack(fill=tkinter.BOTH, expand=True)

        self.window.bind("<MouseWheel>", self._on_scroll)

    def _load(self):
        url = URL(self.url_var.get())
        body = url.request()

        text = self._lex(body)
        self.display_list = self._layout(text)
        self._draw()

    def _lex(self, body):
        out = []
        buffer = ""
        in_tag = False

        for c in body:
            if c == "<":
                in_tag = True
                if buffer:
                    out.append(Text(buffer))
                buffer = ""
            elif c == ">":
                in_tag = False
                out.append(Tag(buffer))
                buffer = ""
            else:
                buffer += c

        if not in_tag and buffer:
            out.append(Text(buffer))
        return out

    def _layout(self, tokens):
        display_list = []
        cursor_x, cursor_y = self.HSTEP, self.VSTEP

        for token in tokens:
            if isinstance(token, Text):
                for word in token.text.split():
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
    Browser()
    tkinter.mainloop()
