import tkinter as tk

# Kelas GameObject digunakan untuk membuat objek dalam game yang memiliki posisi dan bisa dipindahkan dari tkinter import Canvas

# Kelas dasar untuk objek dalam permainan
class GameObject(object):
    def __init__(self, canvas, item):
        # Menginisialisasi objek dengan canvas dan item (bentuk objek pada canvas)
        self.canvas = canvas
        self.item = item

    def get_position(self):
        # Mengambil posisi objek dalam koordinat canvas
        return self.canvas.coords(self.item)

    def move(self, x, y):
        # Memindahkan objek sebesar (x, y) pada canvas
        self.canvas.move(self.item, x, y)

    def delete(self):
        # Menghapus objek dari canvas
        self.canvas.delete(self.item)

# Kelas Ball mewakili bola dalam game
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10  # Radius bola
        self.direction = [1, -1]  # Arah gerak bola (1 untuk kanan, -1 untuk kiri atau sebaliknya)
        self.speed = 7  # Kecepatan bola, semakin besar semakin cepat
        # Membuat objek bola pada canvas dengan warna hijau
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='green')
        super(Ball, self).__init__(canvas, item)  # Memanggil constructor dari kelas induk

    def update(self):
        # Memperbarui posisi bola setiap frame
        coords = self.get_position()  # Mendapatkan posisi terkini bola
        width = self.canvas.winfo_width()  # Mendapatkan lebar canvas
        # Jika bola mengenai tepi kiri atau kanan canvas, ganti arah horizontalnya
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Jika bola mengenai bagian atas canvas, ganti arah vertikalnya
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed  # Menghitung perpindahan horizontal
        y = self.direction[1] * self.speed  # Menghitung perpindahan vertikal
        self.move(x, y)  # Pindahkan bola ke posisi baru

    def collide(self, game_objects):
        # Memeriksa tabrakan antara bola dan objek lain dalam game
        coords = self.get_position()  # Mengambil posisi bola
        x = (coords[0] + coords[2]) * 0.5  # Mendapatkan posisi tengah bola di sumbu x
        if len(game_objects) > 1:
            # Jika bertabrakan dengan lebih dari satu objek, ganti arah vertikal bola
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]  # Mendapatkan objek yang bertabrakan
            coords = game_object.get_position()  # Mendapatkan posisi objek
            # Mengatur arah bola berdasarkan posisi tabrakan dengan paddle atau brick
            if x > coords[2]:
                self.direction[0] = 1  # Jika bola berada di sisi kanan objek, gerakkan ke kanan
            elif x < coords[0]:
                self.direction[0] = -1  # Jika bola berada di sisi kiri objek, gerakkan ke kiri
            else:
                self.direction[1] *= -1  # Jika berada di tengah, ubah arah vertikalnya

        # Jika bola bertabrakan dengan brick, kurangi jumlah hit brick tersebut
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

# Kelas Paddle mewakili paddle yang digunakan untuk memantulkan bola
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 150  # Lebar paddle
        self.height = 10  # Tinggi paddle
        self.ball = None  # Bola yang terkait dengan paddle
        # Membuat objek paddle pada canvas dengan warna abu-abu gelap
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#444444')
        super(Paddle, self).__init__(canvas, item)  # Memanggil constructor dari kelas induk

    def set_ball(self, ball):
        # Mengatur bola yang terkait dengan paddle
        self.ball = ball

    def move(self, offset):
        # Memindahkan paddle ke kiri atau kanan
        coords = self.get_position()  # Mendapatkan posisi paddle
        width = self.canvas.winfo_width()  # Mendapatkan lebar canvas
        # Memastikan paddle tidak keluar dari batas canvas
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)  # Pindahkan paddle
            # Jika bola masih di atas paddle, bola juga ikut bergerak
            if self.ball is not None:
                self.ball.move(offset, 0)

# Kelas Brick mewakili brick yang harus dihancurkan oleh bola
class Brick(GameObject):
    # Warna-warna brick sesuai dengan jumlah hit yang dibutuhkan
    COLORS = {1: '#FF5733', 2: '#C70039', 3: '#900C3F'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75  # Lebar brick
        self.height = 20  # Tinggi brick
        self.hits = hits  # Jumlah hit yang diperlukan untuk menghancurkan brick
        color = Brick.COLORS[hits]  # Warna brick sesuai dengan jumlah hit
        # Membuat objek brick pada canvas
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)  # Memanggil constructor dari kelas induk

    def hit(self):
        # Mengurangi jumlah hit pada brick jika bertabrakan dengan bola
        self.hits -= 1
        if self.hits == 0:
            self.delete()  # Menghapus brick jika hit mencapai 0
        else:
            # Mengubah warna brick sesuai dengan jumlah hit yang tersisa
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])

# Kelas Game mewakili keseluruhan permainan
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)  # Memanggil constructor dari superclass
        self.lives = 1  # Jumlah nyawa pemain
        self.width = 610  # Lebar canvas
        self.height = 400  # Tinggi canvas
        # Membuat canvas untuk game
        self.canvas = tk.Canvas(self, width=self.width, height=self.height)
        # Membuat pola latar belakang kotak-kotak untuk dark mode
        for i in range(0, self.width, 20):
            for j in range(0, self.height, 20):
                color = '#2E2E2E' if (i // 20 + j // 20) % 2 == 0 else '#1E1E1E'
                self.canvas.create_rectangle(i, j, i + 20, j + 20, fill=color, outline='')
        self.canvas.pack()  # Memasang canvas ke dalam frame
        self.pack()  # Memasang frame

        self.items = {}  # Menyimpan semua objek dalam game
        self.ball = None  # Objek bola (awalnya None)
        self.paddle = Paddle(self.canvas, self.width/2, 326)  # Membuat paddle pada posisi tengah bawah canvas
        self.items[self.paddle.item] = self.paddle  # Menyimpan paddle ke dalam dictionary items
        # Menambahkan brick dengan susunan yang membentuk segitiga
        brick_positions = [(x, y, hits) for y, hits in zip(range(50, 140, 30), [3, 2, 1]) for x in range(37, self.width - 37, 75)]
        for x, y, hits in brick_positions:
            self.add_brick(x, y, hits)  # Menambahkan brick sesuai dengan posisi dan jumlah hit

        self.hud = None  # Menyimpan informasi nyawa pemain (awalnya None)
        self.setup_game()  # Mengatur awal permainan
        self.canvas.focus_set()  # Mengatur fokus pada canvas untuk menerima input
        # Mengatur tombol untuk menggerakkan paddle
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))  # Menggerakkan paddle ke kiri
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))  # Menggerakkan paddle ke kanan

    def setup_game(self):
        # Mengatur bola dan menampilkan pesan awal permainan
        self.add_ball()  # Menambahkan bola baru
        self.update_lives_text()  # Memperbarui tampilan jumlah nyawa
        # Menampilkan pesan untuk memulai game
        self.text = self.draw_text(300, 200, 'Tekan Space untuk memulai!', size='30', font='ArcadeClassic')
        self.canvas.bind('<space>', lambda _: self.start_game())  # Mengatur tombol spasi untuk memulai permainan

    def add_ball(self):
        # Menambahkan bola baru pada paddle
        if self.ball is not None:
            self.ball.delete()  # Menghapus bola yang lama jika ada
        paddle_coords = self.paddle.get_position()  # Mendapatkan posisi paddle
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5  # Menempatkan bola di tengah paddle
        self.ball = Ball(self.canvas, x, 310)  # Membuat bola baru
        self.paddle.set_ball(self.ball)  # Mengatur bola agar berada di paddle

    def add_brick(self, x, y, hits):
        # Menambahkan brick pada posisi yang ditentukan
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick  # Menyimpan brick ke dalam dictionary items

    def draw_text(self, x, y, text, size='40', font='Arial'):
        # Menampilkan teks pada canvas
        return self.canvas.create_text(x, y, text=text,
                                       font=(font, size), fill='white')  # Warna teks putih untuk dark mode

    def update_lives_text(self):
        # Memperbarui tampilan jumlah nyawa pemain
        text = 'Nyawa: %s' % self.lives
        if self.hud is None:
            # Jika teks nyawa belum ada, buat baru
            self.hud = self.draw_text(50, 20, text, 12, font='ArcadeClassic')
        else:
            # Jika sudah ada, perbarui teksnya
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        # Memulai permainan setelah pemain menekan tombol spasi
        self.canvas.unbind('<space>')  # Menghilangkan binding tombol spasi setelah game dimulai
        self.canvas.delete(self.text)  # Menghapus teks instruksi
        self.paddle.ball = None  # Melepaskan bola dari paddle
        self.game_loop()  # Memulai loop utama permainan

    def game_loop(self):
        # Loop utama permainan
        self.check_collisions()  # Memeriksa tabrakan antara bola dan objek lain
        num_bricks = len(self.canvas.find_withtag('brick'))  # Menghitung jumlah brick yang tersisa
        if num_bricks == 0:
            # Jika semua brick sudah hancur, tampilkan pesan kemenangan
            self.ball.speed = None  # Menghentikan bola
            self.draw_text(300, 200, 'Yey! kamu menang!^v^', size='30', font='ArcadeClassic')
        elif self.ball.get_position()[3] >= self.height:
            # Jika bola jatuh ke bawah canvas, kurangi nyawa pemain
            self.ball.speed = None  # Menghentikan bola
            self.lives -= 1
            if self.lives < 0:
                # Jika nyawa habis, tampilkan pesan kekalahan
                self.draw_text(300, 200, 'Astaga naga!', size='30', font='ArcadeClassic')
            else:
                # Jika masih ada nyawa, setup game kembali setelah jeda 1 detik
                self.after(1000, self.setup_game)
        else:
            # Memperbarui posisi bola
            self.ball.update()
            self.after(50, self.game_loop)  # Mengulangi game_loop setelah 50 ms

    def check_collisions(self):
        # Memeriksa tabrakan antara bola dan objek lain dalam game
        ball_coords = self.ball.get_position()  # Mendapatkan posisi bola
        items = self.canvas.find_overlapping(*ball_coords)  # Mencari objek yang bertabrakan dengan bola
        objects = [self.items[x] for x in items if x in self.items]  # Mendapatkan objek dari dictionary items
        self.ball.collide(objects)  # Mengatur tabrakan bola dengan objek

# Main program untuk menjalankan game
if __name__ == '__main__':
    root = tk.Tk()  # Membuat jendela utama
    root.title('Break those Bricks!')  # Mengatur judul jendela
    game = Game(root)  # Membuat instance game
    game.mainloop()  # Menjalankan game

