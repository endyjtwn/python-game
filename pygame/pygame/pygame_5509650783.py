# -*- coding: utf-8 -*-
'''
Created on Nov 5, 2557 BE

@author: Endy
'''

import sys,pygame
import numpy as np
import math
import datetime

from pygame.locals import *


try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.arrays import vbo
    from OpenGL.GL import shaders
except:
    print '''
ERROR: PyOpenGL not installed properly.  
        '''
    sys.exit()

ROTATE_TIMER_ID = 30
LEG_TIMER_ID = 31
dirty = 1
 
v0 = (1,1,1)
v1 = (-1,1,1)
v2 = (-1,-1,1)
v3 = (1,-1,1)
v4 = (1,-1,-1)
v5 = (1,1,-1)
v6 = (-1,1,-1)
v7 = (-1,-1,-1)

white = (1,1,1)
red = (1,0,0)
green = (0,1,0)
blue = (0,0,1)
purple = (1,0,1)
green_blue = (0,1,1)
green_red = (1,1,0)
black = (0,0,0)

data =  [v0, white, v1, green_blue, v2, red, v3,  purple,    
         v4, blue, v5, green_red,  v6, green,  v7, black ] 

indices = [0,1,2,3,
           0,3,4,5,
           0,5,6,1,
           1,6,7,2,
           7,4,3,2,
           4,7,6,5
           ] 

vertices = [v0,v1,v2,v3]     

ROTATE = 0
STOP = 1
status = STOP
step = 2
position = 4
angle = 10.0 
  
dArray= np.array(data,dtype=np.float32)   
iArray = np.array(indices,dtype=np.int16)
vArray = np.array(vertices,dtype=np.float32)

sizeOfFloat = 4   
mMatrix = ""
mMatrixLocation = ""
angle = 0
distantx = 0;
distanty = 0;
shader = ''


matrixStack = []
def buildRotateMatrix(x,y,z,angle):
    axis = np.array([x,y,z],dtype = np.float32)  
    #normalize vector represented by x, y, z 
    axis_size = np.linalg.norm(axis)
    axis = axis/axis_size
    
    x = axis [0]
    y = axis [1]
    z = axis [2]

    s = math.sin(math.radians(angle));
    c = math.cos(math.radians(angle));
    oc = 1.0 - c;
    matrix = [[oc * x * x + c, oc * x * y - z * s, oc * z * x + y * s, 0.0],
              [oc * x * y + z * s, oc * y * y + c, oc * y * z - x * s, 0.0],
              [oc * z * x - y * s, oc * y * z + x * s, oc * z * z + c, 0.0],
              [0.0, 0.0, 0.0, 1.0]]
    return np.array(matrix,dtype = np.float32)  

def buildScaleMatrix (x,y,z):
    matrix = [[x,0,0,0],
                  [0,y,0,0],
                  [0,0,z,0],
                  [0,0,0,1]]
    return np.array(matrix,dtype = np.float32)    

def buildIdentityMatrix ():
    matrix = [[1,0,0,0],
                  [0,1,0,0],
                  [0,0,1,0],
                  [0,0,0,1]]
    return np.array(matrix,dtype = np.float32)   

def buildMoveMatrix(x,y,z):
    global mMatrix
    matrix = [[1,0,0,x],
                [0,1,0,y],
                  [0,0,1,z],
                  [0,0,0,1]]
    return np.array(matrix,dtype = np.float32)
    
def init():  
    global shader, mMatrixLocation
    buildMoveMatrix (0,0,0)
    VERTEX_SHADER = shaders.compileShader('''uniform mat4 mMatrix;
                                             void main() { 
                                                gl_Position = gl_ProjectionMatrix * mMatrix* gl_Vertex ; 
                                             }''', GL_VERTEX_SHADER)
    FRAGMENT_SHADER = shaders.compileShader("void main() { gl_FragColor = vec4( 0, 1, 0, 1 ); }", GL_FRAGMENT_SHADER)
    shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
    
    dVboId = glGenBuffers(1)
    iVboId = glGenBuffers(1)
    usage = GL_STATIC_DRAW   
    glBindBuffer(GL_ARRAY_BUFFER,dVboId);
    glBufferData(GL_ARRAY_BUFFER, dArray, usage);
    glVertexPointer(3, GL_FLOAT, 6 * sizeOfFloat, c_void_p(0)  );
    glColorPointer(3, GL_FLOAT, 6 * sizeOfFloat ,c_void_p(4*4)   )
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, iVboId)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, iArray, usage)
    
    vVboId = glGenBuffers(1)
    usage = GL_STATIC_DRAW     
    glBindBuffer(GL_ARRAY_BUFFER,vVboId);
    glBufferData(GL_ARRAY_BUFFER, vArray, usage);
  
    shaders.glUseProgram(shader)
    mMatrixLocation = glGetUniformLocation( shader, 'mMatrix' );
    
def setCurrentMetrix (matrix):
    global currentMatrix

    currentMatrix = matrix
    
def transformCurrentMatrix(moveMatrix):
    global currentMatrix
    currentMatrix = np.dot(currentMatrix,moveMatrix)
                     
def paint():
    glClearColor (1.0, 1.0, 1.0, 1.0)
    glClear (GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)      
     
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity(); 
    
    moveMatrix = buildMoveMatrix (position,0,1)
    xRotateMatrix = buildRotateMatrix(1,1,0,angle)
    yRotateMatrix = buildRotateMatrix(0,1,0,angle)

     
    mMatrix = np.dot(xRotateMatrix, yRotateMatrix)
    mMatrix = np.dot(moveMatrix, mMatrix)
    glUniformMatrix4fv(mMatrixLocation,1,GL_TRUE, mMatrix)
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_COLOR_ARRAY);
    
    glDrawElements(GL_QUADS, 24, GL_UNSIGNED_SHORT, c_void_p(0))
    
    glDisableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_COLOR_ARRAY);
      
    
def resize(w, h):
    glViewport(0, 0, w, h);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(0,6,-10,10);

def animate( ):
    global dirty, angle
    ranNo = np.random.randint(-3, 3)
    distantx = float(ranNo)
    ranNo = np.random.randint(-3, 3)
    distanty = float(ranNo)
    angle = angle - 1
     
    dirty = 1
 
def MouseFunc( x,  y):
    global status,dirty
    if (status == STOP):
        status = ROTATE
        pygame.time.set_timer(ROTATE_TIMER_ID, 100)
#        background_sound.play(-1)
        background_channel.unpause()
    else:
        status = STOP
        pygame.time.set_timer(ROTATE_TIMER_ID, 0)
#        background_sound.stop()
        background_channel.pause()
        wave_sound.play(1)
    dirty = 1
    
    
pygame.init()
screen = pygame.display.set_mode((800, 500), OPENGL|DOUBLEBUF|RESIZABLE|HWSURFACE)
pygame.display.set_caption('Timer Example')
init()
pygame.time.set_timer(ROTATE_TIMER_ID, 80)

timer = pygame.time.Clock()
background_sound = pygame.mixer.Sound("Rain.ogg")
background_channel = background_sound.play(-1)
wave_sound = pygame.mixer.Sound("BigWave.ogg")

while True:

    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit(0)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            x,y = e.pos
            MouseFunc(x,y)    
        elif e.type == VIDEORESIZE:
            resize(e.w,e.h)
        elif e.type == ROTATE_TIMER_ID:
            animate()
        
    if (dirty == 1):
        paint() 
        pygame.display.flip() 
        dirty = 0
    #print "1", datetime.datetime.now()
    timepass = timer.tick(30) 
    #print "2", datetime.datetime.now()
   
