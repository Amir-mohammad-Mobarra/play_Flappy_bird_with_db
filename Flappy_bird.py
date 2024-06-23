import pygame
import random
import time
import sqlite3

db_connect = sqlite3.connect('db.sqlite')
db_curser = db_connect.cursor()

pygame.init()

db_curser.execute('''CREATE TABLE IF NOT EXISTS HIGH_SCORES(high_score VARCHAR(5))''')
show_scores = False
counter_db = 0
start_db = True
screen_width, screen_height = 576, 700
status = True
x_y_bird_rect = (100, 288)
bird_movement = 0
gravity = 0.25
speed = 90
pipe_list = []
floor_x = 0
game_status = True
bird_list_index = 0
x_y_score_true = (300, 50)
score = 0
high_score = 0
active_score = True
# user event variables
creat_pipe = pygame.USEREVENT
flap = pygame.USEREVENT + 1
reset_game_show = pygame.USEREVENT + 2
pygame.time.set_timer(creat_pipe, 1200)
pygame.time.set_timer(flap, 100)
pygame.time.set_timer(reset_game_show, 15)
# font variable
game_font = pygame.font.Font('assets/font/Flappy.TTF', 40)


def connect(value):
    insert = f'''INSERT INTO HIGH_SCORES VALUES ({value})'''
    db_curser.execute(insert)
    db_connect.commit()


def select_h_scores():
    h_list = []
    db_curser.execute('''SELECT * FROM HIGH_SCORES''')
    db_connect.commit()
    for i in db_curser.fetchall():
        for x in i:
            h_list.append(int(x))
    return h_list


def delete_row1():
    db_curser.execute('''SELECT * FROM HIGH_SCORES LIMIT 1''')
    delete_high_score = f'''DELETE FROM HIGH_SCORES WHERE high_score = {db_curser.fetchone()[0]}'''
    db_curser.execute(delete_high_score)


def read_db():
    items = []
    db_curser.execute('''SELECT * FROM HIGH_SCORES''')
    for item2 in db_curser.fetchall():
        for item in item2:
            items.append(item)
    return items


def len_items():
    return len(read_db())


def show_8scores(scores):
    text = game_font.render('8 High Scores', False, 'red')
    text_rect = text.get_rect(center=(390, 50))
    screen.blit(text, text_rect)
    c = 0
    for show in range(60, 480, 60):
        if show // 60 != len_items():
            if c != 10:
                score_text1 = game_font.render(scores[0], False, 'white')
                score_text_rect1 = score_text1.get_rect(center=(show - 30, show - 30))
                screen.blit(score_text1, score_text_rect1)
                c = 10
            score_text2 = game_font.render(scores[show // 60], False, 'white')
            score_text_rect2 = score_text2.get_rect(center=(show, show))
            screen.blit(score_text2, score_text_rect2)
        else:
            break


def show_high_scores():
    score_text2 = game_font.render('show 8 h_scores click <s>', False, 'white')
    score_text_rect2 = score_text2.get_rect(center=(280, 520))
    screen.blit(score_text2, score_text_rect2)


def check_floor_x():
    global floor_x
    if floor_x == -576:
        floor_x = 0
    floor_x -= 3


def apply_gravity():
    global bird_movement, bird_image_rect
    bird_movement += gravity
    bird_image_rect.centery += bird_movement


def move_bird():
    global bird_movement
    bird_movement = 0
    bird_movement -= 8
    bird_image_rect.centery += bird_movement


def generate_pipes_rects():
    r_pipe = random.randrange(270, 550)
    top_pipes_rects = pipe_image.get_rect(midbottom=(700, r_pipe - 250))
    bottom_pipes_rects = pipe_image.get_rect(midtop=(700, r_pipe))
    return top_pipes_rects, bottom_pipes_rects


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    inside_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return inside_pipes


def blit_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 700:
            screen.blit(pipe_image, pipe)
        else:
            screen.blit(pygame.transform.flip(pipe_image, flip_x=False, flip_y=True), pipe)


def check_collision(pipes):
    global game_status, active_score
    for pipe in pipes:
        if bird_image_rect.colliderect(pipe):
            active_score = True
            game_over_sound.play()
            time.sleep(3)
            return False
        if bird_image_rect.top <= 0 or bird_image_rect.bottom >= 600:
            active_score = True
            game_over_sound.play()
            time.sleep(3)
            return False
    return True


def reset_game():
    global game_status, pipe_list, bird_image_rect, bird_movement, score
    game_status = True
    pipe_list.clear()
    bird_image_rect.center = x_y_bird_rect
    bird_movement = 0
    score = 0
    # one move bird
    move_bird()


def bird_animation():
    new_bird = bird_list[bird_list_index]
    new_bird_rect = new_bird.get_rect(center=(x_y_bird_rect[0], bird_image_rect.centery))
    return new_bird, new_bird_rect


def show_score(status_of_game):
    color_score = (255, 255, 255)
    bold = True
    if status_of_game:
        # score
        score_text = game_font.render(f'{score}', bold, color_score)
        score_text_rect = score_text.get_rect(center=x_y_score_true)
        screen.blit(score_text, score_text_rect)
    else:
        # score
        score_text = game_font.render(f'Score: {score}', bold, color_score)
        score_text_rect = score_text.get_rect(center=(200, 200))
        screen.blit(score_text, score_text_rect)
        # high score
        high_score_text = game_font.render(f'High Score: {high_score}', bold, color_score)
        high_score_text_rect = score_text.get_rect(center=(200, 350))
        screen.blit(high_score_text, high_score_text_rect)


def update_score():
    global score, high_score, active_score
    if pipe_list:
        for pipe in pipe_list:
            if 95 < pipe.centerx < 105 and active_score:
                score += 1
                take_sound.play()
                active_score = False
            if pipe.centerx < 0:
                active_score = True
    if score > high_score:
        high_score = score
    return high_score


def game_over():
    game_over_text = game_font.render('game over', True, 'red')
    game_over_text_rect = game_over_text.get_rect(center=(screen_width // 2, 70))
    screen.blit(game_over_text, game_over_text_rect)


def show_reset_game():
    for_reset_text = game_font.render('for reset click <r>', True, 'yellow')
    for_reset_text_rect = for_reset_text.get_rect(center=(300, 450))
    screen.blit(for_reset_text, for_reset_text_rect)


background_image = pygame.transform.scale(pygame.image.load('assets/img/bg2.png')
                                          , (screen_width, screen_height))

floor_image = pygame.transform.scale2x(pygame.image.load('assets/img/floor.png'))

bird_image_down = pygame.transform.scale2x(pygame.image.load('assets/img/red_bird_down_flap.png'))
bird_image_mid = pygame.transform.scale2x(pygame.image.load('assets/img/red_bird_mid_flap.png'))
bird_image_up = pygame.transform.scale2x(pygame.image.load('assets/img/red_bird_up_flap.png'))

bird_list = [bird_image_down, bird_image_mid, bird_image_up]

bird_image = bird_list[bird_list_index]
bird_image_rect = bird_image.get_rect(center=x_y_bird_rect)

pipe_image = pygame.transform.scale2x(pygame.image.load('assets/img/pipe_green.png'))

take_sound = pygame.mixer.Sound('assets/sound/smb_stomp.wav')

game_over_sound = pygame.mixer.Sound('assets/sound/smb_mario_die.wav')

screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

move_bird()

while True:

    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_bird()
            if event.key == pygame.K_r and not game_status:
                reset_game()
            if event.key == pygame.K_s and not game_status:
                show_scores = True

        if event.type == creat_pipe:
            pipe_list.extend(generate_pipes_rects())

        if event.type == flap:
            if bird_list_index < 2:
                bird_list_index += 1
            else:
                bird_list_index = 0
            bird_image, bird_image_rect = bird_animation()

        if event.type == reset_game_show and not game_status:
            show_reset_game()

    if game_status:
        screen.blit(floor_image, (floor_x, 600))
        screen.blit(floor_image, (floor_x + 576, 600))
        check_floor_x()

        game_status = check_collision(pipe_list)

        screen.blit(bird_image, bird_image_rect)
        apply_gravity()

        pipe_list = move_pipes(pipe_list)
        blit_pipes(pipe_list)

        update_score()

        show_score(True)
        counter_db = 0
        show_scores = False
    elif show_scores:
        show_8scores(read_db())
    else:
        show_high_scores()
        counter_db += 1

        show_score(False)

        screen.blit(floor_image, (floor_x, 600))
        screen.blit(floor_image, (floor_x + 576, 600))

        check_floor_x()
        game_over()
        if counter_db == 1:
            start_db = True
        if start_db:
            items = select_h_scores()
            if high_score not in items:
                connect(high_score)
            if len(select_h_scores()) % 9 == 0:
                delete_row1()
            start_db = False

    pygame.display.update()

    clock.tick(speed)
