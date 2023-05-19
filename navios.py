import pygame


class Navio(pygame.sprite.DirtySprite):
    def __init__(self, pos_x: int, pos_y: int, length: int, direcao: str, sq_size: int, *groups):
        super().__init__(*groups)
        self.length = length
        self.set_sprite()
        self.isRotated = False
        self.x = pos_x  # hardcoded para o sink_ships
        self.y = pos_y
        if direcao == "horizontal":
            self.image = pygame.transform.rotate(self.image, 270)
            self.isRotated = True
        self.transform_sprite()
        self.rect = pygame.rect.Rect((pos_x * sq_size, pos_y * sq_size), self.image.get_size())
        self.sunken = False
        self.position_grid = []

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_size(self):
        return self.new_size

    def update(self):
        pass

    def set_sunken(self, boolean):
        self.sunken = boolean

    def set_sprite(self):
        if self.length == 1:
            self.image = pygame.image.load("Navio_1pc.png")
        elif self.length == 2:
            self.image = pygame.image.load('Navio_2pc.png')
        elif self.length == 3:
            self.image = pygame.image.load('Navio_3pc.png')
        elif self.length == 4:
            self.image = pygame.image.load('Navio_4pc.png')
        else:
            self.image = pygame.image.load('Navio_5pc.png')


    def transform_sprite(self):
        if self.isRotated:
            self.image = pygame.transform.scale(self.image, (self.length * 50, 50))
        else:
            self.image = pygame.transform.scale(self.image, (50, self.length*50))