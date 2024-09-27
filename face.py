import sys
import time
import pygame
import spidev
from PIL import Image
import RPi.GPIO as GPIO
from luma.core.interface.serial import spi
from luma.lcd.device import st7735


# Define a Face class to manage the emotions and animations
class Face:
    def __init__(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('TFT Display')
        self.eyes_open = True
        self.mouth_open = False
        self.blinking = False
        self.speaking = False
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        self.device = st7735(self.serial, width=self.WIDTH, height=self.HEIGHT)
        self.screen.fill(self.BLACK)

    def draw_face(self):
        """Draw the face based on the current state (eyes and mouth open/closed)."""
        self.screen.fill(self.BLACK)

        # Draw eyes
        if self.eyes_open:
            pygame.draw.circle(self.screen, self.WHITE, ((self.WIDTH/2)-40, 25), 10)  # Left eye (open)
            pygame.draw.circle(self.screen, self.WHITE, ((self.WIDTH/2)+40, 25), 10) # Right eye (open)
        else:
            pygame.draw.rect(self.screen, self.WHITE, ((self.WIDTH/2)-55, 30, 30, 10))  # Left eye (closed)
            pygame.draw.rect(self.screen, self.WHITE, ((self.WIDTH/2)+25, 30, 30, 10)) # Right eye (closed)

        # Draw mouth
        if self.mouth_open:
            pygame.draw.rect(self.screen, self.WHITE, (40, (self.WIDTH/2)+10, 80, 30))  # Open mouth
        else:
			
            pygame.draw.rect(self.screen, self.WHITE, (40, (self.WIDTH/2)+10, 80, 10))  # Closed mouth

        pygame.display.flip()
        self.display()

    def blink(self):
        self.draw_face()
        """Animate a blink with smooth transitions."""
        if not self.blinking:
            self.blinking = True
            # Frame 1: Eyes open
            self.eyes_open = True
            self.draw_face()
            time.sleep(1)  # Keep eyes open for 1 second

            # Frame 2: Eyes closed
            self.eyes_open = False
            self.draw_face()
            time.sleep(0.2)  # Eyes closed for 0.2 seconds

            # Frame 3: Eyes open again
            self.eyes_open = True
            self.draw_face()
            time.sleep(1)  # Keep eyes open again for 1 second
            self.blinking = False

    def speak(self, duration=2, get_busy=False):
        """Simulate speaking by alternating between mouth open and closed."""
        self.speaking = True
        if not get_busy:
            start_time = time.time()

            while time.time() - start_time < duration:
                # Open mouth
                self.mouth_open = True
                self.draw_face()
                time.sleep(0.1)  # Mouth open

                # Close mouth
                self.mouth_open = False
                self.draw_face()
                time.sleep(0.1)  # Mouth closed
        else:
            self.mouth_open = True
            self.draw_face()
            time.sleep(0.1)  # Mouth open

            # Close mouth
            self.mouth_open = False
            self.draw_face()
            time.sleep(0.1)  # Mouth closed

        self.speaking = False
    
    def display(self):
        pygame_image_string = pygame.image.tostring(self.screen, "RGB")
        image = Image.frombytes("RGB", (self.WIDTH, self.HEIGHT), pygame_image_string)

        self.device.display(image)
        # GPIO.cleanup()


# Main loop function
def main_loop(face):
    """Main loop that handles events and controls face animations."""
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Simulate blinking
        if not face.blinking:
            face.blink()

        # Simulate speaking (for example, for 2 seconds)
        if not face.speaking:
            face.speak(2)

        # Control the frame rate (for smooth animation)
        clock.tick(30)  # Limit to 30 FPS for performance optimization

# Usage in the assistant
if __name__ == "__main__":
    pygame.init()
    GPIO.setmode(GPIO.BCM)
    width, height = 160, 128  # Adjust to your LCD screen size
    face = Face(width, height)
    face.blink()
    
    # # Frame 1: Eyes open
    # face.eyes_open = True
    # face.draw_face()
    # time.sleep(1)  # Keep eyes open for 1 second

    # # Frame 2: Eyes closed
    # face.eyes_open = False
    # face.draw_face()
    # time.sleep(0.2)  # Eyes closed for 0.2 seconds

    # face.eyes_open = True
    # face.draw_face()
    # time.sleep(1)  # Keep eyes open for 1 second

    GPIO.cleanup()
    pygame.quit()
    # main_loop(face)
