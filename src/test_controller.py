import pygame

pygame.init()
pygame.joystick.init()

count = pygame.joystick.get_count()

print("検出されたコントローラー数:", count)

for i in range(count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

    print()
    print("index :", i)
    print("name  :", joystick.get_name())
    print("axes  :", joystick.get_numaxes())
    print("buttons:", joystick.get_numbuttons())
    print("hats  :", joystick.get_numhats())