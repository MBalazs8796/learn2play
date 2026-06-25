import pygame, sys
from pygame.locals import *
import random
 
pygame.init()
 
FPS = 60
FramePerSec = pygame.time.Clock()
 
# Predefined some colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
 
# Screen information
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

PLAYER_SIZE = 30
PLAYER_PROJECTILE_LIFETIME = 50
PLAYER_PROJECTILE_SPEED = 2

ENEMY_SIZE = 20

PROJECTILE_SIZE = 5

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")
 
 
class Enemy(pygame.sprite.Sprite):
      def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.surf.fill(RED)
        self.rect = pygame.Rect((150, 150), (ENEMY_SIZE, ENEMY_SIZE))
        self.rect.center = (160, 160)
 
      def move(self):
        pass
        #self.rect.move_ip(0,10)
        #if (self.rect.bottom > 600):
        #    self.rect.top = 0
        #    self.rect.center = (random.randint(30, 370), 0)
 
      def draw(self, surface):
        surface.blit(self.surf, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.surf.fill((128,255,40))
        self.rect = pygame.Rect((20, 50), (PLAYER_SIZE, PLAYER_SIZE))
        self.rect.center = (160, 520)
        self.fired_projectile = None
        self.movement_speed = 5
 
    def update(self):
        pressed_keys = pygame.key.get_pressed()
        movement_vector = pygame.Vector2()
        if pressed_keys[K_w]:
            if self.rect.top > 0:
                movement_vector.y += -1
        if pressed_keys[K_s]:
            if self.rect.bottom < SCREEN_HEIGHT:
                movement_vector.y += 1
        if pressed_keys[K_a]:
            if self.rect.left > 0:
                 movement_vector.x += -1
        if pressed_keys[K_d]:
            if self.rect.right < SCREEN_WIDTH:        
                movement_vector.x += 1

        self.rect.move_ip(movement_vector * self.movement_speed)


        if self.fired_projectile is None:
            fire_direction_vector = pygame.Vector2()
            if pressed_keys[K_UP]:
                fire_direction_vector.y += -1
            if pressed_keys[K_DOWN]:
                fire_direction_vector.y += 1
            if pressed_keys[K_LEFT]:
                fire_direction_vector.x += -1
            if pressed_keys[K_RIGHT]:
                fire_direction_vector.x += 1
            if fire_direction_vector.x != 0 or fire_direction_vector.y != 0:
                self.fired_projectile = Projectile(BLUE, PLAYER_PROJECTILE_SPEED, PLAYER_PROJECTILE_LIFETIME, self.rect.center, fire_direction_vector + movement_vector)
 
    def draw(self, surface):
        if self.fired_projectile and not self.fired_projectile.active:
            self.fired_projectile = None
        surface.blit(self.surf, self.rect)     

class Projectile(pygame.sprite.Sprite):
    def __init__(self, color, speed, lifetime, position, direction) -> None:
        self.surf = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.surf.fill(color)
        self.rect = pygame.Rect((20, 50), (PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.rect.center = position
        self.speed = speed
        self.max_lifetime = lifetime
        self.direction = direction
        self.active = True
        self.active_time = 0
    
    def draw(self, surface):
        surface.blit(self.surf, self.rect)

    def update(self):
        if self.active_time < self.max_lifetime:
            self.active_time += 1
            self.rect.move_ip((self.direction[0] * self.speed, self.direction[1] * self.speed))
        else:
            self.active = False


P1 = Player()
E1 = Enemy()
i = 0
while True:     
    for event in pygame.event.get():              
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    P1.update()
    E1.move()
     
    DISPLAYSURF.fill(WHITE)
    P1.draw(DISPLAYSURF)
    E1.draw(DISPLAYSURF)
    if P1.fired_projectile:
        P1.fired_projectile.update()
        P1.fired_projectile.draw(DISPLAYSURF)
         
    pygame.display.update()
    FramePerSec.tick(FPS)