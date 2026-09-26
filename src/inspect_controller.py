import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("コントローラーが見つかりません")
    raise SystemExit

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Controller:", joystick.get_name())
print("Ctrl+C で終了")
print()

while True:
    pygame.event.pump()

    axes = [
        round(joystick.get_axis(i), 3)
        for i in range(joystick.get_numaxes())
    ]

    buttons = [
        joystick.get_button(i)
        for i in range(joystick.get_numbuttons())
    ]

    hats = [
        joystick.get_hat(i)
        for i in range(joystick.get_numhats())
    ]

    print(
        "\r"
        f"axes={axes}  "
        f"buttons={buttons}  "
        f"hats={hats}",
        end=""
    )

    time.sleep(0.05)