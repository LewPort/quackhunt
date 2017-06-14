import pygame
import time
import random

pygame.init()

debug = False
monitor_res_width = pygame.display.Info().current_w #Get monitor resolution width

aspect_ratio = 1.78
display_width = 1280
display_height = int(display_width // aspect_ratio)

game_display = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)

pygame.display.set_caption('QUACKHUNT')

red = (255,0,50)
grey = (200,200,230)

scorefont = pygame.font.SysFont("impact", 70)
infofont = pygame.font.SysFont("impact", 20)

scene_bg = pygame.image.load('./img/bg.jpg')
scene_bg = pygame.transform.scale(scene_bg, (display_width, display_height))
crosshair_orig = pygame.image.load('./img/crosshair.png')
crosshair_img = pygame.transform.rotozoom(crosshair_orig, 0, 0.4) #Scaling the crosshair down

music = False

#Loading Sounds
pygame.mixer.music.load('./sfx/ambience.ogg')
duck_startle_sfx = pygame.mixer.Sound('./sfx/duck_startle.ogg')
chicken_startle_sfx = pygame.mixer.Sound('./sfx/chicken.ogg')
gunshot_sfx = pygame.mixer.Sound('./sfx/gunshot.ogg')
mozart = pygame.mixer.Sound('./music/mozart.ogg')
clock = pygame.time.Clock()

#Blueprint for ducks and their behaviour
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



#Generates instances of the Duck class, but won't 'launch' them on to the screen yet. That's done in the gameloop.
def duckgen(n):
    global ducksreleased
    if duck == {}:
        duck_startle_sfx.play()
        for i in range(n):
            if debug == True:
                duck[i] = Duck(sprite='./img/may1.png',
                              x_pos=random.uniform(display_width * 0.1, display_width * 0.9),
                              y_pos=display_height * 0.8,
                              z_pos=0.1,
                              x_mov= random.uniform(-1, 1),
                              y_mov= random.uniform(2, 4),
                              z_mov = random.randrange(1,3),
                              rotation_rate=0.5)

            else:
                duck[i] = Duck(sprite='./img/may1.png',
                               x_pos=random.uniform(display_width * 0.1, display_width * 0.9),
                               y_pos=display_height * 0.8,
                               z_pos=0.1,
                               x_mov=random.uniform(-5, 5),
                               y_mov=random.uniform(6, 8),
                               z_mov=random.randrange(2, 8),
                               rotation_rate=5)
            ducksreleased += 1


#Detects if a shot has hit a duck.
def duck_hit_detection():
    global gunshottime
    global gunloaded
    cursorloc = pygame.mouse.get_pos()

    if debug == True: #Draws a red dot where the pygame thinks the cursor is
        pygame.draw.rect(game_display, red, (cursorloc[0], cursorloc[1], 10, 10))

    if gunshottime + gunreloadinterval <= time.time(): #Simulates the time it takes for a shot to reload, so you can't just spray like a machine gun.
        gunloaded = True
    else:
        gunloaded = False

    if gunloaded == True and pygame.mouse.get_pressed()[0]: #Here's where the gun fires and hits the ducks
        gunshot_sfx.play()
        gunshottime = time.time()
        for i in duck:
            duckarea = duck[i].duck_target_area()
            if duckarea[0] < cursorloc[0] < duckarea[1] and duckarea[2] < cursorloc[1] < duckarea[1]:
                if duck[i].dead == False:
                    duck[i].deadduck()


def draw_crosshair(): #This is pretty self explanatory
    loc = pygame.mouse.get_pos()
    game_display.blit(crosshair_img, (loc[0] - (crosshair_img.get_width() / 2), loc[1] - crosshair_img.get_height() /2))

def stopwatch(): #Mechanism used to mark the time at which ducks are released onto the screen.
    elapsed = time.time() - stopwatch_start
    elapsed = int(elapsed)
    return elapsed

def reset_stopwatch():
    global stopwatch_start
    stopwatch_start = time.time()

def gametimer(): #Times how long the game has been going, which will be displayed on screen via the gameloop
    timetogo = (int(gamestart) + (gameduration)) - time.time()
    if timetogo < 0:
        timetogo = 0
    timetogo = time.strftime('%M:%S', time.gmtime(timetogo))
    return timetogo

def summary(score): #Offering a summary of the player's score
    if score > 79:
        return 'Strong & Stable'
    elif score > 59:
        return 'Somewhat Stable'
    elif score > 39:
        return 'Weak and Wobbly'
    elif score > 19:
        return 'No Overall Control'
    else:
        return 'Gove-esque'

########### GAME STARTS HUR ############

playing = True

gamestart = time.time()
gameduration = 60 * 1.5 #Game duration in secs

pygame.mouse.set_visible(False) #Hiding the standard cursor so it can be replaced with a crosshair

pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(-1)

if music == True:
    mozart.play(loops=-1)
    mozart.set_volume(1)

stopwatch_start = time.time()
duck_release_time = 2 #initial time before the ducks are released, in seconds. This is then changed via the gameloop
gunloaded = True
gunreloadinterval = 1 #seconds (default is 1)
gunshottime = time.time() #Logs the time that the gun was fired, in order to give a 1 second reload time


duck = {} #The ducks currently in play!

ducksreleased = 0 #Total number of ducks released. Used to calculate score.
hitcount = 0 #Ducks successfully shot


#Game Loop
while playing:

    game_display.blit(scene_bg, (0, 0))

    #Ducks generated here nai so they are
    if stopwatch() == duck_release_time and time.time() < gamestart + gameduration:
        duckgen(random.randrange(1,4))

    #Iterates through the duck dictionary and draws them to the screen
    for i in duck:
        duck[i].draw_duck()

    draw_crosshair() #obv

    #Players score is processed here
    if ducksreleased > 0:
        score = round((hitcount / ducksreleased) * 100)
    else:
        score = 0

    #Key-input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                playing = False
            elif event.key == pygame.K_m:
                if music == True:
                    mozart.stop()
                    music = False
                else:
                    mozart.play(loops=-1)
                    music = True

    duck_hit_detection()

    scoredisplay = scorefont.render("Score: %s%%" % score, 1, red)
    game_display.blit(scoredisplay, (display_width * 0.05, display_height * 0.8))
    timer = scorefont.render(gametimer(), 1, red)
    game_display.blit(timer, (display_width * 0.05, display_height * 0.05))
    info = infofont.render("Press 'esc' to Quit // Press M to get in the mood.", 1, grey)
    game_display.blit(info, (display_width * 0.05, display_height * 0.92))
    
    if debug == True: 
        fps = infofont.render(str(int(clock.get_fps())) + 'fps', 1, grey)
        game_display.blit(fps, ((display_width/2) - (fps.get_width()/2), display_height // 2))

    #Display score & Summary at the end of the game
    if time.time() > gamestart + gameduration:
        if gamestart + gameduration + 60 < time.time(): #period of time that the summary stays on screen (secs)
            playing = False
        else:
            if music == False: #Triggers music at the end
                music = True
                mozart.play()
            timesup = scorefont.render('%s%%: %s' % (score, summary(score).upper()), 1, red)
            game_display.blit(timesup, ((display_width/2) - (timesup.get_width()/2), display_height // 2))


    if stopwatch() > 4: #The number of seconds between ducks being generated
        reset_stopwatch()
        duck_release_time = random.randrange(1, 2)
        duck.clear()

    pygame.display.update()
    clock.tick(30)

pygame.quit()
