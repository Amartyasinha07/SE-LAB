import pygame

LANES = 4
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_LABELS = ['D', 'F', 'J', 'K']
LANE_COLORS = [(220, 80, 80), (80, 180, 220), (100, 220, 100), (220, 180, 60)]


class Note:
    """A normal tap note. `y` is the top edge of the note."""
    WIDTH = 70
    HEIGHT = 20
    is_hold = False

    def __init__(self, lane, y=-30, speed=4):
        self.lane = lane
        self.y = y
        self.speed = speed
        self.hit = False      # player hit it
        self.missed = False   # it passed the hit window unhit
        self.dead = False     # engine should remove it

    def update(self):
        self.y += self.speed

    def get_rect(self, lane_x):
        return pygame.Rect(lane_x - self.WIDTH // 2, int(self.y), self.WIDTH, self.HEIGHT)

    @property
    def offscreen_top(self):
        """Highest point of the note (used to know when it has fully left the screen)."""
        return self.y


class HoldNote(Note):
    """A long note: hit the head on time, then keep the key held for HOLD_SECONDS.

    The head is the bottom (leading) edge, the tail trails above it. `length` is
    the distance in pixels from head to tail. Once the player grabs the head it
    is pinned on the hit line and `length` shrinks at the note speed, so the
    tail reaches the line after exactly HOLD_SECONDS.
    """
    HOLD_SECONDS = 1.0
    is_hold = True

    def __init__(self, lane, y=-30, speed=4, fps=60):
        super().__init__(lane, y, speed)
        self.length = speed * fps * self.HOLD_SECONDS
        self.holding = False
        # pending grade info, scored when the hold is completed
        self.grade = None
        self.pts = 0
        self.color = (255, 255, 255)

    def update(self):
        if self.holding:
            self.length -= self.speed   # head stays pinned, tail comes down
        else:
            self.y += self.speed

    @property
    def completed(self):
        return self.holding and self.length <= 0

    def get_body_rect(self, lane_x):
        w = self.WIDTH - 24
        top = int(self.y - self.length)
        bottom = int(self.y) + self.HEIGHT
        return pygame.Rect(lane_x - w // 2, top, w, max(0, bottom - top))

    @property
    def offscreen_top(self):
        return self.y - self.length
