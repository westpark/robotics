import os
import pygame
import time
from . import comms
from ..core import comms as new_comms

TOLERANCE = 0.01
SPEED_STEP = 0.1
TOP_SPEED = 1.0
MIN_SPEED = 0.30
TURN_NINETY_FRACTION = 0.33
TURN_FRACTION = 0.17
NINETY_DEGREE_TURN_TIME_LEFT = 3.7
NINETY_DEGREE_TURN_TIME_RIGHT = 3.7
TURN_NINETY_LEFT_COMMAND = "turn left {} 1 {}".format(TURN_NINETY_FRACTION, NINETY_DEGREE_TURN_TIME_LEFT)
TURN_NINETY_RIGHT_COMMAND = "turn right {} 1 {}".format(TURN_NINETY_FRACTION, NINETY_DEGREE_TURN_TIME_RIGHT)
TURN_LEFT_COMMAND = "turn left {}".format(TURN_FRACTION)
TURN_RIGHT_COMMAND = "turn right {}".format(TURN_FRACTION)
FORWARD_COMMAND = "forward"
BACK_COMMAND = "backward"
STOP_COMMAND = "stop"
AUTO_START_COMMAND = "start"
AUTO_STOP_COMMAND = "stop"
THREE_POINT_TURN_COMMAND = "mode 3point"
SPRINT_COMMAND = "mode sprint"
MANUAL_COMMAND = "mode manual"

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
		diameter = 2 * radius
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

class Screen_Item(object):
	def __init__(self, button, xy_position, label, command, to_screen = None, offset = 50):
		font = pygame.font.Font(None, 36)
		self.label = font.render(label, True, BLACK)
		self.button = button
		self.command = command
		self.to_screen = to_screen
		self.button_xy = xy_position
		self.label_xy = [xy_position[0] + offset, xy_position[1]]

# --- Keypad Classes
class Keypad():
	def __init__(self, keys, axes, background_image, xy_position, mode_screens):
		self.keys = keys
		self.axes = axes
		self.background_image = background_image
		self.xy_position = xy_position
		self.mode_screens = mode_screens
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
	STOP_BUTTON = 9
	SELECT_BUTTON = 8
	AUTO_START_BUTTON = 0
	AUTO_STOP_BUTTON = 2
	AUTO_EXIT_BUTTON = 3
	MODE_THREE_POINT_BUTTON = 0
	MODE_SPRINT_BUTTON = 1
	MODE_MANUAL_BUTTON = 2
	MANUAL_SCREEN = 1
	MODE_SELECT_SCREEN = 2
	AUTO_SCREEN = 3

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
		
		select_options_x = 200
		select_3_point_turn_y = 200
		select_gulley_race_y = 300
		select_manual_drive_y = 400
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
		Round_Key(BLUE, [x_key_x, x_key_y],),
		Round_Key(RED, [a_key_x, a_key_y],),
		Round_Key(YELLOW, [b_key_x, b_key_y],),
		Round_Key(GREEN, [y_key_x, y_key_y],), 
		LR_Key([l_key_x, l_key_y]),
		LR_Key([r_key_x, r_key_y]),
		"BLANK", #This key doesn't exist on the snes keypad
		"BLANK", #This key doesn't exist on the snes keypad
		Thin_Key([select_key_x, select_key_y]),
		Thin_Key([start_key_x, start_key_y]),
		]
		
		select_x = 200
		mode_screens = ('NORMAL SCREEN PLACEHOLDER',
						'NORMAL SCREEN PLACEHOLDER',
						(
						Screen_Item(self.MODE_THREE_POINT_BUTTON, [select_x, 100], "3 Point Turn", THREE_POINT_TURN_COMMAND, self.AUTO_SCREEN),
						Screen_Item(self.MODE_SPRINT_BUTTON, [select_x, 200], "Sprint", SPRINT_COMMAND, self.AUTO_SCREEN),
						Screen_Item(self.MODE_MANUAL_BUTTON, [select_x, 300], "Manual Control", MANUAL_COMMAND, self.MANUAL_SCREEN),
						),
						(
						Screen_Item(self.AUTO_START_BUTTON, [select_x, 100], "Start", AUTO_START_COMMAND),
						Screen_Item(self.AUTO_STOP_BUTTON, [select_x, 200], "Stop", AUTO_STOP_COMMAND),
						Screen_Item(self.AUTO_EXIT_BUTTON, [select_x, 300], "Exit", MANUAL_COMMAND, self.MANUAL_SCREEN),
						))
		background_image = pygame.image.load(self.BACKGROUND_IMAGE).convert()
		background_image.set_colorkey(WHITE)
		super().__init__(keys, axes, background_image, xy_position, mode_screens)

class Speedo(object):
	def __init__(self):
		self.image = pygame.Surface((100, 100))
		self.font = pygame.font.Font(None, 36)
		self.fixed_text = self.font.render("Speed", True, WHITE)
		
	def update(self, speed):
		self.image.fill(BLACK)
		self.image.blit(self.fixed_text,[10, 5])
		show_speed = self.font.render(str(speed), True, RED)
		self.image.blit(show_speed, [25, 50])

class Mode_Display(object):
	def __init__(self):
		self.subscriber = new_comms.Subscriber()
		self.subscriber.subscribe()
		self.message = "Initialising..."
		self.image = pygame.Surface((500, 40))
		self.font = pygame.font.Font(None, 36)
		
	def update(self):
		self.image.fill(BLACK)
		message_received = self.subscriber.get_message()
		if message_received:
			message_type = message_received.split()[0]
			message_end = message_received.split()[-1] 
			if message_type == "INFO" and not message_end == "[]":
				self.message = message_received.split('-')[1].strip()
		show_mode = self.font.render(self.message, True, RED)
		self.image.blit(show_mode, (50, 5))

# --- Event Result functions
def mode_joybuttondown_results(keypad, screen_number, sender):
	for item in keypad.mode_screens[screen_number]:
		if keypad.device.get_button(item.button):
			sender.send(item.command)
			if item.to_screen:
				return item.to_screen
	return screen_number

def joybuttondown_results(keypad, speed, sender):
	if keypad.device.get_button(keypad.SPEED_DOWN_BUTTON) and speed > MIN_SPEED + TOLERANCE:
		speed -= SPEED_STEP
	elif keypad.device.get_button(keypad.SPEED_UP_BUTTON) and speed + SPEED_STEP < TOP_SPEED + TOLERANCE:
		speed += SPEED_STEP
	elif keypad.device.get_button(keypad.TOP_SPEED_BUTTON):
		speed = TOP_SPEED
	elif keypad.device.get_button(keypad.MIN_SPEED_BUTTON):
		speed = MIN_SPEED
	elif keypad.device.get_button(keypad.TURN_LEFT_BUTTON):
		sender.send(TURN_NINETY_LEFT_COMMAND)
	elif keypad.device.get_button(keypad.TURN_RIGHT_BUTTON):
		sender.send(TURN_NINETY_RIGHT_COMMAND)
	elif keypad.device.get_button(keypad.STOP_BUTTON):
		sender.send(STOP_COMMAND)
	elif keypad.device.get_button(keypad.SELECT_BUTTON):
		return keypad.MODE_SELECT_SCREEN, speed
	return keypad.MANUAL_SCREEN, speed

def joyaxismotion_results(keypad, axes, speed, sender):
	axis_total = 0
	for i in range(axes):
		axis = keypad.device.get_axis(i)
		axis_total += abs(axis)
		if axis > TOLERANCE:
			command = "{} {}".format(keypad.axes[i][1].command, speed)
			sender.send(command)
		elif axis < 0 - TOLERANCE:
			command = "{} {}".format(keypad.axes[i][0].command, speed)
			sender.send(command)
	if axis_total < axes * TOLERANCE:
		sender.send(STOP_COMMAND)
		
def main():
	pygame.init()
	size = (500, 500)
	screen = pygame.display.set_mode(size)
	keypad = Snes_Keypad([0,0])
	clock = pygame.time.Clock()
	sender = comms.Sender()
	pygame.display.set_caption("Robot Controller")
	buttons = keypad.device.get_numbuttons()
	axes = keypad.device.get_numaxes()
	speed = TOP_SPEED
	speedo = Speedo()
	mode_display = Mode_Display()
	screen_number = 1
	message = "Initialising..."

	
	done = False
	while not done:
		# --- Main event loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
			if event.type == pygame.JOYBUTTONDOWN:
				if screen_number == keypad.MANUAL_SCREEN:
					screen_number, speed = joybuttondown_results(keypad, speed, sender)
				else:
					screen_number = mode_joybuttondown_results(keypad, screen_number, sender)
			if event.type == pygame.JOYAXISMOTION and screen_number == keypad.MANUAL_SCREEN:
				joyaxismotion_results(keypad, axes, speed, sender)
		
		# --- Update Display
		screen.fill(WHITE)
		if screen_number == keypad.MANUAL_SCREEN:
			screen.blit(keypad.background_image, keypad.xy_position)
			for i in range(buttons):
				button = keypad.device.get_button(i)
				if button:
					show_button = keypad.keys[i]
					screen.blit(show_button.image, show_button.xy_position)
			for i in range(axes):
				axis = keypad.device.get_axis(i)
				if axis > TOLERANCE:
					arrow = keypad.axes[i][1]
					screen.blit(arrow.image, arrow.xy_position)
				elif axis < 0 - TOLERANCE:
					arrow = keypad.axes[i][0]
					screen.blit(arrow.image, arrow.xy_position)
			speedo.update(speed)
			screen.blit(speedo.image, [10,10])
		else:
			for item in keypad.mode_screens[screen_number]:
				key = keypad.keys[item.button]
				screen.blit(key.image, item.button_xy)
				screen.blit(item.label, item.label_xy)
		
		mode_display.update()
		screen.blit(mode_display.image, [0,460])
		pygame.display.flip()
		clock.tick(60)
	pygame.quit()

class Shell(object):
	def start(self):
		main()

if __name__ == "__main__":
    main()