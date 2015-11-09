import os
import pygame
import time
from . import comms

TOLERANCE = 0.01
SPEED_STEP = 0.1
TOP_SPEED = 1.0
MIN_SPEED = 0.30
TURN_FRACTION = 0.25
NINETY_DEGREE_TURN_TIME = 0.5
TURN_LEFT_COMMAND = "turn left {}".format(TURN_FRACTION)
TURN_RIGHT_COMMAND = "turn right {}".format(TURN_FRACTION)
FORWARD_COMMAND = "forward"
BACK_COMMAND = "backward"
STOP_COMMAND = "stop"

HERE = os.path.dirname(__file__)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 191, 255)

# --- Key Classes
class Key():
	def __init__(self, image, xy_position):
		self.image = image
		self.xy_position = xy_position
		self.pressed = False

class Arrow_Key(Key):
	RIGHT_ARROW_IMAGE = os.path.join(HERE, "right_arrow.png")
	def __init__(self, xy_position, rotation, command):
		image = pygame.image.load(self.RIGHT_ARROW_IMAGE).convert()
		image.set_colorkey(BLACK)
		image = pygame.transform.rotate(image, rotation)
		self.command = command
		super().__init__(image, xy_position)
		
class Round_Key(Key):
	def __init__(self, color, xy_position, radius=20):
		diameter = 2*radius
		image = pygame.Surface((diameter, diameter))
		image.set_colorkey(BLACK)
		pygame.draw.circle(image, color, [radius, radius], radius)
		super().__init__(image, xy_position)

class LR_Key(Key):
	def __init__(self, xy_position, length=100):
		height = length/4
		image = pygame.Surface((length, height))
		image.fill(RED)
		super().__init__(image, xy_position)
		
class Thin_Key(Key):
	def __init__(self, xy_position, length=35):
		image = pygame.Surface((length, length))
		image.set_colorkey(BLACK)
		pygame.draw.line(image, RED, [0, length], [length, 0], 30)
		super().__init__(image, xy_position)

# --- Keypad Classes		
class Keypad():
	def __init__(self, keys, axes, background_image, xy_position):
		self.keys = keys
		self.axes = axes
		self.background_image = background_image
		self.xy_position = xy_position
		self.device = pygame.joystick.Joystick(0)
		self.device.init()
		
class Snes_Keypad(Keypad):
	BACKGROUND_IMAGE = os.path.join(HERE,  "controller.JPG")
	TOP_SPEED_BUTTON = 0
	MIN_SPEED_BUTTON = 2
	TURN_RIGHT_BUTTON = 1
	TURN_LEFT_BUTTON = 3
	SPEED_DOWN_BUTTON = 4
	SPEED_UP_BUTTON = 5

	def __init__(self, xy_position):
		arrows_center_x = 85 + xy_position[0]
		arrows_center_y = 275 + xy_position[1]
		arrows_center = [arrows_center_x, arrows_center_y]
		arrows_image_offset = 30
		left_arrow_x = arrows_center[0] - arrows_image_offset
		left_arrow_y = arrows_center[1]
		right_arrow_x = arrows_center[0] + arrows_image_offset
		right_arrow_y = arrows_center[1]
		up_arrow_x = arrows_center[0]
		up_arrow_y = arrows_center[1] - arrows_image_offset
		down_arrow_x = arrows_center[0]
		down_arrow_y = arrows_center[1] + arrows_image_offset
		a_key_x = xy_position[0] + 415
		a_key_y = xy_position[1] + 278
		b_key_x = xy_position[0] + 368
		b_key_y = xy_position[1] + 313
		x_key_x = xy_position[0] + 370
		x_key_y = xy_position[1] + 244
		y_key_x = xy_position[0] + 324
		y_key_y = xy_position[1] + 279
		l_key_x = 62
		l_key_y = 187
		r_key_x = 330
		r_key_y = 187
		select_key_x = 190
		select_key_y = 294
		start_key_x = 242
		start_key_y = 294
		axes = [
		[
		Arrow_Key([left_arrow_x, left_arrow_y], 180, TURN_LEFT_COMMAND),
		Arrow_Key([right_arrow_x, right_arrow_y], 0, TURN_RIGHT_COMMAND),
		],
		[
		Arrow_Key([up_arrow_x, up_arrow_y], 90, FORWARD_COMMAND),
		Arrow_Key([down_arrow_x, down_arrow_y], -90, BACK_COMMAND),
		], 
		]
		
		keys = [ 
		Round_Key(BLUE, [x_key_x, x_key_y]),
		Round_Key(RED, [a_key_x, a_key_y]),
		Round_Key(YELLOW, [b_key_x, b_key_y]),
		Round_Key(GREEN, [y_key_x, y_key_y]), 
		LR_Key([l_key_x, l_key_y]),
		LR_Key([r_key_x, r_key_y]),
		"BLANK", #This key doesn't exist on the snes keypad
		"BLANK", #This key doesn't exist on the snes keypad
		Thin_Key([select_key_x, select_key_y]),
		Thin_Key([start_key_x, start_key_y]),
		]
		
		background_image = pygame.image.load(self.BACKGROUND_IMAGE).convert()
		background_image.set_colorkey(WHITE)
		super().__init__(keys, axes, background_image, xy_position)

# --- Event Result functions
def joybuttondown_results(keypad):
	if keypad.device.get_button(keypad.SPEED_DOWN_BUTTON) and speed > MIN_SPEED + TOLERANCE:
		speed -= SPEED_STEP
	elif keypad.device.get_button(keypad.SPEED_UP_BUTTON) and speed + SPEED_STEP < TOP_SPEED + TOLERANCE:
		speed += SPEED_STEP
	if keypad.device.get_button(keypad.TOP_SPEED_BUTTON):
		speed = TOP_SPEED
	elif keypad.device.get_button(keypad.MIN_SPEED_BUTTON):
		speed = MIN_SPEED
	if keypad.device.get_button(keypad.TURN_LEFT_BUTTON):
		sender.send(TURN_LEFT_COMMAND)
		time.sleep(NINETY_DEGREE_TURN_TIME)
		sender.send(STOP_COMMAND)
	elif keypad.device.get_button(keypad.TURN_RIGHT_BUTTON):
		sender.send(TURN_RIGHT_COMMAND)

def joyaxismotion_results(keypad):
	axis_total = 0
	for i in range(axes):
		axis = keypad.device.get_axis(i)
		axis_total += abs(axis)
		if axis > TOLERANCE:
			command = "{} {}".format(keypad.axes[i][1].command, speed)
			sender.send(command)
		elif axis < -TOLERANCE:
			command = "{} {}".format(keypad.axes[i][0].command, speed)
			sender.send(command)
	if axis_total < TOLERANCE:
		sender.send(STOP_COMMAND)

def speedo(speed, font):
	image = pygame.Surface((100, 100))
	image.fill(BLACK)
	text = font.render("Speed", True, WHITE)
	show_speed = font.render(str(speed), True, RED)
	image.blit(text,[10, 5])
	image.blit(show_speed, [25, 50])
	return image

def display_command(command, font):
	image = pygame.Surface((500, 40))
	image.fill(BLACK)
	text = font.render("COMMAND:", True, WHITE)
	show = font.render(command, True, RED)
	image.blit(text,[10, 5])
	image.blit(show, [160, 5])
	return image
	
pygame.init()
size = (500, 500)
screen = pygame.display.set_mode(size)
font = pygame.font.Font(None, 36)
pygame.display.set_caption("Robot Controller")
clock = pygame.time.Clock()
sender = comms.Sender()
keypad = Snes_Keypad([0,0])
buttons = keypad.device.get_numbuttons()
axes = keypad.device.get_numaxes()

speed = TOP_SPEED
done = False
while not done:
	# --- Main event loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == pygame.JOYBUTTONDOWN:
			joybuttondown_results(keypad)
		if event.type == pygame.JOYAXISMOTION:
			joyaxismotion_results(keypad)
	# --- Update Display
	screen.fill(WHITE)
	screen.blit(keypad.background_image, keypad.xy_position)
	for i in range(buttons):
		button = keypad.device.get_button(i)
		if button:
			screen.blit(keypad.keys[i].image, keypad.keys[i].xy_position)
	for i in range(axes):
		axis = keypad.device.get_axis(i)
		if axis > TOLERANCE:
			screen.blit(keypad.axes[i][1].image, keypad.axes[i][1].xy_position)
		elif axis < -TOLERANCE:
			screen.blit(keypad.axes[i][0].image, keypad.axes[i][0].xy_position)
	screen.blit(speedo(speed, font), [10,10])
	screen.blit(display_command(str(speed), font), [0,460])
	pygame.display.flip()
	clock.tick(60)
pygame.quit()