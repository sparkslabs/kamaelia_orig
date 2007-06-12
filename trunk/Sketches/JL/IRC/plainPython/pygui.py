#simple scrolling textbox using Pygame

import pygame
import time

def update(text):
    while len(text) > linelen:
        cutoff = text.rfind(' ', 0, linelen)
        updateLine(text[0:cutoff])
        text = text[cutoff + 1:]
    updateLine(text)
        
def updateLine(line):            
    lineSurf = font.render(line, True, text_color)    
    screen.fill(background_color)
    screen.blit(scratch, scrollingRect, keepRect)
    screen.blit(lineSurf, writeRect)
    scratch.fill(background_color)
    scratch.blit(screen, screen.get_rect())
    pygame.display.update()

## initialize the pygame stuff. The output window.
screen_width=300
screen_height=200
text_height=14
background_color = (255,255,255)
text_color=(0,0,0)
        
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
screen.fill(background_color)
pygame.display.update()

scratch = screen.copy()
font = pygame.font.Font(None, 14)
linelen = screen_width/font.size('a')[0]
keepRect = pygame.Rect((0, text_height), (screen_width, screen_width-text_height))
scrollingRect = pygame.Rect((0, 0), (screen_width, screen_height - text_height))
writeRect = pygame.Rect((0, screen_height-text_height), (screen_width, text_height))

#initialize the IRC connection
import socket
import select

def say(chan, words):
    send = 'PRIVMSG %s :%s\r\n' % (chan, words)
    sock.send(send)

def checkForMessages():
    read_list, write_list, error_list = \
               select.select([sock], [], [sock], 0)
    if sock in read_list:
        raw = sock.recv(8000)
        print raw

network = 'irc.freenode.net'
port = 6667
nick = 'lolasuketo'
uname = 'jinna'
host = 'jlei-laptop'
server = 'comcast'
realname = 'python irc bot'
channel = '#kamtest'

sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
sock.connect ( ( network, port ) )
sock.send ('NICK %s \r\n' % nick )
sock.send ( 'USER %s %s %s :%s r\n' % (uname, host, server, realname))
sock.send ( 'JOIN %s\r\n' % channel)

checkForMessages()
say(channel, "Hi there")

data = ''
while data != 'QUIT':
    data = raw_input('> ')
    update(data)
    
checkForMessages()
