import pygame


class Navio(pygame.sprite.DirtySprite):
    def __init__(self, pos_x: int, pos_y: int, length: int, direcao: str, sq_size: int, *groups):
        super().__init__(*groups)
        self.length = length
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.p1_points = 0
        self.p2_points = 0
        self.direction = direcao
        self.set_sprite()
        self.isRotated = False
        self.verify_direction()
        self.transform_sprite()
        self.rect = pygame.rect.Rect((self.pos_x * sq_size, self.pos_y * sq_size), self.image.get_size())
        self.sunken = False
        self.position_grid = []
        self.set_position_grid()
        self.visible = 0

    def set_sprite(self):
        if self.length == 1:
            self.image = pygame.image.load("images/Navio_1pc.png")
        elif self.length == 2:
            self.image = pygame.image.load('images/Navio_2pc.png')
        elif self.length == 3:
            self.image = pygame.image.load('images/Navio_3pc.png')
        elif self.length == 4:
            self.image = pygame.image.load('images/Navio_4pc.png')
        else:
            self.image = pygame.image.load('images/Navio_5pc.png')

    def transform_sprite(self):
        if self.isRotated:
            self.image = pygame.transform.scale(self.image, (self.length * 50, 50))
        else:
            self.image = pygame.transform.scale(self.image, (50, self.length*50))

    def set_position_grid(self):
        """
        Define a posição na grelha com base na sua posição inicial x,y e a sua orientação
        :return: Lista das posições ocupadas pelo navio
        """
        j = 0
        if self.direction == "horizontal":
            for _ in range(self.length):
                self.position_grid.append((self.pos_x + j, self.pos_y))
                j += 1
        else:
            for _ in range(self.length):
                self.position_grid.append((self.pos_x, self.pos_y + j))
                j += 1

        return self.position_grid

    def verify_direction(self):
        if self.direction == "horizontal":
            self.image = pygame.transform.rotate(self.image, 270)
            self.isRotated = True

    def get_position_grid(self):
        return self.position_grid

    def set_sunken(self):
        self.sunken = True
        self.visible = 1

    def get_sunken(self):
        return self.sunken

    def get_p1_points(self):
        return self.p1_points

    def get_p2_points(self):
        return self.p2_points

    def add_p1_points(self):
        self.p1_points += 1

    def add_p2_points(self):
        self.p2_points += 1
