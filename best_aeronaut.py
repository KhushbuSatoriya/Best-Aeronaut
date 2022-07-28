
import pgzrun #pip install pgzero
import random
WIDTH = 800
HEIGHT = 600

#define the actors
bird_speed = random.randint(1,3)
bird_flap = True
bird_flap_rate = 9
bird_alive = True
bird = Actor('bird-up', pos = (600,100))

balloon = Actor('balloon', pos = (400, 300))
balloon_up = True
game_running = True

tree = Actor('tree')
tree.x = 300
tree.y = HEIGHT - tree.height//2

thunder = Actor('thunder')
thunder_flag = False
thunder_sound = None

button_quit = Actor('quit', pos = (250, 200))
button_replay = Actor('replay', pos = (530,200))

#tones
beep = tone.create('Bb4', 0.5)
touch = tone.create('F4', 0.1)

#score
score = 0
show_high_score = False

def play_alarm():
    global beep
    beep.play()

def flap():
    global bird_flap
    if bird_flap:
        bird.image = 'bird-down'
        bird_flap = False
    else:
        bird.image = 'bird-up'
        bird_flap = True

    if not bird_alive:
        bird.angle = 180

def draw(): #autocalled to reflect the latest states of the actors
    global game_running, show_high_score
    if game_running:
        screen.blit('background', (0,0))

        # draw the actors
        bird.draw()
        balloon.draw()
        tree.draw()

        if thunder_flag:
            thunder.draw()

        screen.draw.text('Score: ' + str(score), topleft=(500, 50), fontname='arial', color='yellow', gcolor='green', fontsize=48, owidth=0.5, ocolor='black')

    else:
        screen.blit('game_ends', (0,0,))
        button_quit.draw()
        button_replay.draw()
        if show_high_score:
            screen.draw.text('New Record: ' + str(score), midtop=(WIDTH//2, 50), fontname='arial', color='yellow', gcolor='green', fontsize=48, owidth=0.5, ocolor='black')


def update(): #autocalled at frame rate
    global bird_speed, bird_flap_rate, score, bird_alive, balloon_up

    if bird_alive:
        bird.left -= bird_speed

    bird_flap_rate-=1
    if bird_flap_rate == 0:
        flap()
        bird_flap_rate=9
        if balloon_up:
            score+=1

    if bird.left + bird.width <0:
        bird.pos = random.randint(800,1600), random.randint(50,250)
        bird_speed = random.randint(1,3)

    #balloon control
    if balloon_up:
        if keyboard.right:
            if balloon.left + balloon.width >= WIDTH: # balloon touches the right wall
                touch.play() #play a tone
                balloon.left-=5 #push it left
            else:
                balloon.left+=1
        elif keyboard.left:
            if balloon.left <= 0: # balloon touches the left wall
                touch.play()
                balloon.left+=5
            else:
                balloon.left-=1
        elif keyboard.up:
            if balloon.top <= 0: # balloon touches the top wall
                touch.play()
                balloon.top +=5
            else:
                balloon.top-=1
        elif keyboard.down:
            if balloon.top + balloon.height >= HEIGHT: # balloon touches the ground
                touch.play()
                game_ends() #game ends (landing)
            else:
                balloon.top+=1

    #clash
    if bird_alive and balloon_up and bird.collidepoint(balloon.pos) :
        print('bird strikes the ballon')
        animate(balloon, pos=(balloon.x, HEIGHT - balloon.height // 2), tween='bounce_end', duration=10, on_finished=game_over)
        balloon_up = False
        clock.schedule_interval(play_alarm, 1)

    if thunder_flag and thunder.collidepoint(bird.pos):
        print('bird dies')
        #pos: target pos
        #tween: animation
        #duration: time taken to reach the target pos from current pos
        #on_finished = register a function to be called as animation ends
        animate(bird, pos=(bird.x, HEIGHT - bird.height // 2), tween='bounce_end', duration=10, on_finished=relive)
        bird_alive = False

    if  balloon_up and thunder_flag and balloon.collidepoint(thunder.pos):
        print('thunder strikes the balloon')
        animate(balloon, pos=(balloon.x, HEIGHT - balloon.height // 2), tween='bounce_end', duration=10, on_finished=game_over)
        balloon_up = False
        clock.schedule_interval(play_alarm, 1)

    if balloon_up and balloon.collidepoint(tree.pos):
        print('balloon collides with the tree')
        animate(balloon, pos=(balloon.x, HEIGHT - balloon.height // 2), tween='bounce_end', duration=5, on_finished=game_over)
        balloon_up = False
        clock.schedule_interval(play_alarm, 1)

def on_mouse_down(pos, button):
    global game_running, balloon_up, score, show_high_score
    if not game_running:
        if button_replay.collidepoint(pos):
            score = 0
            game_running = True
            music.play('instrumental')
            balloon_up = True
            clock.schedule_interval(thunder_strike, 10)
            balloon.image = 'balloon'
            balloon.pos = (400, 300)
            show_high_score = False

        elif button_quit.collidepoint(pos):
            quit()


def game_ends():
    global balloon_up, game_running
    balloon_up = False
    music.stop()
    clock.unschedule(thunder_strike)
    game_running = False
    print('Game Ends')
    update_score()

def game_over():
    global game_running, balloon_up
    balloon.image = 'balloon_grounded.png'
    balloon.y = HEIGHT - balloon.height//2
    clock.unschedule(play_alarm)
    clock.unschedule(thunder_strike)
    music.stop()
    balloon_up = False
    game_running = False
    print('Game Ends')
    update_score()


def update_score():
    global score, show_high_score
    score_file = 'd:/temp/best_aeronaut_score.txt'
    recorded_score = file_read_score(score_file)

    if int(score) > int(recorded_score):
        show_high_score = True
        file_write_score(score_file, str(score))

def thunder_strike():
    global thunder_flag, thunder_sound
    thunder_positions = [(80,100), (410,160), (740,110)]
    thunder.pos = random.choice(thunder_positions)
    thunder_flag = True
    thunder_sound = sounds.thunder_sound.play()
    clock.schedule_unique(thunder_strike_over, 2)

def thunder_strike_over():
    global thunder_flag, thunder_sound
    thunder_flag = False
    thunder_sound.stop()

def relive():
    global bird_alive
    #balloon.image = 'balloon_grounded'
    bird.left = -150
    bird_alive = True

def file_write_score(file, score):
    try:
        #open the file
        file_handle = open(file, 'w') #creates or overwrites the file
        #write the score
        file_handle.write(score)
        #close the file
        file_handle.close()
    except:
        pass

def file_read_score(file):
    try:
        #open the file for reading
        file_handle = open(file, 'r')
        #read the first line
        score = file_handle.readline()
        #close the file
        file_handle.close()
        return score
    except:
        return '0'




clock.schedule_interval(thunder_strike, 10)
music.play('instrumental') #auto loops
pgzrun.go()
