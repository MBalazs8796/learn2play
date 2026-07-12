import pygame, sys
from pygame.locals import *
import random
import math

from itertools import compress
 
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
PLAYER_RATE_OF_FIRE = 50 # bullet per second

ENEMY_SIZE = 20

PROJECTILE_SIZE = 5

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")
 
 
class Enemy(pygame.sprite.Sprite):
      def __init__(self, player, movement_speed):
        super().__init__()
        self.surf = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.surf.fill(RED)
        self.rect = pygame.Rect((150, 150), (ENEMY_SIZE, ENEMY_SIZE))
        self.rect.center = (160, 160)
        self.target_player = player
        self.speed = movement_speed
 
      def move(self):
        def euc_distance_tuples(v1, v2):
            x1, y1 = v1
            x2, y2 = v2
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        def get_shift_towards_thing(thing):
            other_pos = thing.get_position()
            shift_x = other_pos[0] - self.rect.center[0]
            shift_x = math.copysign(min(abs(shift_x), self.speed), shift_x)
            shift_y = other_pos[1] - self.rect.center[1]
            shift_y = math.copysign(min(abs(shift_y), self.speed), shift_y)
            return (shift_x, shift_y)

        if not any([x.active for x in self.target_player.fired_projectiles]):
            # move towards the player
            shift = get_shift_towards_thing(self.target_player)
        else:
            #move away from the closest projectile
            min_distance = 9999999
            index = -1
            for i, incoming_proj in enumerate(self.target_player.fired_projectiles):
                if not incoming_proj.active:
                    continue
                dist = euc_distance_tuples(self.rect.center, incoming_proj.get_position())
                if min_distance > dist:
                    min_distance = dist
                    index = i
            if index == -1:
                raise Exception("Minimum distance calculation errored")
            shift_x, shift_y = get_shift_towards_thing(self.target_player.fired_projectiles[index])
            shift = shift_y, shift_x * -1 # dodge left, cuz vector is rotated 90 degrees

        shift_x, shift_y = shift
        if self.rect.top <= 0:
            shift = shift_x, 1
        elif self.rect.bottom > SCREEN_HEIGHT:
            shift = shift_x, -1
        if self.rect.left < 0:
            shift = 1, shift_y
        elif self.rect.right > SCREEN_WIDTH:
            shift = -1, shift_y
        self.rect.move_ip(shift)
        

 
      def draw(self, surface):
        surface.blit(self.surf, self.rect) 
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.surf.fill((128,255,40))
        self.rect = pygame.Rect((20, 50), (PLAYER_SIZE, PLAYER_SIZE))
        self.rect.center = (160, 520)
        self.movement_speed = 5
        self.fire_delay_remaining = 0
        self.proj_count = max(math.ceil((PLAYER_PROJECTILE_LIFETIME * PLAYER_RATE_OF_FIRE) / 200), 1)
        self.fired_projectiles = []
        for _ in range(self.proj_count):
            p = Projectile(BLUE, PLAYER_PROJECTILE_SPEED, PLAYER_PROJECTILE_LIFETIME, self.rect.center)
            p.active = False
            self.fired_projectiles.append(
                p
               )
 
    def get_position(self):
        return self.rect.center

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


        if self.fire_delay_remaining <= 0:
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
                i = 0
                while  i < self.proj_count and self.fired_projectiles[i].active:
                    i += 1
                if i < self.proj_count:
                    current_proj = self.fired_projectiles[i]
                    current_proj.active = True
                    current_proj.set_direction(fire_direction_vector + movement_vector)
                    current_proj.set_position(self.rect.center)
                    self.fire_delay_remaining =  max(1, math.floor(60 - PLAYER_RATE_OF_FIRE))
        else:
            self.fire_delay_remaining -= 1
 
    def draw(self, surface):
        surface.blit(self.surf, self.rect)     

class Projectile(pygame.sprite.Sprite):
    def __init__(self, color, speed, lifetime, position) -> None:
        self.surf = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.surf.fill(color)
        self.rect = pygame.Rect((20, 50), (PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.rect.center = position
        self.speed = speed
        self.max_lifetime = lifetime
        self.direction = (0,0)
        self.active = True
        self.active_time = 0
    
    def set_direction(self, direction):
        self.direction = direction

    def set_position(self, position):
        self.rect.center = position

    def get_position(self):
        return self.rect.center

    def draw(self, surface):
        surface.blit(self.surf, self.rect)

    def update(self):
        if self.active_time < self.max_lifetime:
            self.active_time += 1
            self.rect.move_ip((self.direction[0] * self.speed, self.direction[1] * self.speed))
        else:
            self.active = False
            self.active_time = 0

P1 = Player()
E1 = Enemy(P1, 3)
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
    for p in  P1.fired_projectiles:
        if p.active:
            p.update()
            p.draw(DISPLAYSURF)
         
    pygame.display.update()
    FramePerSec.tick(FPS)