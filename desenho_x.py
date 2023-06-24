import pygame


class Xdrawing(pygame.sprite.DirtySprite):
    def __init__(self, pos_x: int, pos_y: int, estilo: int, x_size: int, *groups):
        super().__init__(*groups)
        self.estilo = estilo
        self.set_sprite()
        initial_size = self.image.get_size()
        size_rate = x_size / initial_size[0]
        self.new_size = (int(self.image.get_size()[0] * size_rate), int(self.image.get_size()[1] * size_rate))
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = pygame.rect.Rect((pos_x * x_size, pos_y * x_size), self.image.get_size())

    def set_sprite(self):
        if self.estilo == 0:
            self.image = pygame.image.load("images/X-Letter.png")
        elif self.estilo == 1:
            self.image = pygame.image.load('images/X-Letter_Blue.png')
        else:
            self.image = pygame.image.load('images/png_sd_preto.png')
