import pygame
import json


class Overlay:
    def __init__(self, screen, font_size=14, font_color=(255, 255, 255), bg_alpha=0):
        self.screen = screen
        self.font_size = font_size
        self.font_color = font_color
        self.bg_alpha = bg_alpha

        # Set up font (can be customized)

        pygame.font.init()

        PressStart2P = "roller/assets/fonts/PressStart2P/PressStart2P-Regular.ttf"
        # self.font = pygame.font.SysFont('monospace', self.font_size)
        self.font = pygame.font.SysFont('ubuntu mono', self.font_size)
        # self.font = pygame.font.SysFont(PressStart2P, self.font_size)

    def render_housekeeping(self, data):
        # Convert JSON to formatted text string
        json_text = json.dumps(data, indent=4)
        
        # Split the text into lines
        lines = json_text.splitlines()

        # Create a transparent surface for the overlay
        text_overlay = pygame.Surface((self.screen.get_width(), len(lines) * self.font_size), pygame.SRCALPHA)

        # Fill the surface with a semi-transparent background
        text_overlay.fill((0, 0, 0, self.bg_alpha))

        # Render each line of text
        y_offset = 0
        for line in lines:
            text_surface = self.font.render(line, True, self.font_color)
            text_overlay.blit(text_surface, (10, y_offset))
            y_offset += self.font_size

        # y_offset is not the total pixel height of the text block
        # we now offset the entire text_surface so that the block
        # of json is middle-aligne verically
        # this is maybe confusin re-usde of y_offset. 
        y_offset = self.screen.get_height() / 2 - y_offset/2
        # Blit the overlay on top of the screen
        self.screen.blit(text_overlay, (0, y_offset))

    @staticmethod
    def get_middle_alignment_offset(text_surface, screen_surface):
        return (screen_surface.get_height() / 2)



import pygame

class LinePlot:
    def __init__(self, surface, data, rect, line_color=(255, 165, 0), background_color=(0, 0, 0)):
        """
        Initialize the LinePlot class.

        Args:
            surface: The Pygame surface to draw the plot on.
            data: List of (x, y) tuples representing the data points.
            rect: A pygame.Rect defining the area of the plot on the surface.
            line_color: The color of the line plot (default is orange).
            background_color: The background color of the plot (default is black).
        """
        self.surface = surface
        self.data = data
        self.rect = rect
        self.line_color = line_color
        self.background_color = background_color
        self.idx = 0

    def add_data(self, point):
        """Uses a round-robin data buffer to add a new datapoint, replacing the oldest one."""
        self.idx = (self.idx + 1) % len(data)
        assert(self.idx < len(data))  

        # Update the minimum and maximum limits of the data, used to scale plotted values
        x_min = point.x if point.x < x_min else x_min
        x_max = point.x if point.x > x_max else x_max
        y_min = point.y if point.y < y_min else y_min
        y_max = point.y if point.y > y_max else y_max

        data[self.idx] = point

    def update_plot()

        pygame.draw.line(self.surface, self.line_color, scale(self.data[i]), scale(self.data[i+1]), 1)


    def scale(self, point, x_min, x_max, y_min, y_max):
        """Scale the (x, y) data point to fit within the plot rect."""
        x, y = point
        x_scaled = self.rect.left + (x - x_min) / (x_max - x_min) * self.rect.width
        y_scaled = self.rect.bottom - (y - y_min) / (y_max - y_min) * self.rect.height
        return (x_scaled, y_scaled)

    def draw(self):
        """Draw the line plot on the given surface."""
        # Fill the background of the plot
        pygame.draw.rect(self.surface, self.background_color, self.rect)

        if len(self.data) < 2:
            return  # Not enough data to draw a line

        # Scale the data points to fit within the plot area
        x_vals = [point[0] for point in self.data]
        y_vals = [point[1] for point in self.data]

        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)

        x_vals = self.scale(x)
        # Draw the lines connecting the scaled data points
        for i in range(len(self.data) - 1):
            pygame.draw.line(self.surface, self.line_color, scale(self.data[i]), scale(self.data[i+1]), 1)
