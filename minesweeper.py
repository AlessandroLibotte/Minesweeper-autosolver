from random import randint
import time
import tkinter as tk


class Cell:

    def __init__(self):
        self.neighbors: int = 0
        self.mine: bool = False
        self.flag: bool = False
        self.visible: bool = False
        return

    @property
    def get_neighbors(self):
        return self.neighbors

    @property
    def is_mine(self):
        return self.mine

    @property
    def is_visible(self):
        return self.visible

    @property
    def is_flagged(self):
        return self.flag

    def set_neigh(self, neigh):
        self.neighbors = neigh

    def set_mine(self):
        self.mine = True

    def set_flag(self):
        if self.flag is True:
            self.flag = False
        elif self.flag is False:
            self.flag = True
        return self.flag

    def reveal(self):
        self.visible = True


class Minesweeper:

    def __init__(self):

        self.running = False
        self.autoplay = False
        self.stage = 0
        self.guess = False
        self.idle_counter = 0
        self.idle_neighs = list()

        self._run()

    def _run(self):

        self.running = True

        self.field = MsField()
        self.field.new_game()
        self.gui = MsGui(self.field)

        master = self.gui.setup_window()
        master.protocol("WM_DELETE_WINDOW", lambda: self.quit(master))
        self.gui.autoplay_btn.config(command=self._toggle_autoplay)
        self.gui.new_game_btn.config(command=self._new_game)

        t = 0.5

        while self.running:

            if self.field.game_over is False and self.field.win is False:
                if self.autoplay is True:
                    if time.time() - t >= 0.5:
                        t = time.time()
                        self._autoplayer()
                        self.gui.update_win()

            master.update()
            master.update_idletasks()

    def quit(self, master):
        self.running = False
        master.destroy()

    def _toggle_autoplay(self):
        self.autoplay = not self.autoplay

    def _new_game(self):
        self.autoplay = False
        self.field.new_game()
        self.gui.update_win()
        self.stage = 0
        self.guess = False
        self.idle_counter = 0
        self.idle_neighs.clear()

    def _autoplayer(self):

        if self.stage == 0:

            if self.guess is False:
                x = randint(0, self.field.field_size[0]-1)
                y = randint(0, self.field.field_size[1]-1)
            else:
                cells = self.idle_neighs[randint(0, len(self.idle_neighs)-1)]
                c = cells[randint(0, len(cells)-1)]
                while self.field.field[c[0]][c[1]].get_neighbors == 0:
                    cells.remove(c)
                    c = cells[randint(0, len(cells) - 1)]
                x = c[0]
                y = c[1]

            self.field.reveal(x, y)

            if self.guess is True:
                self.idle_neighs.clear()
                self.guess = False
                self.stage = 1

            elif self.field.field[x][y].get_neighbors == 0:

                self.stage = 1

        elif self.stage == 1:

            counter = 0

            for y in range(self.field.field_size[1]):
                for x in range(self.field.field_size[0]):

                    if self.field.field[x][y].is_visible:

                        neigh_num = 0
                        neighs = list()

                        for ay in range(-1, 2):
                            for ax in range(-1, 2):

                                if x != 0 or y != 0:

                                    fx = x + ax
                                    fy = y + ay

                                    if 0 <= fx < self.field.field_size[0] and 0 <= fy < self.field.field_size[1]:
                                        if not self.field.field[fx][fy].is_visible:
                                            neigh_num += 1
                                            neighs.append((fx, fy))

                        if neigh_num == self.field.field[x][y].get_neighbors:

                            for n in neighs:

                                if not self.field.field[n[0]][n[1]].is_flagged:

                                    self.field.field[n[0]][n[1]].set_flag()

                        else:
                            if len(neighs) != 0:
                                self.idle_neighs.append(neighs)
                            counter += 1

            if counter == self.idle_counter:
                self.guess = True
                self.stage = 0
            else:
                self.idle_counter = counter
                self.stage = 2

        elif self.stage == 2:

            for y in range(self.field.field_size[1]):
                for x in range(self.field.field_size[0]):

                    if self.field.field[x][y].is_visible:

                        neigh_num = 0
                        neighs = list()
                        flags_num = 0

                        for ay in range(-1, 2):
                            for ax in range(-1, 2):

                                if x != 0 or y != 0:

                                    fx = x + ax
                                    fy = y + ay

                                    if 0 <= fx < self.field.field_size[0] and 0 <= fy < self.field.field_size[1]:

                                        if not self.field.field[fx][fy].is_visible \
                                                and not self.field.field[fx][fy].is_flagged:

                                            neigh_num += 1
                                            neighs.append((fx, fy))

                                        if self.field.field[fx][fy].is_flagged:

                                            flags_num += 1

                        if flags_num == self.field.field[x][y].get_neighbors:

                            for n in neighs:

                                self.field.reveal(n[0], n[1])

            self.stage = 1


class MsField:

    def __init__(self):
        self.win = None
        self.game_over = None
        self.field_size = None
        self.mine_num = None
        self.field = None

    def new_game(self, field_size=(16, 16), mine_density=0.136):

        self.win = False
        self.game_over = False
        self.field_size = field_size
        self.mine_num = int(mine_density * (self.field_size[0] * self.field_size[1]))
        self.field = [[Cell() for i in range(self.field_size[0])] for j in range(self.field_size[1])]
        self._gen_mines()
        self._setup_field()

    @property
    def get_field_size(self):
        return self.field_size

    @property
    def get_field(self):
        return self.field

    def _gen_mines(self):

        X = [i for i in range(self.field_size[0])]
        Y = [i for i in range(self.field_size[1])]

        draw_batch = list()

        for y in Y:
            for x in X:
                draw_batch.append((x, y))

        mines = list()
        counter = 0
        while counter < self.mine_num:
            mines.append(draw_batch[randint(0, len(draw_batch)-1)])
            counter += 1
            draw_batch.remove(mines[-1])

        """mines_x = np.random.choice(a=self.field_size[0], size=self.mine_num)
        mines_y = np.random.choice(a=self.field_size[1], size=self.mine_num)
        mines = list(zip(mines_y, mines_x))"""

        for m in mines:

            self.field[m[0]][m[1]].set_mine()

    def _setup_field(self):

        for y in range(self.field_size[1]):
            for x in range(self.field_size[0]):

                if not self.field[x][y].is_mine:

                    neigh_count = self._check_around((x, y))
                    self.field[x][y].set_neigh(neigh_count)

    def _check_around(self, p: tuple[int, int]):

        neigh_count = 0

        for y in range(-1, 2):
            for x in range(-1, 2):

                if x != 0 or y != 0:

                    fx = x+p[0]
                    fy = y+p[1]

                    if 0 <= fx < self.field_size[0] and 0 <= fy < self.field_size[1]:
                        if self.field[fx][fy].is_mine:

                            neigh_count += 1

        return neigh_count

    def reveal(self, x, y):

        if not self.field[x][y].is_visible and not self.field[x][y].is_flagged:

            self.field[x][y].reveal()

            if self.field[x][y].is_mine:

                self.game_over = True

            else:

                if self.field[x][y].get_neighbors == 0:

                    for ay in range(-1, 2):
                        for ax in range(-1, 2):

                            if ax != 0 or ay != 0:

                                fx = ax + x
                                fy = ay + y

                                if 0 <= fx < self.field_size[0] and 0 <= fy < self.field_size[1]:

                                    self.reveal(fx, fy)


class MsGui:

    def __init__(self, field: MsField):

        self.field = field
        self.flags = list()
        self.screen_scale = 30
        self.master = None
        self.new_game_btn = None
        self.autoplay_btn = None
        self.canvas = None
        self.mine_counter_tv = None

    def setup_window(self):

        self.master = tk.Tk()
        self.master.wm_resizable(False, False)
        self.master.title("Minesweeper")
        self.master.iconbitmap('icon.ico')

        master_frame = tk.Frame(self.master)

        top_frame = tk.Frame(master_frame, bg="#141414", height=50,
                             width=self.field.field_size[0] * self.screen_scale)
        self.new_game_btn = tk.Button(top_frame, text='New Game', relief=tk.RIDGE, bg="#141414",
                                      fg="#EBEBEB", activebackground="#EBEBEB")
        self.mine_counter_tv = tk.Variable(value=self.field.mine_num - len(self.flags))
        mine_counter_label = tk.Label(top_frame, textvariable=self.mine_counter_tv, bg="#141414",
                                      fg="#EBEBEB")

        """settings_icon = tk.PhotoImage(file="settings_icon.png")
        settings_button = tk.Button(top_frame, relief=tk.RIDGE, width=20, height=20,
                                    image=settings_icon, bg="#EBEBEB",
                                    fg="#141414", activebackground="#EBEBEB", command=self._settings_window)
        settings_button.image = settings_icon"""

        self.autoplay_btn = tk.Button(top_frame, text='Autoplay', relief=tk.RIDGE, bg="#141414",
                                      fg="#EBEBEB", activebackground="#EBEBEB")

        canvas_frame = tk.Frame(master_frame, bg="#141414")
        self.canvas = tk.Canvas(canvas_frame, bg='#0065FF', width=self.field.field_size[0] * self.screen_scale,
                                height=self.field.field_size[1] * self.screen_scale,
                                highlightbackground="#141414")
        self.canvas.bind("<Button-1>", self._input_reveal)
        self.canvas.bind("<Button-3>", self._input_flag)

        master_frame.pack(expand=True, fill=tk.BOTH)

        top_frame.pack(fill=tk.BOTH, expand=True)
        top_frame.pack_propagate(False)
        self.new_game_btn.pack(side=tk.LEFT, padx=10)
        mine_counter_label.pack(side=tk.LEFT)
        # settings_button.pack(side=tk.LEFT)

        self.autoplay_btn.pack(side=tk.RIGHT, padx=10)

        canvas_frame.pack()
        self.canvas.pack()

        self._draw_cells()

        self.update_win()

        return self.master

    """def _settings_window(self):

        settings_master = tk.Toplevel(self.master)
        settings_master.title(" ")
        settings_master.resizable(False, False)
        settings_master.geometry("178x115")
        settings_master.iconbitmap('settings_icon.ico')

        master_frame = tk.Frame(settings_master, bg="#141414")
        master_frame.pack(expand=True, fill=tk.BOTH)
        master_frame.pack_propagate(False)

        field_w_label = tk.Label(master_frame, text="Field Width", bg="#141414", fg="#EBEBEB")
        field_h_label = tk.Label(master_frame, text="Field Height", bg="#141414", fg="#EBEBEB")
        field_w_entry = tk.Entry(master_frame, width=4)
        field_h_entry = tk.Entry(master_frame, width=4)
        field_density_label = tk.Label(master_frame, text="Field Density", bg="#141414", fg="#EBEBEB")
        field_density_entry = tk.Entry(master_frame, width=4)

        field_w_label.grid(column=0, row=0, padx=3, ipady=3)
        field_w_entry.grid(column=1, row=0, padx=10, pady=3)
        field_h_label.grid(column=0, row=1, padx=3, pady=3)
        field_h_entry.grid(column=1, row=1, padx=10, pady=3)
        field_density_label.grid(column=0, row=2, padx=3, pady=3)
        field_density_entry.grid(column=1, row=2, padx=3, pady=3)

        finish_button = tk.Button(master_frame, text="Finish", relief=tk.RIDGE, bg="#141414",
                                  fg="#EBEBEB", activebackground="#EBEBEB")
        finish_button.grid(column=2, row=3)

        settings_master.mainloop()

        return"""

    def _input_reveal(self, event):

        if self.field.game_over is False and self.field.win is False:

            x = int(event.x / self.screen_scale)
            y = int(event.y / self.screen_scale)
            self.field.reveal(x, y)
            self.update_win(self.field.game_over, self.field.win)

    def _input_flag(self, event):

        if self.field.game_over is False and self.field.win is False:

            x = int(event.x / self.screen_scale)
            y = int(event.y / self.screen_scale)

            if not self.field.field[x][y].is_visible:

                self.field.field[x][y].set_flag()
                self.mine_counter_tv.set(self.field.mine_num)
                self.update_win(self.field.game_over, self.field.win)

    def _draw_cells(self):

        for y in range(self.field.field_size[0]):
            for x in range(self.field.field_size[1]):

                self.canvas.create_line(0, y * self.screen_scale,
                                        self.field.field_size[0] * self.screen_scale, y * self.screen_scale,
                                        fill='#003D99')
                self.canvas.create_line(x * self.screen_scale, 0,
                                        x * self.screen_scale, self.field.field_size[1] * self.screen_scale,
                                        fill='#003D99')

    def update_win(self, game_over=False, win=False):

        self.flags.clear()

        if game_over is False and win is False:
            self.canvas.delete("all")

        for y in range(self.field.field_size[1]):
            for x in range(self.field.field_size[0]):

                if game_over is False and win is False:

                    if self.field.field[x][y].is_visible:

                        self.canvas.create_rectangle(x * self.screen_scale, y * self.screen_scale,
                                                     (x + 1) * self.screen_scale, (y + 1) * self.screen_scale,
                                                     fill="#003D99")

                        if self.field.field[x][y].get_neighbors != 0:

                            self.canvas.create_text((x * self.screen_scale) + 15, ((y + 1) * self.screen_scale) - 15,
                                                    font=('Consolas', 20),
                                                    text=str(self.field.field[x][y].get_neighbors),
                                                    fill="#FFFFFF")

                    if self.field.field[x][y].is_flagged:

                        self.canvas.create_rectangle(x * self.screen_scale, y * self.screen_scale,
                                                     (x + 1) * self.screen_scale, (y + 1) * self.screen_scale,
                                                     fill="#969696")
                        flag_icon = tk.PhotoImage(file="flag_icon.png")
                        self.flags.append(flag_icon)
                        self.canvas.create_image((x * self.screen_scale) + 3, (y * self.screen_scale) + 3,
                                                 anchor=tk.NW, image=flag_icon)

                elif game_over is True:

                    if self.field.field[x][y].is_mine:

                        if not self.field.field[x][y].is_flagged:

                            self.canvas.create_rectangle(x * self.screen_scale, y * self.screen_scale,
                                                         (x + 1) * self.screen_scale, (y + 1) * self.screen_scale,
                                                         fill="#960000")
                        else:

                            self.canvas.create_rectangle(x * self.screen_scale, y * self.screen_scale,
                                                         (x + 1) * self.screen_scale, (y + 1) * self.screen_scale,
                                                         fill="#960000")
                            flag_icon = tk.PhotoImage(file="flag_icon.png")
                            self.flags.append(flag_icon)
                            self.canvas.create_image((x * self.screen_scale) + 3, (y * self.screen_scale) + 3,
                                                     anchor=tk.NW, image=flag_icon)

                elif win is True:

                    self.canvas.create_rectangle(x * self.screen_scale, y * self.screen_scale,
                                                 (x + 1) * self.screen_scale, (y + 1) * self.screen_scale,
                                                 fill="#003D99")

                    if self.field.field[x][y].get_neighbors != 0:
                        self.canvas.create_text((x * self.screen_scale) + 15, ((y + 1) * self.screen_scale) - 15,
                                                font=('Consolas', 20),
                                                text=str(self.field.field[x][y].get_neighbors),
                                                fill="#FFFFFF")

                    if self.field.field[x][y].is_flagged:

                        self.canvas.create_rectangle(x * self.screen_scale, y * self.screen_scale,
                                                     (x + 1) * self.screen_scale, (y + 1) * self.screen_scale,
                                                     fill="#969696")
                        flag_icon = tk.PhotoImage(file="flag_icon.png")
                        self.flags.append(flag_icon)
                        self.canvas.create_image((x * self.screen_scale) + 3, (y * self.screen_scale) + 3,
                                                 anchor=tk.NW, image=flag_icon)

        if win is False:
            counter = 0

            for row in self.field.field:
                for cell in row:
                    if cell.is_mine and cell.is_flagged:
                        counter += 1

            if counter == self.field.mine_num:
                print('Win')
                self.field.win = True
                self.update_win(False, True)

        self.mine_counter_tv.set(self.field.mine_num - len(self.flags))
        self._draw_cells()


if __name__ == "__main__":
    Minesweeper()
