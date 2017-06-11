import pygame
import time
import random

pygame.init()

debug = False
monitor_res_width = pygame.display.Info().current_w

aspect_ratio = 1.78
display_width = 1280
display_height = int(display_width // aspect_ratio)

game_display = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)

pygame.display.set_caption('QUACKHUNT')

red = (255,0,50)

scorefont = pygame.font.SysFont("impact", 70)

music = True

#Loading Sounds
pygame.mixer.music.load('./sfx/ambience.ogg')
duck_startle_sfx = pygame.mixer.Sound('./sfx/duck_startle.ogg')
chicken_startle_sfx = pygame.mixer.Sound('./sfx/chicken.ogg')
gunshot_sfx = pygame.mixer.Sound('./sfx/gunshot.ogg')
mozart = pygame.mixer.Sound('./music/mozart.ogg')
clock = pygame.time.Clock()

def drawbackground():
    scene_bg = pygame.image.load('./img/bg.jpg')
    scene_bg = pygame.transform.scale(scene_bg, (display_width, display_height))
    game_display.blit(scene_bg, (0, 0))


class Duck:
    duck_number = 0

    def __init__(self, sprite, x_pos, y_pos, z_pos, x_mov, y_mov, z_mov, rotation_rate):
        Duck.duck_number += 1
        self.sprite = sprite
        self.sprite = pygame.image.load(self.sprite)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.z_pos = z_pos
        self.x_mov = x_mov
        self.y_mov = y_mov
        self.z_mov = z_mov / 10000
        self.rotation_rate = rotation_rate
        self.rotation_amount = 0
        self.scaled_duck = pygame.transform.rotozoom(self.sprite, 0, self.z_pos)
        self.dead = False

    def draw_duck(self):
        self.z_pos = self.z_pos - self.z_mov
        self.scaled_duck = pygame.transform.rotozoom(self.sprite, 0, self.z_pos)
        self.x_pos = self.x_pos - self.x_mov
        self.y_pos = self.y_pos - self.y_mov
        game_display.blit(self.scaled_duck, (self.x_pos, self.y_pos))
        if debug == True:
            pygame.draw.rect(game_display, red, (self.duck_centre()[0], self.duck_centre()[1], 10, 10))
            pygame.draw.rect(game_display, red, (self.duck_target_area()[0], self.duck_target_area()[2], 5, 5))
            pygame.draw.rect(game_display, red, (self.duck_target_area()[0], self.duck_target_area()[3], 5, 5))
            pygame.draw.rect(game_display, red, (self.duck_target_area()[1], self.duck_target_area()[2], 5, 5))
            pygame.draw.rect(game_display, red, (self.duck_target_area()[1], self.duck_target_area()[3], 5, 5))

    def duck_centre(self):
        x = self.x_pos + (self.scaled_duck.get_width() // 2)
        y = self.y_pos + (self.scaled_duck.get_height() // 2)
        return x, y

    def duck_target_area(self):
        xmin = self.x_pos
        xmax = self.x_pos + self.scaled_duck.get_width()
        ymin = self.y_pos
        ymax = self.y_pos + self.scaled_duck.get_height()
        return xmin, xmax, ymin, ymax

    def deadduck(self):
        global hitcount
        chicken_startle_sfx.play()
        self.dead == True
        hitcount += 1
        self.y_mov -= 20

        print('A HIT')




def duckgen(n):

    if debug == True:
        if duck == {}:
            duck_startle_sfx.play()
            for i in range(n):
                duck[i] = Duck(sprite='./img/may1.png',
                      x_pos=random.uniform(display_width * 0.1, display_width * 0.9),
                      y_pos=display_height * 0.8,
                      z_pos=0.1,
                      x_mov= random.uniform(-1, 1),
                      y_mov= random.uniform(2, 4),
                      z_mov = random.randrange(1,3),
                      rotation_rate=0.5)

    else:
        if duck == {}:
            duck_startle_sfx.play()
            for i in range(n):
                duck[i] = Duck(sprite='./img/may1.png',
                      x_pos=random.uniform(display_width * 0.1, display_width * 0.9),
                      y_pos=display_height * 0.8,
                      z_pos=0.1,
                      x_mov= random.uniform(-10, 10),
                      y_mov= random.uniform(6, 10),
                      z_mov = random.randrange(5,15),
                      rotation_rate=0.5)


def draw_all_ducks():

    for i in duck:
        duck[i].draw_duck()

def duck_hit_detection():
    global gunshottime
    global gunloaded
    cursorloc = pygame.mouse.get_pos()

    if debug == True:
        pygame.draw.rect(game_display, red, (cursorloc[0], cursorloc[1], 10, 10))
        #mark_shot()

    if gunshottime + 1 <= time.time():
        gunloaded = True
    else:
        gunloaded = False


    if gunloaded == True and pygame.mouse.get_pressed()[0]:
        gunshot_sfx.play()
        gunshottime = time.time()
        for i in duck:
            duckarea = duck[i].duck_target_area()
            if duckarea[0] < cursorloc[0] < duckarea[1] and duckarea[2] < cursorloc[1] < duckarea[1]:
                if duck[i].dead == False:
                    duck[i].deadduck()
            else:
                print('Empty click')

def mark_shot():
    loc = pygame.mouse.get_pos()
    while gunloaded == False:
        pygame.draw.rect(game_display, red, (loc[0], loc[1], 10, 10))


def reset_stopwatch():
    global stopwatch_start
    stopwatch_start = time.time()

def stopwatch():
    elapsed = time.time() - stopwatch_start
    elapsed = int(elapsed)
    return elapsed





########### GAME STARTS HUR ############

playing = True

pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)

if music == True:
    mozart.play(loops=-1)
    mozart.set_volume(0.8)

stopwatch_start = time.time()
duck_release_time = random.randrange(1,3)
gunloaded = True
gunshottime = time.time()

duck = {}

hitcount = 0



#Game Loop
while playing:

    drawbackground()

    if stopwatch() == duck_release_time:
        duckgen(random.randrange(1,4)) #Gener8 a ranom amount of ducks

    draw_all_ducks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                playing = False
            if event.key == pygame.K_m:
                if music == True:
                    mozart.stop()
                    music = False
                else:
                    mozart.play(loops=-1)
                    music = True

    duck_hit_detection()
    score = scorefont.render("Score: %s" % hitcount, 1, red)
    game_display.blit(score, (display_width * 0.05, display_height * 0.8))

    if stopwatch() > 10:
        reset_stopwatch()
        duck_release_time = random.randrange(0, 5)
        duck.clear()

    pygame.display.update()
    clock.tick(30)

pygame.quit()