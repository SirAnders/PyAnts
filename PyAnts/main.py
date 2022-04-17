import sys

import numpy.linalg
import pygame
import numpy as np
import collections as cl
from pygame.locals import *

width, height = 960, 960
WHITE= (255, 255, 255)
RED=(255, 0, 0)
LIGHT_BLUE=(22, 201, 220)
DARK_BLUE = (0, 119, 255)
BACKGROUND = (74, 180, 237)
YELLOW = (237, 210, 74)
T = 2 #locations to store for ant trace
N = 100  #number of ants
stored_locations = [cl.deque(maxlen=T) for k in range(N)]
#color_1 = (100+155*np.random.rand(),100+155*np.random.rand(),100+155*np.random.rand())

class Environment:

    def __init__(self,grid_div,width,height,food_nr):
        #grid_divs is the total number of squares in the grid
        self.screen_width = width
        self.food_nr = food_nr
        self.screen_height = height
        self.screen_ratio = width/height
        self.x = np.linspace(0,width,grid_div)
        self.y = np.linspace(0,height,grid_div)
        self.grid_l = self.x[1] #grid square size length

    def locationToGrid(x1, y1, location):
        temp = [0, 0]
        for i in range(len(x1)):
            for j in range(i, len(x1)):
                if (j != i):
                    if (location[0] < j and location[0] >= i):
                        temp[0] = i
        for i in range(len(y1)):
            for j in range(i, len(y1)):
                if (j != i):
                    if (location[1] < j and location[1] >= i):
                        temp[1] = i
        return (temp[0], temp[1])

    def rngSpawnFood(self):
        x1 = self.x
        y1 = self.y

        ok_flag = False
        count = 0
        self.food = np.zeros([2,self.food_nr])
        while(not ok_flag):
            x_f =self.screen_width*np.random.rand(1,self.food_nr)
            y_f =self.screen_height*np.random.rand(1,self.food_nr)
            self.food = np.array([x_f,y_f])
            for i in self.food[0]:
                count = count + np.count_nonzero(self.food[0] == i)
            for i in self.food[1]:
                count = count + np.count_nonzero(self.food[1] == i)
            if(count == 2*len(self.food[0])): ok_flag = True



    def drawFood(self,surf):
        for i in range(self.food_nr):
            temp = self.food[:,i]
            pygame.draw.rect(surf,(0,150,0),Rect(temp[0], temp[1],self.grid_l,self.grid_l))

        return surf



    def DrawGrid(self,width,surf):

        for i in range(len(self.x)):
            pygame.draw.line(surf, WHITE,(self.x[i],0),(self.x[i],self.screen_height),width)
        for i in range(len(self.y)):
            pygame.draw.line(surf, WHITE,(0,self.y[i]),(self.screen_width,self.y[i]),width)
        return surf

class Ant:

    def __init__(self,size=3,color = WHITE,location=(width/2,height/2),speed=2,angle=0,max_angle=np.pi/4):
        self.size = size
        self.color = color
        self.location = location #center
        self.speed = speed #pixels per frame
        self.angle = angle #angle from vertical
        self.max_angle = max_angle #radians, half width of the angle update cone
        self.cone_angle = angle


    def reset(self):
        self.__init__()

    def randomWalk(self,flag,forced=False):

        def redirect_collision(flag, location, speed, angle):
            if (flag == 1):
                angle = -np.pi * np.random.rand()
                location = (location[0] - speed * np.sin(angle), location[1] - speed * np.cos(angle))
                return (location, angle)
            if (flag == 2):
                angle = np.pi * np.random.rand()
                location = (location[0] - speed * np.sin(angle), location[1] - speed * np.cos(angle))
                return (location, angle)
            if (flag == 3):
                angle = np.pi * (0.5 + np.random.rand())
                location = (location[0] - speed * np.sin(angle), location[1] - speed * np.cos(angle))
                return (location, angle)
            if (flag == 4):
                angle = np.pi / 2 - np.pi * np.random.rand()
                location = (location[0] - speed * np.sin(angle), location[1] - speed * np.cos(angle))
                return (location, angle)
            return (location, angle)

        if(flag != 0):
            (self.location, self.angle) = redirect_collision(flag, self.location,self.speed+(2*np.random.rand()-1),self.angle)
        else:
            if(forced):
                self.angle = self.cone_angle + (self.max_angle * np.random.rand() - self.max_angle / 2)
            else:
                self.angle = self.angle + (self.max_angle * np.random.rand() - self.max_angle / 2)

            self.location = (self.location[0] - self.speed * np.sin(self.angle),self.location[1] - self.speed * np.cos(self.angle))

def collisionDetector(width,height,location,size):
    if(location[0]<= size):
        #left wall
        return 1
    if (location[0]>= width-size):
        #right wall
        return 2
    if (location[1] <= size):
        #up wall
        return 3
    if (location[1] >= height - size):
        #bottom wall
        return 4

    return 0

pygame.init()
pygame.display.set_caption('Ants Sim')

fps = 60
fpsClock = pygame.time.Clock()
loop_count = 1
flag = 0
screen = pygame.display.set_mode((width, height))
surf1 = pygame.Surface((width, height))
start_surf = pygame.image.load('start.png')
ant_list = [Ant(size=3,speed=7,angle = 2*np.pi*np.random.rand(),max_angle=np.pi/4)  for i in range(N)]
env = Environment(32,width,height,10)
env.rngSpawnFood()
start_flag = 0
pause_flag = False
grid_flag = False
click_flag = False
# Game loop.
while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                start_flag = 1
        if ((event.type == pygame.KEYDOWN) and (start_flag==1)):
            if event.key == pygame.K_p:
                pause_flag = not pause_flag
        if ((event.type == pygame.KEYDOWN) and (start_flag==1)):
            if event.key == pygame.K_g:
                grid_flag = not grid_flag
        if ((event.type == pygame.MOUSEBUTTONDOWN) and (start_flag==1)):
            if event.button == 1:
                click_flag = not click_flag


    if(start_flag == 0):

        surf1.fill((0,0,0))
        surf1.blit(start_surf, (width/2-450/2, height/2-240/2))

    else:
        if(not pause_flag):
            # Update.
            surf1.fill((0, 0, 0))
            x, y = pygame.mouse.get_pos()
            for i in range(N):

                stored_locations[i].append(ant_list[i].location)
                if (loop_count > 1):
                    for k in range(len(stored_locations[i])):
                        if (k != len(stored_locations[i]) - 1):
                            pygame.draw.line(surf1, WHITE, stored_locations[i][k], stored_locations[i][k + 1], width=3)

                pygame.draw.circle(surf1, ant_list[i].color, ant_list[i].location, ant_list[i].size)
                flag = collisionDetector(width, height, ant_list[i].location, ant_list[i].size)

                if(click_flag):
                    r =np.array([x,y]) - np.array([ant_list[i].location[0],ant_list[i].location[1]])
                    r = -r/np.linalg.norm(r)
                    if (r[0] < 0 and r[1] < 0): ant_list[i].cone_angle = np.arctan(r[0]/r[1]) + np.pi
                    if (r[0] > 0 and r[1] > 0): ant_list[i].cone_angle = -np.arctan(r[1]/r[0]) + np.pi/2
                    if (r[0] < 0 and r[1] > 0): ant_list[i].cone_angle = np.arctan(-r[1]/r[0]) + np.pi/2 + np.pi
                    if (r[0] > 0 and r[1] < 0): ant_list[i].cone_angle = -np.arctan(-r[0]/r[1]) + np.pi

                    ant_list[i].randomWalk(flag, forced=True)
                else:
                    ant_list[i].color = WHITE
                    ant_list[i].randomWalk(flag,forced=False)

                # ant_list[i].location = (ant_list[i].location[0]+ant_list[i].speed*np.random.rand()-ant_list[i].speed/2,ant_list[i].location[1]+ant_list[i].speed*np.random.rand()-ant_list[i].speed/2)

    loop_count = loop_count+1
  #  surf1 = env.drawFood(surf1)
    if(grid_flag): surf1 = env.DrawGrid(1,surf1)

    # Draw.
    screen.blit(surf1, (0,0))
    pygame.display.flip()
    fpsClock.tick(fps)