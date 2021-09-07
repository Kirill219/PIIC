import pygame
import os
import random

pygame.font.init()
pygame.display.set_caption('Space Invaders')
w = 900
h = 750
screen = pygame.display.set_mode((w, h))

player_ship = pygame.image.load(os.path.join("assets", "blue_ship.png"))

enemy_green_ship = pygame.image.load(os.path.join("assets", "enemy_green_ship.png"))
enemy_red_ship = pygame.image.load(os.path.join("assets", "enemy_red_ship.png"))
enemy_yellow_ship = pygame.image.load(os.path.join("assets", "enemy_yellow_ship.png"))

blue_laser = pygame.image.load(os.path.join("assets", "laser_blue.png"))
green_laser = pygame.image.load(os.path.join("assets", "laser_green.png"))
red_laser = pygame.image.load(os.path.join("assets", "laser_red.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "laser_yellow.png"))

bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space_bg.png")), (w, h))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, h):
        return not(self.y <= h and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    CoolDown = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(h):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.CoolDown:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def width(self):
        return self.ship_img.get_width()

    def height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = player_ship
        self.laser_img = blue_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(h):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    color_init = {
        "green": (enemy_green_ship, green_laser),
        "red": (enemy_red_ship, red_laser),
        "yellow": (enemy_yellow_ship, yellow_laser)
    }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_init[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("impact", 40)
    lost_font = pygame.font.SysFont("impact", 80)
    win_font = pygame.font.SysFont("impact", 80)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5
    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    win = False
    win_count = 0

    def draw_game():
        screen.blit(bg, (0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (227, 207, 87))
        level_label = main_font.render(f"Level: {level}", 1, (227, 207, 87))

        screen.blit(lives_label, (10, 10))
        screen.blit(level_label, (w - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if lost:
            lost_label = lost_font.render("Lose", 1, (255, 0, 0))
            screen.blit(lost_label, (w/2 - lost_label.get_width()/2, 350))

        if win:
            win_label = win_font.render("WIN", 1, (227, 207, 87))
            screen.blit(win_label, (w/2 - win_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        draw_game()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            for i in range(wave_length):
                if level == 1:
                    enemy = Enemy(random.randrange(100, w - 200), random.randrange(-1500, -100), ("green"))
                    enemies.append(enemy)
                if level == 2:
                    enemy = Enemy(random.randrange(100, w - 200), random.randrange(-1500, -100), ("yellow"))
                    enemies.append(enemy)
                if level == 3:
                    enemy = Enemy(random.randrange(100, w - 200), random.randrange(-1500, -100), ("red"))
                    enemies.append(enemy)
                if level == 4:
                    enemy = Enemy(random.randrange(100, w - 200), random.randrange(-1500, -100), random.choice(["green", "yellow"]))
                    enemies.append(enemy)
                if level >= 5:
                    enemy = Enemy(random.randrange(100, w - 200), random.randrange(-1500, -100), random.choice(["green", "red", "yellow"]))
                    enemies.append(enemy)
            wave_length += 3

        if level >= 6:
            win = True
            win_count += 1
        if win:
            if win_count > FPS * 3:
                run = False
            else:
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.width() < w:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.height() + 20 < h:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0, 60) == 1:
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.height() > h:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def menu():
    title_font = pygame.font.SysFont("impact", 65)
    run = True
    while run:
        screen.blit(bg, (0, 0))
        title_label = title_font.render("Press any button to start!", 1, (227, 207, 87))
        screen.blit(title_label, (w/2 - title_label.get_width()/2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP:
                main()

    pygame.quit()

menu()

