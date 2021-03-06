import sys
import random
from copy import deepcopy
import math
import pygame
from pygame.locals import *
from pygame import gfxdraw

GRID_OFFSET = 300
GRID_TOP_OFFSET = 0
WINDOW_WIDTH = 800 + 2 * GRID_OFFSET
WINDOW_HEIGHT = 800 + 2 * GRID_TOP_OFFSET

COLOR_RED = (125, 0, 1)
COLOR_GREEN = (5, 125, 6)
COLOR_BLUE = (4, 57, 115)
COLOR_YELLOW = (128, 128, 0)

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

pygame.font.init()
GLOBAL_FONT = pygame.font.SysFont("monospace", 30)


def is_in_square(x, y, x1, y1, x2, y2):
    if x1 <= x <= x2 and y1 <= y <= y2:
        return True
    else:
        return False

def angle_to_circle_coordinate(angle):
    return math.sin(angle), math.cos(angle)

# you would assume that rotating squares is a trivial task...
def rectRotated(surface,
                color,
                pos,
                fill,
                border_radius,
                rotation_angle,
                rotation_offset_center=(0, 0),
                nAntialiasingRatio=1):
    """
    - rotation_angle: in degree
    - rotation_offset_center: moving the center of the rotation:
      (-100,0) will turn the rectangle around a point 100 above
      center of the rectangle,
      if (0,0) the rotation is at the center of the rectangle
    - nAntialiasingRatio: set 1 for no antialising, 2/4/8 for better aliasing
    """
    nRenderRatio = nAntialiasingRatio

    # Improtant comment -pos[0] is only a the x length of the rectangle
    rotation_offset_center = (-pos[2] // 2, 0)
    sw = pos[2]+abs(rotation_offset_center[0])*2
    sh = pos[3]+abs(rotation_offset_center[1])*2

    surfcenterx = sw//2
    surfcentery = sh//2
    s = pygame.Surface((sw * nRenderRatio, sh * nRenderRatio))
    s = s.convert_alpha()
    s.fill((0, 0, 0, 0))

    rw2 = pos[2] // 2  # halfwidth of rectangle
    rh2 = pos[3] // 2

    size_tuple = (
        (surfcenterx-rw2-rotation_offset_center[0]) * nRenderRatio,
        (surfcentery-rh2-rotation_offset_center[1]) * nRenderRatio,
        pos[2] * nRenderRatio,
        pos[3] * nRenderRatio
    )

    pygame.draw.rect(s,
                     color,
                     size_tuple,
                     fill * nRenderRatio,
                     border_radius=border_radius * nRenderRatio)
    s = pygame.transform.rotate(s, rotation_angle)
    if nRenderRatio != 1:
        s = pygame.transform.smoothscale(s,
                                         (s.get_width()//nRenderRatio,
                                          s.get_height()//nRenderRatio))
    incfromrotw = (s.get_width() - sw) // 2
    incfromroth = (s.get_height() - sh) // 2
    surface.blit(s, 
                 (pos[0] - surfcenterx + rotation_offset_center[0] + rw2 - incfromrotw,
                  pos[1] - surfcentery + rotation_offset_center[1] + rh2 - incfromroth))
    


def check_if_in_square(x, y, x1, y1, x2, y2):
    if x1 < x < x2 and y1 < y < y2:
        return True
    return False

class Grid:
    block_size = 10
    offset_x = 0
    offset_y = 0
    size = 0
    blocks = 0

    def __init__(self, offset_x, offset_y, size, blocks):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.size = size

        self.blocks = int(blocks)

        self.block_size = int(size / blocks)
        self.grid_array = []

        for i in range(int(blocks * blocks)):
            self.grid_array.append(False)

        self.top_corner_x = int(self.blocks / 2)
        self.top_corner_y = int(self.blocks / 2)

        for x in range(0, self.blocks):
            for y in range(0, self.blocks):
                if x <=  self.top_corner_x and y <= self.top_corner_y:
                    self.grid_array[x + y * self.blocks] = 1
                elif x <= self.top_corner_x and y > self.top_corner_y:
                    self.grid_array[x + y * self.blocks] = 2
                elif x >= self.top_corner_x and y > self.top_corner_y:
                    self.grid_array[x + y * self.blocks] = 3
                else:
                    self.grid_array[x + y * self.blocks] = 4

    def draw_lines(self):
        global SCREEN
        temp_size = self.block_size * self.blocks
        for x in range(self.blocks):
            pygame.draw.line(SCREEN, 
                             COLOR_BLACK, 
                             (self.offset_x + x * self.block_size, self.offset_y),
                             (self.offset_x + x * self.block_size, self.offset_y + temp_size),
                             1)

        for y in range(self.blocks):
            pygame.draw.line(SCREEN, 
                             COLOR_BLACK, 
                             (self.offset_x, self.offset_y + y * self.block_size),
                             (self.offset_x + temp_size, self.offset_y + y * self.block_size),
                             1)

    def draw_grid(self):
        global SCREEN
        for x in range(self.blocks):
            for y in range(self.blocks):
                # refactor 
                if self.grid_array[x + y * self.blocks] == 1:
                    pygame.draw.rect(SCREEN, 
                                     COLOR_RED, 
                                     (self.offset_x + x * self.block_size, self.offset_y + y * self.block_size, self.block_size, self.block_size))
                elif self.grid_array[x + y * self.blocks] == 2:
                    pygame.draw.rect(SCREEN, 
                                     COLOR_GREEN, 
                                     (self.offset_x + x * self.block_size, self.offset_y + y * self.block_size, self.block_size, self.block_size))
                elif self.grid_array[x + y * self.blocks] == 3:
                    pygame.draw.rect(SCREEN, 
                                     COLOR_BLUE, 
                                     (self.offset_x + x * self.block_size, self.offset_y + y * self.block_size, self.block_size, self.block_size))
                elif self.grid_array[x + y * self.blocks] == 4:
                    pygame.draw.rect(SCREEN, 
                                     COLOR_YELLOW, 
                                     (self.offset_x + x * self.block_size, self.offset_y + y * self.block_size, self.block_size, self.block_size))

    def real_position_to_grid_position(self, x, y):
        x = int((x - self.offset_x) / self.block_size)
        y = int((y - self.offset_y) / self.block_size)
        return x, y

    def is_in_top_corner_left(self, x, y):
        return is_in_square(x,
                            y,
                            self.offset_x,
                            self.offset_y,
                            self.offset_x + (self.blocks*self.block_size)//2,
                            self.offset_y + (self.blocks*self.block_size)//2)

    def is_in_bottom_corner_left(self, x,y ):
        return is_in_square(x,
                            y,
                            self.offset_x,
                            self.offset_y,
                            self.offset_x + (self.blocks*self.block_size)//2,
                            self.offset_y + (self.blocks*self.block_size)//2)              

    def is_in_top_corner_right(self, x, y):
        return is_in_square(x,
                            y,
                            self.offset_x+(self.blocks*self.block_size)//2,
                            self.offset_y,
                            self.offset_x + (self.blocks+self.block_size),
                            self.offset_y + (self.blocks+self.block_size)//2)

    def is_in_bottom_corner_right(self, x, y):
        return is_in_square(x,
                            y,
                            self.offset_x + (self.blocks*self.block_size)//2,
                            self.offset_y + (self.blocks*self.block_size)//2,
                            self.offset_x + (self.blocks*self.block_size),
                            self.offset_y + (self.blocks*self.block_size)
                            )

    def get(self, x, y):
        if x < 0 or x >= self.blocks or y < 0 or y >= self.blocks:
            return False
        return self.grid_array[x + y * self.blocks]

    def update_grid(self, x, y, value):
        # Boundary Check, fail early
        if x > self.blocks or y > self.blocks:
            return
        self.grid_array[x + y * self.blocks] = value

    top_left_gun_alive = True
    def draw_top_left_gun(self, rot):
        if self.top_left_gun_alive:
            pygame.draw.circle(SCREEN,
                            (255,4,4),
                            (self.offset_x + self.block_size,
                            self.offset_y + self.block_size),
                            self.block_size)
            rectRotated(SCREEN, 
                        (255, 0, 0), 
                        (self.offset_x + (self.block_size ),
                        self.offset_y + (self.block_size // 2), 
                        self.block_size*3, 
                        self.block_size),
                        0,
                        0, 
                        rot)

    top_right_gun_alive = True
    def draw_top_right_gun(self, rot): 
        if self.top_right_gun_alive:
            pygame.draw.circle(SCREEN,
                            (255,255,4),
                            (self.offset_x + (self.blocks-1) * self.block_size,
                            self.offset_y +  self.block_size),
                            self.block_size)
            rectRotated(SCREEN, 
                        (255, 255, 4), 
                        (self.offset_x + (self.block_size)*(self.blocks-1), 
                        self.offset_y + (self.block_size // 2), 
                        self.block_size*3, self.block_size),
                        0,
                        0, 
                        270+rot)

    bottom_left_gun_alive = True 
    def draw_bottom_left_gun(self, rot):
        if self.bottom_left_gun_alive:
            pygame.draw.circle(SCREEN,
                            (4,255,4),
                            (self.offset_x +  self.block_size,
                            self.offset_y +  (self.blocks-1) * self.block_size),
                            self.block_size)
            rectRotated(SCREEN, 
                        (4, 255, 4), 
                        (self.offset_x + (self.block_size), 
                        self.offset_y + (self.block_size)*(self.blocks-1)-(self.block_size//2),
                        self.block_size*3, self.block_size),
                        0,
                        0, 
                        90+rot)

    bottom_right_gun_alive = True
    def draw_bottom_right_gun(self, rot):
        if self.bottom_right_gun_alive:
            rectRotated(SCREEN, 
                        (4, 4, 255), 
                        (self.offset_x + (self.block_size)*(self.blocks-1), 
                        self.offset_y + (self.block_size)*(self.blocks-1)-(self.block_size//2),
                        self.block_size*3, self.block_size),
                        0,
                        0, 
                        180+rot)
            pygame.draw.circle(SCREEN,
                            (4,4,255),
                            (self.offset_x + (self.blocks-1) * self.block_size,
                            self.offset_y + (self.blocks-1) * self.block_size),
                            self.block_size)

    def draw(self, rot):
        self.draw_grid()
        self.draw_lines()
        self.draw_top_right_gun(rot)
        self.draw_top_left_gun(rot)
        self.draw_bottom_right_gun(rot)
        self.draw_bottom_left_gun(rot)
        

class MiniGameObstacle:
    def __init__(self, x, y, start_y, end_y, radius=12):
        self.initial_x = x
        self.initial_y = y
        self.radius = radius
        self.color = (129, 129, 129)
        self.x = x
        self.y = y
        self.start_y = start_y
        self.end_y = end_y
        self.move_x = 0
        self.move_y = -0.4

    def draw(self):
        gfxdraw.aacircle(SCREEN,  int(self.x), int(self.y), self.radius, self.color)
        gfxdraw.filled_circle(SCREEN,  int(self.x), int(self.y), self.radius, self.color)

    def update(self):
        self.x += self.move_x
        self.y += self.move_y
        # some india jones action
        #if self.x - self.initial_x == 0:
        #    self.move_x = 0.5
        #elif self.x - self.initial_x == 5:
        #    self.move_x = -0.5
        #if self.y - self.initial_y == 0:
        #    self.move_y = 0.5
        #elif self.y - self.initial_y == 5:
        #    self.move_y = -0.5
        # constant upward motion
        if self.y < self.start_y:
            self.y = self.end_y 
        


class MiniGameMarble: 
    def __init__(self, start_x, start_y, end_x, end_y, color=COLOR_RED):
        print("Marble initiated: {}", start_x)
        self.color = color

        self.x = start_x
        self.y = start_y

        # this introduces velocity into the system
        self.move_x = 0
        self.move_y = 0

        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y - 15
        self.radius = 12
        self.lastscore = 0
        self.alive = True
    
    def gravity(self):
        # introduce acceleration
        self.move_y += 0.15
        if self.y > self.end_y and self.move_y > 0:
            if self.alive:  
                self.move_y = 0
                #self.move_x = 0.001
                self.y = self.start_y
                #self.y = self.border_y + self.height
                thirds = self.start_x + int((self.end_x - self.start_x)/3)
                if self.x < thirds:
                    print("self.x{} self.start_x{} self.end_x{} thirds: {} RELEASE".format(self.x, self.start_x, self.end_x, thirds))
                    self.lastscore = 1
                elif self.x > thirds:
                    print("self.x{} self.start_x{} self.end_x{} thirds: {} MULTIPLY".format(self.x, self.start_x, self.end_x, thirds))
                    self.lastscore = 2
                self.x = random.randrange(self.start_x, self.end_x)
            else:
                self.move_y = 0

        

        # Left border bounce off
        if self.x - self.radius < self.start_x and self.move_x < 0:
            self.move_x = -self.move_x #+ 1
            self.x = self.start_x + self.radius
        # Right border bounce off
        if self.x + self.radius > self.end_x and self.move_x > 0:
            self.move_x = -self.move_x #+ 1
            self.x = self.end_x - self.radius
        # top border bounce off 
        #if self.y < self.start_y and self.move_y > 0:
        #    self.move_y = 1
        #    self.y = self.start_y


    def draw(self):
        global SCREEN
#        pygame.draw.circle(SCREEN, self.color, (self.x, self.y), self.radius, width=0)
        gfxdraw.aacircle(SCREEN,  int(self.x), int(self.y), self.radius, self.color)
        gfxdraw.filled_circle(SCREEN,  int(self.x), int(self.y), self.radius, self.color)


    def update(self):
        if self.alive == False:
            self.color = (128, 128, 128)
        self.x += self.move_x
        self.y += self.move_y
        self.gravity()

        

class MiniGame:
    collect_store = 1
    def create_obstacles(self):
        """
        Initialization Function for creating the obstacles for the first time 
        """
        self.obstacles = []
        for k in range(0, 6):
            for i in range(0, 5):
                additional_factor = 0
                if k % 2 == 0:
                    additional_factor = 30

                # Someone told me this needs refactoring...
                new_obstacle = MiniGameObstacle(x=self.start_x + k * 55, 
                                                y=self.start_y + 30 + i * 90 + additional_factor,
                                                start_y=self.start_y,
                                                end_y=self.end_y,
                                                radius=14)
                self.obstacles.append(new_obstacle)


    def __init__(self, start_x, start_y, end_x, end_y, team=1):
        self.start_x = int(start_x)
        self.start_y = int(start_y)
        self.end_x = int(end_x)
        self.end_y = int(end_y)
        self.create_obstacles()
        self.marbles = []
        self.text = ""
        self.additional_text = ""
        self.score = 1
        self.collect_score = 4
        self.team = team
        self.alive = True
        
        if self.team == 1:
            self.marble_color = (255, 0, 0)
        elif self.team == 2:
            self.marble_color = (0, 255, 0)
        elif self.team == 3:
            self.marble_color = (128, 128, 255)
        elif self.team == 4:
            self.marble_color = (255, 255, 40)
        else:
            self.marble_color = (255, 255, 255)
        # Add inital marble
        # this is somewhat criminal
        first_marble = MiniGameMarble(start_x,
                                      start_y,
                                      end_x,
                                      end_y,
                                      color=self.marble_color)
        second_marble = MiniGameMarble(start_x,
                                      start_y,
                                      end_x,
                                      end_y,
                                      color=self.marble_color)
        fourth_marble = MiniGameMarble(start_x,
                                      start_y,
                                      end_x,
                                      end_y,
                                      color=self.marble_color)
        first_marble.move_x += 0.01 # Lets get the party STARTED
        second_marble.move_x -= 0.01
        fourth_marble.move_x += 0.1
        self.marbles.append(first_marble)
        self.marbles.append(second_marble)
        self.marbles.append(fourth_marble)
        #self.marbles.append(second_marble)

    def update(self):
        for obstacle in self.obstacles:
            obstacle.update()
        # TODO event driven architecture
        for marble in self.marbles:
            # collect results
            if marble.lastscore == 1:
                #self.additional_text = "RELEASE"
                if self.score == 0:
                    self.score = 1
                self.collect_score = deepcopy(self.score) # im getting scared...
                print("setting collect_score to {}".format(self.collect_score))
                self.score = 1
            elif marble.lastscore == 2:
                #self.additional_text = "MULTIPLY"
                self.score *= 2

            marble.lastscore = 0
            # The physics are broken. There is some for of Marble - Marble
            # attraction force that I cannot possibly fathom
            # Marble - Obstacle Collision - here is where the fun begins
            for obstacle in self.obstacles:
                max_dist = (obstacle.x - marble.x) ** 2 + (obstacle.y - marble.y) ** 2
                if max_dist < (obstacle.radius + marble.radius) ** 2:
                    obstacle.color = COLOR_RED
                    angle = math.atan2(marble.y - obstacle.y, marble.x - obstacle.x)
                    cosa = math.cos(angle)
                    sina = math.sin(angle)
                    # Square root is a costly operation
                    # maybe seek to improve in the future
                    # the obstacle.radius offset avoids a strange bug 
                    # which occurs when a marble colludes too much with 
                    # a obstacle
                    overlap = marble.radius + (obstacle.radius + 2) - math.sqrt(max_dist)

                    overlapX = overlap * cosa
                    overlapY = overlap * sina

                    marble.x = marble.x + overlapX
                    marble.y = marble.y + overlapY

                    px1 = cosa * marble.move_x - sina * marble.move_y
                    py1 = sina * marble.move_x + cosa * marble.move_y

                    vXNew = cosa * px1 - sina * py1
                    vYNew = sina * px1 + cosa * py1
                    # now set new velocities with loss factor for friction
                    marble.move_x = vXNew * 0.9
                    marble.move_y = vYNew * 0.9
                else:
                    obstacle.color = (129, 129, 129)
            # Marble - Marble Collision
            for marble in self.marbles:
                for enemy_marble in [i for i in self.marbles if i != marble]:
                    max_dist = (marble.x - enemy_marble.x) ** 2 + (marble.y - enemy_marble.y) ** 2
                    if max_dist < (marble.radius + enemy_marble.radius) ** 2:
                        angle = math.atan2(marble.y - enemy_marble.y, marble.x - enemy_marble.x)
                        cosa = math.cos(angle)
                        sina = math.sin(angle)
                        overlap = marble.radius + (enemy_marble.radius + 2) - math.sqrt(max_dist)

                        overlapX = overlap * cosa
                        overlapY = overlap * sina

                        marble.x = marble.x + overlapX
                        marble.y = marble.y + overlapY

                        px1 = cosa * marble.move_x - sina * marble.move_y
                        py1 = sina * marble.move_x + cosa * marble.move_y

                        px2 = cosa * enemy_marble.move_x - sina * enemy_marble.move_y
                        py2 = sina * enemy_marble.move_x + cosa * enemy_marble.move_y

                        vXNew = (px1 + px2) / 2
                        vYNew = (py1 + py2) / 2

                        marble.move_x = vXNew * 0.9
                        marble.move_y = vYNew * 0.9
                        enemy_marble.move_x = vXNew * 0.9
                        enemy_marble.move_y = vYNew * 0.9
            for marble in self.marbles:
                if self.alive == False:
                    marble.alive = False
                marble.update()

    def draw(self):
        global SCREEN

        # draw borders and landing areas
        pygame.draw.rect(SCREEN, 
                        COLOR_BLACK, 
                        (self.start_x, self.start_y, self.end_x, self.end_y) 
                        )
        pygame.draw.rect(SCREEN, 
                        (127,255,0),
                        (self.start_x, self.end_y, 
                        100,
                        20))
        pygame.draw.rect(SCREEN,
                        (40,40,125),
                        (self.start_x+100, self.end_y,
                        200,
                        20))

        for obstacle in self.obstacles:
            obstacle.draw()
        for marble in self.marbles:
            marble.draw()
        self.text = "Score: {} {}".format(self.score, self.additional_text)
        textsurface = GLOBAL_FONT.render(self.text, False, (128, 128, 128))
        SCREEN.blit(textsurface, (self.start_x + 10, self.start_y + 30))



def draw_circle_alpha(color, center, radius, alpha):
    global SCREEN
    target_rect = pygame.Rect(center,(0,0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    #shape_surf.fill((255,255,255,255), special_flags=pygame.BLEND_RGBA_ADD)
    shape_surf.set_alpha(alpha)
    #pygame.draw.circle(SCREEN, color, center, radius)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    SCREEN.blit(shape_surf, target_rect)

class Bullet:
    def __init__(self, x, y, angle, speed, team=1):
        self.x = x
        self.y = y
        self.team = team
        self.angle = math.radians(angle)
        self.speed_x = speed
        self.speed_y = speed
        self.radius = 8
        self.last_x = []
        self.last_y = []
        if self.team == 1:
            self.color = (255, 0, 0)
        elif self.team == 2:
            self.color = (0, 255, 0)
        elif self.team == 3:
            self.color = (128, 128, 255)
        elif self.team == 4:
            self.color = (255, 255, 40)
        else:
            self.color = (255, 255, 255)

    def draw(self):
        # Shadowing effect
        global SCREEN
        # I hate this loop with every fiber of my being 
        i = 0
        for x, y in zip(self.last_x, self.last_y):
            draw_circle_alpha(self.color, (int(x), int(y)), 6, 30 + i * 10)
            i += 1


#        pygame.draw.circle(SCREEN, self.color, (int(self.x), int(self.y)), self.radius)        
#        pygame.draw.circle(SCREEN, (0,0,0), (int(self.x), int(self.y)), self.radius, width=1)       
        gfxdraw.aacircle(SCREEN,  int(self.x), int(self.y), self.radius, self.color)
        gfxdraw.filled_circle(SCREEN,  int(self.x), int(self.y), self.radius, self.color)

    def update(self):
        self.last_x += [self.x]
        self.last_y += [self.y]
        if len(self.last_x) > 8:
            self.last_x.pop(0) 
            self.last_y.pop(0)
        self.x += math.cos(self.angle) * self.speed_x
        self.y += math.sin(self.angle) * self.speed_y


def main():
    global SCREEN, CLOCK
    pygame.init()
    pygame.font.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()

    bullets_to_release = [0,0,0,0,0]
    myGrid = Grid(GRID_OFFSET, GRID_TOP_OFFSET, (WINDOW_WIDTH-2*GRID_OFFSET), 40)
    rot_speed = 2
    rot = 270
    inverse_rot = 360
    inverse_rot_speed = -2
    active_bullets = []
    minigames = []
    myMinigame = MiniGame(0,
                          0,
                          GRID_OFFSET,
                          (WINDOW_HEIGHT-10)//2,
                          team=1)
    minigames.append(myMinigame)
    secondMiniGame = MiniGame(0, (WINDOW_HEIGHT-10)//2+20,GRID_OFFSET, (WINDOW_HEIGHT-20), team=2)
    minigames.append(secondMiniGame)
    thirdMiniGame = MiniGame(WINDOW_WIDTH-GRID_OFFSET,
                             0,
                             WINDOW_WIDTH,
                             (WINDOW_HEIGHT-10)//2,
                             team=4)
    minigames.append(thirdMiniGame)
    fourthMiniGame = MiniGame(WINDOW_WIDTH-GRID_OFFSET,
                              (WINDOW_HEIGHT-12)//2+20,
                              WINDOW_WIDTH,
                              WINDOW_HEIGHT-22,
                              team=3)
    minigames.append(fourthMiniGame)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_w:
                    if rot > 345:
                        my_rot = 345
                    elif rot < 295:
                        my_rot = 295
                    else:
                        my_rot = rot
                    circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot+90))
                    current_x = circle_coordinates[0] * myGrid.block_size * 3.5
                    current_y = circle_coordinates[1] * myGrid.block_size * 3.5
                    current_x += myGrid.offset_x + myGrid.block_size
                    current_y += myGrid.offset_y + myGrid.block_size
                    active_bullets.append(Bullet(current_x,
                                                current_y,
                                                90+inverse_rot, 
                                                8,
                                                team=1))
                if event.key == K_s: 
                    if rot > 345:
                        my_rot = 345
                    elif rot < 295:
                        my_rot = 295
                    else:
                        my_rot = rot
                    circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot-180))
                    current_x = circle_coordinates[0] * myGrid.block_size * 3.5
                    current_y = circle_coordinates[1] * myGrid.block_size * 3.5
                    current_x += myGrid.offset_x + myGrid.block_size
                    current_y += myGrid.offset_y + myGrid.block_size*(myGrid.blocks-1)
                    print("left to release {}".format(bullets_to_release[1]))
                    print("rot {}".format(rot))
                    print("current_x {}".format(current_x))
                    print("current_y {}".format(current_y))
                    active_bullets.append(Bullet(current_x,
                                                current_y, 
                                                inverse_rot, 
                                                8,
                                                team=2))
                if event.key == K_a:
                    my_rot = rot
                    circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot-90))
                    current_x = circle_coordinates[0] * myGrid.block_size * 3.5
                    current_y = circle_coordinates[1] * myGrid.block_size * 3.5
                    current_x += myGrid.offset_x + myGrid.block_size*(myGrid.blocks-1)
                    current_y += myGrid.offset_y + myGrid.block_size*(myGrid.blocks-1)
                    active_bullets.append(Bullet(current_x,
                                                current_y, 
                                                inverse_rot-90, 
                                                8,
                                                team=3))
                if event.key == K_d:
                    my_rot = rot
                    circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot))
                    current_x = circle_coordinates[0] * myGrid.block_size * 3.5
                    current_y = circle_coordinates[1] * myGrid.block_size * 3.5
                    current_x += myGrid.offset_x + myGrid.block_size*(myGrid.blocks-1)
                    current_y += myGrid.offset_y + myGrid.block_size
                    active_bullets.append(Bullet(current_x,
                                                current_y, 
                                                inverse_rot+180, 
                                                8,
                                                team=4))

        total_rot_speed = 2
        rot = (rot + rot_speed)  % 361
        if rot == 360:
            rot_speed = -total_rot_speed
        elif rot == 270:
            rot_speed = total_rot_speed
        inverse_rot = (inverse_rot + inverse_rot_speed)  % 361
        if inverse_rot == 360:
            inverse_rot_speed = -total_rot_speed
        elif inverse_rot == 270:
            inverse_rot_speed = total_rot_speed
        #point = pygame.mouse.get_pos()
        #for i in [0,1,-1]:
        #    for y in [0,1,-1]:
        #        real_position = myGrid.real_position_to_grid_position(point[0]+i, point[1]+y)
        #        myGrid.update_grid(real_position[0]+i, real_position[1]+y, 1)

        # fill the screen

        # draw game borders

        randomness_factor = 4

        SCREEN.fill(COLOR_WHITE)


        pygame.draw.rect(SCREEN, (90, 90, 90), (WINDOW_WIDTH - GRID_OFFSET, 0, GRID_OFFSET, WINDOW_HEIGHT))
        pygame.draw.rect(SCREEN, (90, 90, 90), (0, 0, WINDOW_WIDTH, GRID_TOP_OFFSET))
        pygame.draw.rect(SCREEN, (90, 90, 90), (0, 0, GRID_OFFSET, WINDOW_HEIGHT))
        pygame.draw.rect(SCREEN, (90, 90, 90), (0, WINDOW_HEIGHT - GRID_TOP_OFFSET, WINDOW_WIDTH, GRID_TOP_OFFSET))
        # Draw Marble mini games
        # BURGGGH

        for i, minigame in enumerate(minigames):
            if minigame.collect_score != 0:
                temp_store = minigame.collect_score
                bullets_to_release[minigame.team] += minigame.collect_score
                minigame.collect_score = 0
                # I cannot count all the antipatterns which are probably present
                # in the code below

        if bullets_to_release[1] != 0:
            bullets_to_release[1] -= 1
            my_rot = rot
            circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot-270))
            current_x = circle_coordinates[0] * myGrid.block_size * 3.5
            current_y = circle_coordinates[1] * myGrid.block_size * 3.5
            current_x += myGrid.offset_x + myGrid.block_size
            current_y += myGrid.offset_y + myGrid.block_size
            active_bullets.append(Bullet(current_x,
                                        current_y,
                                        inverse_rot+90, 
                                        8,
                                        team=1))
        if bullets_to_release[2] != 0:
            bullets_to_release[2] -= 1
            my_rot = rot
            circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot-180))
            current_x = circle_coordinates[0] * myGrid.block_size * 3.5
            current_y = circle_coordinates[1] * myGrid.block_size * 3.5
            current_x += myGrid.offset_x + myGrid.block_size
            current_y += myGrid.offset_y + myGrid.block_size*(myGrid.blocks-1)
            active_bullets.append(Bullet(current_x,
                                        current_y, 
                                        inverse_rot, 
                                        8,
                                        team=2))
        if bullets_to_release[3] != 0:
            bullets_to_release[3] -= 1
            my_rot = rot
            circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot-90))
            current_x = circle_coordinates[0] * myGrid.block_size * 3.5
            current_y = circle_coordinates[1] * myGrid.block_size * 3.5
            current_x += myGrid.offset_x + myGrid.block_size*(myGrid.blocks-1)
            current_y += myGrid.offset_y + myGrid.block_size*(myGrid.blocks-1)
            active_bullets.append(Bullet(current_x,
                                        current_y, 
                                        inverse_rot-90, 
                                        8,
                                        team=3))
        if bullets_to_release[4] != 0:
            bullets_to_release[4] -= 1
            my_rot = rot
            circle_coordinates = angle_to_circle_coordinate(math.radians(my_rot))
            current_x = circle_coordinates[0] * myGrid.block_size * 3.5
            current_y = circle_coordinates[1] * myGrid.block_size * 3.5
            current_x += myGrid.offset_x + myGrid.block_size*(myGrid.blocks-1)
            current_y += myGrid.offset_y + myGrid.block_size
            active_bullets.append(Bullet(current_x,
                                        current_y, 
                                        inverse_rot+180, 
                                        8,
                                        team=4))


        for minigame in minigames:
            print("{}", minigame.team)
            team = minigame.team
            current_x = 0
            current_y = 0
            # we must select our offset in to target the left most 
            if team == 1:
                current_x = 1
                current_y = 1
            elif team == 2:
                current_x = 1
                current_y = (myGrid.blocks - 2) 
            elif team == 3:
                current_x = (myGrid.blocks - 2)
                current_y = (myGrid.blocks - 2)
            elif team == 4: 
                current_x = (myGrid.blocks - 1)
                current_y = 1

            toggle = False
            for i in [0]:
                for j in [0]:
                    if myGrid.get(current_x + i, current_y + j) != minigame.team:
                        # We need a event based architecture for god's sake
                        if team == 1:
                            myGrid.top_left_gun_alive = False
                        elif team == 2:
                            myGrid.bottom_left_gun_alive = False
                        elif team == 3:
                            myGrid.bottom_right_gun_alive = False
                        elif team == 4: 
                            myGrid.top_right_gun_alive = False
                        print("killing team {}".format(minigame.team))
                        toggle = True
                        minigame.alive = False
                        break
            minigame.update()
            minigame.draw()

        # wall bounce bullets
        for bullet in active_bullets:
            if bullet.y - (bullet.radius // 2) < myGrid.offset_y:
                bullet.speed_y = -bullet.speed_y
            if bullet.y + (bullet.radius // 2) > myGrid.offset_y + (myGrid.block_size * myGrid.blocks):
                bullet.speed_y = -bullet.speed_y
            if bullet.x - (bullet.radius // 2) < myGrid.offset_x:
                bullet.speed_x = -bullet.speed_x
            if bullet.x + (bullet.radius // 2) > myGrid.offset_x + (myGrid.block_size * myGrid.blocks):
                bullet.speed_x = -bullet.speed_x

        for bullet in active_bullets:
            real_position = myGrid.real_position_to_grid_position(bullet.x, bullet.y)
            # do entire grid search, costly, but what else am I gonna do?
            hit = False
            for i in [0, 1, -1]:
                for y in [0, 1, -1]:
                    try: 
                        if myGrid.get(real_position[0]+i, real_position[1]+y) != bullet.team and myGrid.get(real_position[0]+i, real_position[1]+y) != False:
                            #print("updating {} {}".format(real_position[0]+i, real_position[1]+y))
                            myGrid.update_grid(real_position[0]+i, real_position[1]+y, bullet.team)           # todo: bounce off effect...
                            hit = True
                            break
                    except:
                        pass
                if hit:
                    break
#active_bullets.remove(bullet)
            if not hit:
                bullet.update()
            else:
                active_bullets.remove(bullet)
            

        myGrid.draw(rot)
        for bullet in active_bullets:
            bullet.draw()

        # artifically limit rotation angles
        #pygame.draw.circle(SCREEN,
        #                   (255,255,255),
        #                   (current_x,
        #                   current_y),
        #                   2)

        pygame.display.update()
        CLOCK.tick(30)


if __name__ == '__main__':
    main()
