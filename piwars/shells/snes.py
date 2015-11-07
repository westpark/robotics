import pygame
from . import comms
sender = comms.Sender()

#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 191, 255)

#Images
RIGHT_ARROW_IMAGE = "right_arrow.png"
SNES_BACKGROUND_IMAGE = "controller.JPG"

#Key commands
FORWARD = "forward"
BACK = "backward"
LEFT = "left"
RIGHT = "right"
BLUE_KEY = "stop"
RED_KEY = "stop"
YELLOW_KEY = "stop"
GREEN_KEY = "stop"
LR_LEFT = None
LR_RIGHT = None
SELECT_KEY = "stop"
START_KEY = "stop"

#Key Classes
class Key():
	def __init__(self, image, xy_position, command):
		self.image = image
		self.xy_position = xy_position
		self.pressed = False
		self.command = command

class Arrow_Key(Key):
	def __init__(self, xy_position, rotation, command):
		image = pygame.image.load(RIGHT_ARROW_IMAGE).convert()
		image.set_colorkey(BLACK)
		image = pygame.transform.rotate(image, rotation) 
		super().__init__(image, xy_position, command)
		
class Round_Key(Key):
	def __init__(self, color, xy_position, command, radius=20 ):
		diameter = 2*radius		 
		image = pygame.Surface((diameter, diameter))
		image.set_colorkey(BLACK)
		pygame.draw.circle(image, color, [radius, radius], radius)
		super().__init__(image, xy_position, command)

class LR_Key(Key):
	def __init__(self, xy_position, command, length=100):
		height = length/4
		image = pygame.Surface((length, height))
		image.fill(RED)
		super().__init__(image, xy_position, command)
		
class Thin_Key(Key):
	def __init__(self, xy_position, command, length=35):
		image = pygame.Surface((length, length))
		image.set_colorkey(BLACK)
		pygame.draw.line(image, RED, [0, length], [length, 0], 30)
		super().__init__(image, xy_position, command)

#Keypad Classes		
class Keypad():
	def __init__(self, keys, axes, background_image, xy_position):
		self.keys = keys
		self. axes = axes
		self.background_image = background_image
		self.xy_position = xy_position
		self.device = pygame.joystick.Joystick(0)
		self.device.init()
		
class Snes_Keypad(Keypad):
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
		Arrow_Key([left_arrow_x, left_arrow_y], 180, LEFT),
		Arrow_Key([right_arrow_x, right_arrow_y], 0, RIGHT),
		],
		[
		Arrow_Key([up_arrow_x, up_arrow_y], 90, FORWARD),
		Arrow_Key([down_arrow_x, down_arrow_y], -90, BACK),
		], 
		]
		
		keys = [ 
		Round_Key(BLUE, [x_key_x, x_key_y], BLUE_KEY),
		Round_Key(RED, [a_key_x, a_key_y], RED_KEY),
		Round_Key(YELLOW, [b_key_x, b_key_y], YELLOW_KEY),
		Round_Key(GREEN, [y_key_x, y_key_y], GREEN_KEY), 
		LR_Key([l_key_x, l_key_y], LR_LEFT),
		LR_Key([r_key_x, r_key_y], LR_RIGHT),
		"BLANK", #These keys don't exist on the snes keypad
		"BLANK", #These keys don't exist on the snes keypad
		Thin_Key([select_key_x, select_key_y], SELECT_KEY),
		Thin_Key([start_key_x, start_key_y], START_KEY),
		]
		
		background_image = pygame.image.load(SNES_BACKGROUND_IMAGE).convert()
		background_image.set_colorkey(WHITE)
		super().__init__(keys, axes, background_image, xy_position)

	
pygame.init()
 
# Set the width and height of the screen [width, height]
size = (500, 500)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("My Game")
 
# Loop until the user clicks the close button.
 
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
keypad = Snes_Keypad([0,0])
done = False
buttons = keypad.device.get_numbuttons()
axes = keypad.device.get_numaxes()

SPEED_STEP = 0.2
speed = 1.0

while not done:
	# --- Main event loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == 10:
			if keypad.device.get_button(4):
				speed -= SPEED_STEP
				print("Left:", speed)
			if keypad.device.get_button(5):
				speed += SPEED_STEP
				print("Right:", speed)
		screen.fill(WHITE)
		screen.blit(keypad.background_image, keypad.xy_position)
	for i in range(buttons):
		button = keypad.device.get_button(i)
		if button and keypad.keys[i].command:
			print("KEY COMMAND:", keypad.keys[i].command)
			sender.send(keypad.keys[i].command)
			screen.blit(keypad.keys[i].image, keypad.keys[i].xy_position)
	for i in range(axes):
		axis = keypad.device.get_axis(i)
		if axis > 0.1:
			command = "{} {}".format(keypad.axes[i][1].command, speed)
			print("COMMAND1:", command)
			sender.send(command)
			screen.blit(keypad.axes[i][1].image, keypad.axes[i][1].xy_position)
		elif axis < -0.1:
			# command = "{} {}".format(keypad.axes[i][0].command, speed)
			command = "%s %s" % (keypad.axes[i][0].command, speed)
			print("COMMAND2:", command)
			sender.send(command)
			screen.blit(keypad.axes[i][0].image, keypad.axes[i][0].xy_position)
	pygame.display.flip()
	clock.tick(60)
 
pygame.quit()
 
