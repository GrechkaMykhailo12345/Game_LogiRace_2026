from pygame import *
from random import randint
from time import time as timer

init()
font.init()
mixer.init()

try:
    mixer.music.load('the-final-boss-battle-158700.mp3')
    mixer.music.play(-1) 
    fire_sound = mixer.Sound('fire.ogg')
except:
    fire_sound = None


win_width, win_height = 1280, 720
window = display.set_mode((win_width, win_height))
display.set_caption("Mars Mission: Hardcore Edition")


font_title = font.Font(None, 120); font_btn_main = font.Font(None, 60) 
font_btn_small = font.Font(None, 45); font_score = font.Font(None, 36); font_stats = font.Font(None, 55)


img_back = "gameground.png"; img_hero = "Rover_Mars_Hero.png"; img_bullet = "bullet.png"
img_enemy = "Shahed.png"; img_ast = "meteorites.png"


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        try: self.image = transform.scale(image.load(player_image), (size_x, size_y))
        except: self.image = Surface((size_x, size_y)); self.image.fill((150, 150, 150))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = player_x, player_y
    def reset(self): window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5: self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80: self.rect.x += self.speed
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)
        if fire_sound: fire_sound.play()

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x, self.rect.y = randint(80, win_width - 80), 0
            lost += 1 

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x, self.rect.y = randint(80, win_width - 80), 0

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0: self.kill()

def draw_btn(text, x, y, w, h, base_color, current_font, enabled=True):
    mouse_pos = mouse.get_pos(); rect_btn = Rect(x, y, w, h)
    if not enabled:
        draw.rect(window, (50, 50, 50), rect_btn, border_radius=10)
        txt = current_font.render(text + " (Owned)", True, (120, 120, 120))
    else:
        color = base_color
        if rect_btn.collidepoint(mouse_pos):
            color = (min(base_color[0]+50, 255), min(base_color[1]+50, 255), min(base_color[2]+50, 255))
            draw.rect(window, color, rect_btn, border_radius=12)
            draw.rect(window, (255, 255, 255), rect_btn, 3, border_radius=12)
            global hover_on_btn; hover_on_btn = True
        else: draw.rect(window, color, rect_btn, border_radius=10)
        txt = current_font.render(text, True, (255, 255, 255))
    window.blit(txt, (x+(w-txt.get_width())//2, y+(h-txt.get_height())//2))
    return rect_btn


coins_total = 0 
coins_in_game = 0 
score, lost, life = 0, 0, 3
max_bullets = 5; enemy_speed_boost = 0 
finish, run = False, True; state = "MENU" 
num_fire, rel_time, hover_on_btn = 0, False, False

ship = Player(img_hero, win_width//2, win_height - 100, 80, 100, 10)
monsters, meteorites, bullets = sprite.Group(), sprite.Group(), sprite.Group()

def restart():
    global score, lost, life, finish, num_fire, rel_time, enemy_speed_boost, coins_in_game
    score, lost, life, finish, num_fire, rel_time, enemy_speed_boost = 0, 0, 3, False, 0, False, 0
    coins_in_game = 0 
    monsters.empty(); meteorites.empty(); bullets.empty()
    for i in range(5): monsters.add(Enemy(img_enemy, randint(80, win_width-80), -40, 80, 50, randint(3, 7)))
    for i in range(2): meteorites.add(Asteroid(img_ast, randint(30, win_width-30), -40, 80, 50, randint(4, 9)))


while run:
    hover_on_btn = False; window.fill((0, 0, 0))
    try: bg = transform.scale(image.load(img_back), (win_width, win_height)); window.blit(bg, (0, 0))
    except: pass

    for e in event.get():
        if e.type == QUIT: run = False
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            if state == "GAME" and not finish: state = "PAUSE"
            elif state == "PAUSE": state = "GAME"
        if e.type == MOUSEBUTTONDOWN:
            if state == "MENU":
                if btn_play.collidepoint(e.pos): restart(); state = "GAME"
                if btn_shop_main.collidepoint(e.pos): state = "SHOP"
                if btn_quit_main.collidepoint(e.pos): run = False
            elif state == "SHOP":
                if btn_buy1.collidepoint(e.pos) and coins_total >= 25 and max_bullets < 10:
                    coins_total -= 25; max_bullets = 10
                if btn_buy2.collidepoint(e.pos) and coins_total >= 50 and max_bullets < 15:
                    coins_total -= 50; max_bullets = 15
                if btn_buy3.collidepoint(e.pos) and coins_total >= 75 and max_bullets < 20:
                    coins_total -= 75; max_bullets = 20
                if btn_back_shop.collidepoint(e.pos): state = "MENU"
            elif state == "PAUSE":
                if btn_resume.collidepoint(e.pos): state = "GAME"
                if btn_pause_menu.collidepoint(e.pos): state = "MENU"
                if btn_pause_quit.collidepoint(e.pos): run = False
            elif state == "GAME" and finish:
                if btn_again.collidepoint(e.pos): restart()
                if btn_back_to_menu.collidepoint(e.pos): state = "MENU"
                if btn_quit_game.collidepoint(e.pos): run = False
        if state == "GAME" and not finish and e.type == KEYDOWN and e.key == K_SPACE:
            if num_fire < max_bullets and not rel_time: num_fire += 1; ship.fire()
            if num_fire >= max_bullets and not rel_time: last_time = timer(); rel_time = True

    if state == "MENU":
        title = font_title.render("Mars Mission: Hardcore Edition", True, (255, 255, 255))
        window.blit(title, (win_width//2 - title.get_width()//2, 100))
        window.blit(font_score.render(f"Coins: {coins_total}", True, (255, 215, 0)), (20, 20))
        btn_play = draw_btn("PLAY", win_width//2 - 150, 300, 300, 70, (0, 120, 0), font_btn_main)
        btn_shop_main = draw_btn("SHOP", win_width//2 - 150, 400, 300, 70, (180, 150, 0), font_btn_main)
        btn_quit_main = draw_btn("QUIT", win_width//2 - 150, 500, 300, 70, (120, 0, 0), font_btn_main)

    elif state == "SHOP":
        title = font_title.render("MARS SHOP", True, (255, 215, 0))
        window.blit(title, (win_width//2 - title.get_width()//2, 50))
        
        coins_txt = font_stats.render(f"Coins: {coins_total}", True, (255, 255, 255))
        window.blit(coins_txt, (win_width//2 - coins_txt.get_width()//2, 140))
        
        ammo_txt = font_score.render(f"Ammo: {max_bullets}", True, (0, 255, 0))
        window.blit(ammo_txt, (win_width//2 - ammo_txt.get_width()//2, 200))
        
        btn_buy1 = draw_btn("10 Ammo (25 Coins)", win_width//2-250, 280, 500, 60, (50,50,150), font_btn_small, max_bullets < 10)
        btn_buy2 = draw_btn("15 Ammo (50 Coins)", win_width//2-250, 360, 500, 60, (50,50,150), font_btn_small, max_bullets < 15)
        btn_buy3 = draw_btn("20 Ammo (75 Coins)", win_width//2-250, 440, 500, 60, (50,50,150), font_btn_small, max_bullets < 20)
        btn_back_shop = draw_btn("BACK", win_width//2-150, 550, 300, 60, (100,100,100), font_btn_small)

    elif state == "PAUSE":
        overlay = Surface((win_width, win_height)); overlay.set_alpha(170); overlay.fill((0,0,0)); window.blit(overlay, (0,0))
        p_title = font_title.render("PAUSE", True, (255, 255, 255)); window.blit(p_title, (win_width//2 - p_title.get_width()//2, 150))
        btn_resume = draw_btn("RESUME", win_width//2-125, 300, 250, 60, (0,120,0), font_btn_small)
        btn_pause_menu = draw_btn("MENU", win_width//2-125, 380, 250, 60, (80,80,80), font_btn_small)
        btn_pause_quit = draw_btn("QUIT", win_width//2-125, 460, 250, 60, (120,0,0), font_btn_small)

    elif state == "GAME":
        if not finish:
            ship.update(); monsters.update(); meteorites.update(); bullets.update()
            ship.reset(); monsters.draw(window); meteorites.draw(window); bullets.draw(window)
            if rel_time:
                if timer() - last_time < 3: window.blit(font_score.render('RELOADING...', True, (255,0,0)), (win_width//2-60, win_height-50))
                else: num_fire, rel_time = 0, False
            if sprite.groupcollide(monsters, bullets, True, True):
                score += 1; coins_in_game += 1 
                if score % 5 == 0: enemy_speed_boost += 1.0
                monsters.add(Enemy(img_enemy, randint(80, win_width-80), -40, 80, 50, randint(3,7)+enemy_speed_boost))
            if sprite.spritecollide(ship, monsters, True) or sprite.spritecollide(ship, meteorites, True):
                life -= 1
                if len(monsters) < 5: monsters.add(Enemy(img_enemy, randint(80, win_width-80), -40, 80, 50, randint(3,7)+enemy_speed_boost))
            
            window.blit(font_score.render(f"Score: {score}", True, (255,255,255)), (20, 20))
            window.blit(font_score.render(f"Skipped: {lost}", True, (255,255,255)), (20, 50))
            window.blit(font_score.render(f"Coins: {coins_total + coins_in_game}", True, (255,215,0)), (20, 80))
            window.blit(font_score.render(f"Ammo: {max_bullets - num_fire}", True, (0, 255, 0)), (20, 110))
            window.blit(font_title.render(str(life), True, (0,255,0) if life>1 else (255,0,0)), (win_width-80, 20))

            if life <= 0 or score >= 100: 
                finish = True
                coins_total += coins_in_game
                if life <= 0: res_txt, res_col = "GAME OVER", (180,0,0)
                else: res_txt, res_col = "YOU WIN!", (255,255,255)
        else:
            msg = font_title.render(res_txt, True, res_col); window.blit(msg, (win_width//2 - msg.get_width()//2, 100))
            final_stats_text = f"Score: {score} | Skipped: {lost} | Total Coins: {coins_total}"
            final_stats = font_stats.render(final_stats_text, True, (255,255,255))
            window.blit(final_stats, (win_width // 2 - final_stats.get_width() // 2, 220))
            
            btn_again = draw_btn("PLAY AGAIN", win_width//2-390, 450, 250, 60, (0,120,0), font_btn_small)
            btn_back_to_menu = draw_btn("MENU", win_width//2-125, 450, 250, 60, (80,80,80), font_btn_small)
            btn_quit_game = draw_btn("QUIT", win_width//2+140, 450, 250, 60, (120,0,0), font_btn_small)

    mouse.set_cursor(SYSTEM_CURSOR_HAND if hover_on_btn else SYSTEM_CURSOR_ARROW)
    display.update(); time.delay(30)