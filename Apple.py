import pygame

class Apple:
    def __init__(self, weight: int, color, grow_amount: int):
        self.weight: int = weight
        self.color = color
        self.grow_amount: int = grow_amount