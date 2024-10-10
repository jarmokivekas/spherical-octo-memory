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