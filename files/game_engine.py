 stimport random
import pygame
from game.beat import Note, HoldNote, LANES, LANE_KEYS, LANE_LABELS, LANE_COLORS
from game.sounds import SoundBank

WIDTH, HEIGHT = 480, 640
FPS = 60
HIT_Y = HEIGHT - 80
HIT_WINDOW = 30
BG = (15, 10, 25)
LANE_W = WIDTH // LANES
MAX_MISSES = 15

# --- Task 3: BPM-synced spawning -------------------------------------------
BPM = 120                     # one note per beat
BEAT_LEN = 60.0 / BPM         # seconds per beat
LEAD_IN = 2.0                 # seconds before the first beat reaches the hit line
SPAWN_Y = -30                 # y where notes appear (top edge)

# --- Task 2: hold notes ------------------------------------------------------
HOLD_CHANCE = 0.2             # chance that a beat becomes a hold note
HOLD_MIN_BEAT = 8             # no hold notes during the first 8 beats
HOLD_GAP = 0.25               # extra seconds a lane/hold slot stays reserved

GRADES = ["PERFECT", "GREAT", "OK"]
GRADE_COLORS = {"PERFECT": (255, 220, 0), "GREAT": (100, 220, 100),
                "OK": (180, 180, 255), "MISS": (220, 60, 60)}


class GameEngine:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                pass  # no audio device: game runs silently
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rhythm Tap")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 26, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.sounds = SoundBank()
        self.reset()

    def reset(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.counts = {"PERFECT": 0, "GREAT": 0, "OK": 0, "MISS": 0}
        self.speed = 5
        self.frame = 0
        self.next_beat = 0
        self.lane_free_at = [0.0] * LANES   # song time when a lane may get a new note
        self.hold_free_at = 0.0             # only one hold note in flight at a time
        self.feedback = []  # (text, color, ttl, x, y)
        self.game_over = False

    # ---------------------------------------------------------------- helpers
    @property
    def misses(self):
        return self.counts["MISS"]

    @property
    def hits(self):
        return sum(self.counts[g] for g in GRADES)

    @property
    def accuracy(self):
        """Percentage of judged notes that were hit (PERFECT + GREAT + OK)."""
        total = self.hits + self.misses
        return 100.0 * self.hits / total if total else 0.0

    @property
    def song_time(self):
        return self.frame / FPS

    @staticmethod
    def lane_x(lane):
        return lane * LANE_W + LANE_W // 2

    # ------------------------------------------------- BPM-synced spawning
    @staticmethod
    def beat_time(n):
        """Song time (s) at which beat n must be exactly on the hit line."""
        return LEAD_IN + n * BEAT_LEN

    def travel_time(self, speed):
        """Seconds a note needs to fall from the spawn point to the hit line."""
        distance = HIT_Y - (SPAWN_Y + Note.HEIGHT // 2)
        return distance / (speed * FPS)

    def spawn_due_notes(self):
        while True:
            due = self.beat_time(self.next_beat) - self.travel_time(self.speed)
            if self.song_time + 1e-9 < due:
                break
            self.spawn_beat(self.next_beat, max(0.0, self.song_time - due))
            self.next_beat += 1

    def spawn_beat(self, n, elapsed):
        """Spawn the note for beat n. `elapsed` = seconds it is already late,
        so it is placed further down and still lands exactly on the beat."""
        t = self.beat_time(n)
        free = [l for l in range(LANES) if self.lane_free_at[l] <= t]
        if not free:
            return
        lane = random.choice(free)
        y = SPAWN_Y + elapsed * self.speed * FPS
        if n >= HOLD_MIN_BEAT and t >= self.hold_free_at and random.random() < HOLD_CHANCE:
            note = HoldNote(lane, y=y, speed=self.speed, fps=FPS)
            busy_until = t + HoldNote.HOLD_SECONDS + HOLD_GAP
            self.lane_free_at[lane] = busy_until
            self.hold_free_at = busy_until
        else:
            note = Note(lane, y=y, speed=self.speed)
        self.notes.append(note)

    # ----------------------------------------------------------------- input
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif not self.game_over:
                    for i, key in enumerate(LANE_KEYS):
                        if event.key == key:
                            self.process_tap(i)
            elif event.type == pygame.KEYUP and not self.game_over:
                for i, key in enumerate(LANE_KEYS):
                    if event.key == key:
                        self.process_release(i)
        return True

    @staticmethod
    def grade_for(dist):
        if dist < 8:
            return "PERFECT", 300
        if dist < 18:
            return "GREAT", 200
        return "OK", 100

    def register_hit(self, grade, pts, lane):
        self.counts[grade] += 1
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.score += pts * max(1, self.combo // 5)
        self.sounds.play(grade)                       # Task 1: sound on every hit
        self.feedback.append([grade, GRADE_COLORS[grade], 40, self.lane_x(lane), HIT_Y - 30])

    def register_miss(self, lane, text="MISS"):
        self.counts["MISS"] += 1
        self.combo = 0
        self.feedback.append([text, GRADE_COLORS["MISS"], 40, self.lane_x(lane), HIT_Y - 30])

    def process_tap(self, lane):
        # Find closest note in this lane near hit zone
        best = None
        best_dist = 9999
        for note in self.notes:
            if note.lane == lane and not note.hit and not note.missed and not note.dead:
                dist = abs(note.y + Note.HEIGHT // 2 - HIT_Y)
                if dist < best_dist:
                    best_dist = dist
                    best = note
        if best and best_dist <= HIT_WINDOW:
            grade, pts = self.grade_for(best_dist)
            best.hit = True
            if best.is_hold:
                # grab the head: pin it on the line; it scores once held for 1 second
                best.holding = True
                best.y = HIT_Y - Note.HEIGHT // 2
                best.grade, best.pts, best.color = grade, pts * 2, GRADE_COLORS[grade]
                self.feedback.append(["HOLD!", best.color, 40, self.lane_x(lane), HIT_Y - 30])
            else:
                best.dead = True
                self.register_hit(grade, pts, lane)
        else:
            self.register_miss(lane)   # ghost tap: counted, so the HUD matches the feedback

    def process_release(self, lane):
        for note in self.notes:
            if note.is_hold and note.holding and note.lane == lane:
                note.holding = False
                note.dead = True
                self.register_miss(lane, "DROPPED")

    # ---------------------------------------------------------------- update
    def update(self):
        if self.game_over:
            return
        self.frame += 1

        # difficulty ramp: every 10 seconds (was nested in the spawn block and never fired)
        if self.frame % 600 == 0:
            self.speed = min(10, self.speed + 0.5)

        self.spawn_due_notes()

        for note in self.notes:
            note.update()
            if note.is_hold and note.completed and not note.dead:
                note.dead = True
                self.register_hit(note.grade, note.pts, note.lane)
            elif (not note.hit and not note.missed
                  and note.y + Note.HEIGHT // 2 > HIT_Y + HIT_WINDOW):
                note.missed = True   # can no longer be hit
                self.register_miss(note.lane)

        self.notes = [n for n in self.notes
                      if not n.dead and not (n.missed and n.offscreen_top > HEIGHT + 10)]
        self.feedback = [[t, c, ttl - 1, x, y] for t, c, ttl, x, y in self.feedback if ttl > 1]

        if self.misses >= MAX_MISSES:
            self.game_over = True

    # ------------------------------------------------------------------ draw
    @staticmethod
    def dim(color, f=0.35):
        return tuple(int(c * f) for c in color)

    def draw_note(self, note):
        lx = self.lane_x(note.lane)
        color = LANE_COLORS[note.lane]
        if note.missed:
            color = self.dim(color)
        if note.is_hold:
            body_color = color if note.holding else self.dim(color, 0.6)
            pygame.draw.rect(self.screen, body_color, note.get_body_rect(lx), border_radius=8)
        head = note.get_rect(lx)
        pygame.draw.rect(self.screen, color, head, border_radius=5)
        if note.is_hold and note.holding:
            pygame.draw.rect(self.screen, (255, 255, 255), head, width=3, border_radius=5)

    def draw(self):
        self.screen.fill(BG)
        # Lane dividers
        for i in range(LANES + 1):
            pygame.draw.line(self.screen, (40, 40, 60), (i * LANE_W, 0), (i * LANE_W, HEIGHT), 1)

        # Notes (drawn under the hit pads)
        for note in self.notes:
            if not note.dead:
                self.draw_note(note)

        # Hit line
        pygame.draw.line(self.screen, (80, 80, 100), (0, HIT_Y), (WIDTH, HIT_Y), 2)
        for i in range(LANES):
            lx = self.lane_x(i)
            pygame.draw.rect(self.screen, LANE_COLORS[i],
                             pygame.Rect(lx - Note.WIDTH // 2, HIT_Y - 12, Note.WIDTH, 24), border_radius=6)
            lbl = self.font.render(LANE_LABELS[i], True, (20, 20, 20))
            self.screen.blit(lbl, (lx - lbl.get_width() // 2, HIT_Y - 10))

        # Feedback
        for text, color, ttl, x, y in self.feedback:
            surf = self.font.render(text, True, color)
            surf.set_alpha(min(255, ttl * 7))
            self.screen.blit(surf, (x - surf.get_width() // 2, y))

        # HUD (misses is right-aligned so it no longer runs off the window)
        sc = self.font.render(f"Score: {self.score}", True, (220, 220, 220))
        co = self.font.render(f"Combo: {self.combo}x", True, (255, 220, 80))
        mi = self.font.render(f"Misses: {self.misses}/{MAX_MISSES}", True, (220, 100, 100))
        self.screen.blit(sc, (10, 10))
        self.screen.blit(co, (10, 40))
        self.screen.blit(mi, (WIDTH - mi.get_width() - 10, 10))

        if self.game_over:
            self.draw_summary()
        pygame.display.flip()

    # ---- Task 4: grade summary screen
    def draw_summary(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 225))
        self.screen.blit(ov, (0, 0))

        title = self.big_font.render("GAME OVER", True, (220, 60, 60))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        y = 150
        for grade in GRADES + ["MISS"]:
            name = self.font.render(grade, True, GRADE_COLORS[grade])
            cnt = self.font.render(str(self.counts[grade]), True, (230, 230, 230))
            self.screen.blit(name, (110, y))
            self.screen.blit(cnt, (WIDTH - 110 - cnt.get_width(), y))
            y += 38

        pygame.draw.line(self.screen, (90, 90, 110), (100, y + 4), (WIDTH - 100, y + 4), 2)
        y += 20
        acc = self.big_font.render(f"{self.accuracy:.1f}%", True, (255, 255, 255))
        acc_lbl = self.font.render("Accuracy", True, (180, 180, 200))
        self.screen.blit(acc_lbl, (WIDTH // 2 - acc_lbl.get_width() // 2, y))
        self.screen.blit(acc, (WIDTH // 2 - acc.get_width() // 2, y + 30))
        y += 110

        for text in (f"Final Score: {self.score}", f"Max Combo: {self.max_combo}x"):
            s = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, y))
            y += 34

        restart = self.font.render("Press R to Restart", True, (160, 160, 160))
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, y + 25))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
