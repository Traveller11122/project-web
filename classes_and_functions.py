import pygame
import os
import random
from requests import get, post


Color = pygame.Color


gravity = 10
speed = 7
spikes = pygame.sprite.Group()
size = width, height = 900, 750
k = 0
b = False
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
start = True
n_y = 0
screen_rect = (0, 0, width, height)
particles = pygame.sprite.Group()
access = False
processing = False
holding1 = False
holding2 = False
SCORE = 0
score_inc = 30
gen = 31
bgen = False


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.init()

        pygame.display.set_caption("Geometry Dash (alpha)")
        self.end_sound = pygame.mixer.Sound(os.path.join('data', 'boom.wav'))

    class Score(pygame.sprite.Sprite):
        def __init__(self):
            pygame.font.init()
            pygame.sprite.Sprite.__init__(self)
            self.font = pygame.font.Font(None, 20)
            self.font.set_italic(1)
            self.color = Color('white')
            self.lastscore = -1
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)
            self.rect = self.image.get_rect().move(10, height - 15)

        def update(self):
            if SCORE != self.lastscore:
                self.lastscore = SCORE
                msg = "Score: %d" % SCORE
                self.image = self.font.render(msg, 0, self.color)
            if access:
                self.rect.left += speed

    @staticmethod
    def load_image(name, colorkey=None):
        image = pygame.image.load(name)
        image = image.convert_alpha()
        return image

    class Camera:
        # зададим начальный сдвиг камеры
        def __init__(self):
            self.dx = 0
            self.dy = 0

        # сдвинуть объект obj на смещение камеры
        def apply(self, obj):
            obj.rect.x += self.dx
            obj.rect.y += self.dy

        # позиционировать камеру на объекте target
        def update(self, target):
            self.dx = -(target.rect.x + target.rect.w // 2 - 265)
            if target.rect.y + target.rect.h // 2 <= height // 2:
                self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
            else:
                self.dy = 0

        def clear(self):
            self.dx = 0
            self.dy = 0

    class Particle(pygame.sprite.Sprite):
        # сгенерируем частицы разного размера

        def __init__(self, pos, dx, dy, im):
            global all_sprites, particles
            super().__init__(all_sprites)
            self.fire = [im]
            for scale in (5, 10, 20):
                self.fire.append(pygame.transform.scale(self.fire[0], (scale, scale)))
            self.image = random.choice(self.fire)
            self.rect = self.image.get_rect()
            self.add(particles)
            # у каждой частицы своя скорость — это вектор
            self.velocity = [dx, dy]
            # и свои координаты
            self.rect.x, self.rect.y = pos

            # гравитация будет одинаковой (значение константы)
            self.gravity = 1

        def update(self):
            # применяем гравитационный эффект:
            # движение с ускорением под действием гравитации
            self.velocity[1] += self.gravity
            # перемещаем частицу
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            # убиваем, если частица ушла за экран
            if not self.rect.colliderect(screen_rect):
                self.kill()

    def create_particles(self, position, im1):
        # количество создаваемых частиц
        particle_count = 20
        # возможные скорости
        numbers = range(-15, 16)
        for _ in range(particle_count):
            self.Particle(position, random.choice(numbers), random.choice(numbers), im1)

    class Cube(pygame.sprite.Sprite):
        def __init__(self, *pos, img):
            super().__init__()
            self.add(all_sprites)
            self.original_image = img
            self.image = self.original_image
            self.next_im = [self.image, pygame.transform.rotate(self.image, 90),
                            pygame.transform.rotate(self.image, 180),
                            pygame.transform.rotate(self.image, 270)]
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.original = self.image
            self.angle = 0
            self.holding = False
            self.mask = pygame.mask.from_surface(self.image)
            self.speed_y = 10
            # self.const_center_coord = 265, pos[1]

        def update(self):
            self.rect.left += speed

        def jump(self):
            global processing, start, n_y
            # print(processing, 'something')
            if self.holding:
                processing = True
            if processing:
                if start:
                    self.speed_y = 18
                    start = False
                    n_y = self.rect.y
                self.image = pygame.transform.rotate(self.original_image, self.angle % 360)
                self.angle -= 10  # Value will repeat after 359. This prevents angle to overflow.
                self.angle %= 360
                x, y = self.rect.center  # Save its current center.
                self.rect = self.image.get_rect()  # Replace old rect with new rect.
                self.rect.center = x, y
                self.rect.y -= self.speed_y
                self.speed_y -= 2
                if self.rect.y >= n_y:
                    self.speed_y = 0
                    processing = False
                    self.rect.y = n_y
                    start = True
                    if self.angle <= 45 or self.angle > 315:
                        im = self.next_im[0]
                        self.angle = 0
                    elif 46 < self.angle <= 135:
                        im = self.next_im[1]
                        self.angle = 90
                    elif 136 <= self.angle <= 225:
                        im = self.next_im[2]
                        self.angle = 180
                    else:
                        im = self.next_im[3]
                        self.angle = 270
                    self.image = im

    class Block(pygame.sprite.Sprite):
        def __init__(self, *pos):
            global all_sprites
            super().__init__()
            self.add(all_sprites)
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect()
            self.rect.topleft = pos

        def update(self):
            if self.rect.x + self.rect.w < 0:
                self.kill()

    class Spike(pygame.sprite.Sprite):
        def __init__(self, *pos):
            global all_sprites, spikes
            super().__init__()
            self.add(all_sprites)
            self.add(spikes)
            self.image = pygame.Surface((30, 30))
            clk = self.image.get_at((0, 0))
            self.image.set_colorkey(clk)
            self.image = self.image.convert_alpha()
            pygame.draw.polygon(self.image, (255, 0, 0), [(0, 30), (15, 0), (30, 30)])
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.mask = pygame.mask.from_surface(self.image)

        def update(self):
            if self.rect.x + self.rect.w < 0:
                self.kill()

    class Ground(pygame.sprite.Sprite):
        def __init__(self, *pos):
            super().__init__()
            self.add(all_sprites)
            self.image = pygame.Surface((width + 15, 1))
            self.image.fill((255, 255, 255))
            self.rect = self.image.get_rect()
            self.rect.topleft = pos

        def update(self):
            if access:
                self.rect.left += speed

    def main(self):
        global size, access, k, b, width, holding1, holding2, height, all_sprites, spikes, clock, speed, SCORE, bgen
        pygame.mixer.init()
        self.running = True
        pygame.mixer.music.load(os.path.join('data', "Stay_Inside_Me_Official.ogg"))
        self.screen = pygame.display.set_mode(size)
        self.screen2 = pygame.Surface(size)
        pygame.mouse.set_visible(False)
        trf = self.load_image(os.path.join('data', 'trollface.png'))
        trf = pygame.transform.scale(trf, (30, 30))
        trf = pygame.transform.flip(trf, True, False)
        self.player = self.Cube(0, 470, img=trf)
        self.ground = self.Ground(-15, 500)
        pygame.mixer.music.play(-1)
        self.temp = list(range(1, 4))
        self.fire1 = self.load_image(os.path.join('data', 'star.png'))
        self.camera = self.Camera()
        self.score = self.Score()
        all_sprites.add(self.score)
        pygame.time.set_timer(score_inc, 100)
        pygame.time.set_timer(gen, 3000)
        while self.running:
            self.player.jump()
            if self.player.rect.x + self.player.rect.w // 2 >= 265:
                access = True
                self.camera.update(self.player)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    self.running = False
                if event.type == score_inc:
                    SCORE += 1
                if event.type == gen:
                    bgen = True
                if bgen and random.choice(self.temp) == 1:
                    self.Spike(self.player.rect.x + self.player.rect.w * 20 + 40, self.ground.rect.y - 30)
                    bgen = False
                elif bgen and random.choice(self.temp) == 2:
                    self.Spike(self.player.rect.x + self.player.rect.w * 20 + 40, self.ground.rect.y - 30)
                    self.Spike(self.player.rect.x + self.player.rect.w * 20 + 40 + 30, self.ground.rect.y - 30)
                    bgen = False
                elif bgen and random.choice(self.temp) == 3:
                    self.Spike(self.player.rect.x + self.player.rect.w * 20 + 40, self.ground.rect.y - 30)
                    self.Spike(self.player.rect.x + self.player.rect.w * 20 + 40 + 30, self.ground.rect.y - 30)
                    self.Spike(self.player.rect.x + self.player.rect.w * 20 + 40 + 60, self.ground.rect.y - 30)
                    bgen = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    holding1 = True
                elif event.type == pygame.KEYUP:
                    holding1 = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    holding2 = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    holding2 = False
                self.player.holding = holding1 or holding2
            self.screen2.fill((0, 0, 0))
            all_sprites.draw(self.screen2)
            all_sprites.update()
            clock.tick(60)
            for sprite in all_sprites:
                self.camera.apply(sprite)
            self.screen.blit(self.screen2, self.screen2.get_rect())
            if pygame.sprite.spritecollideany(self.player, spikes, pygame.sprite.collide_mask):
                self.screen2.fill((0, 0, 0))
                expcoords = self.player.rect.center
                self.player.kill()
                pygame.mixer.music.stop()
                self.end_sound.play()
                speed = 0
                if not b:
                    self.create_particles(expcoords, self.fire1)
                    b = True
                all_sprites.draw(self.screen2)
                all_sprites.update()
                self.screen.blit(self.screen2, self.screen2.get_rect())
                while particles:
                    self.screen2.fill((0, 0, 0))
                    all_sprites.draw(self.screen2)
                    all_sprites.update()
                    self.screen.blit(self.screen2, self.screen2.get_rect())
                self.running = False
            pygame.display.flip()
        start = True
        access = False
        processing = False
        holding1 = False
        holding2 = False
        b = False
        k = 0
        n_y = 0
        SCORE = 0
        speed = 7
        self.player.image = self.player.next_im[0]
        all_sprites = pygame.sprite.Group()
        spikes = pygame.sprite.Group()
        all_sprites.draw(self.screen2)
        self.screen.blit(self.screen2, self.screen2.get_rect())
        pygame.quit()
