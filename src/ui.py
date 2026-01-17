import pygame
pygame.font.init()

class Font:
    def __init__(self, font=None, size=24, color=(255,255,255)):
        self.font = None
        if font:
            self.font = pygame.font.Font(font, size=size)
        else:
            self.font = pygame.font.Font(None, size=size)

        self.color = color

    def draw_text(self, screen: pygame.surface.Surface, text, pos, button=False, centered=False):
        if not button:
            rendered_text = self.font.render(text, antialias=True, color=self.color)
            if centered:
                rect = rendered_text.get_rect(center=pos)
                pos = rect
            screen.blit(rendered_text, pos)
        elif button:
            rendered_text = self.font.render(text, antialias=True, color=self.color)
            rect = rendered_text.get_rect(center=pos)
            screen.blit(rendered_text, rect)


# Button Class
class Button:
    def __init__(self, x, y, width, height, text, color=(100,100,100), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.centerx = x
        self.rect.centery = y
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False

    # Draw the Button - Assigning Collision and Bliting to Surface
    def draw(self, surface, font:Font):
        color = (150, 150, 150) if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)

        font.draw_text(surface, self.text, (self.rect.centerx, self.rect.centery), button=True)

    # Event for Button Clicked
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    # Event for Update Hover
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)