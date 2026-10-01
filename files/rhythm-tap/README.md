# Rhythm Tap

A 4-lane rhythm game — tap the right key as notes reach the hit line.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Lane |
|-----|------|
| D | Lane 1 |
| F | Lane 2 |
| J | Lane 3 |
| K | Lane 4 |
| R | Restart |

## Tasks to Complete

### Task 1: Sound Effects on Hit
> Play a short beep or drum sound on each PERFECT, GREAT, or OK hit.

**Done** - `game/sounds.py` synthesises a short beep per grade (PERFECT 1320 Hz, GREAT 990 Hz, OK 660 Hz), so no audio files are needed. If no audio device exists the game runs silently instead of crashing.



### Task 2: Hold Notes
> Add a long note type that the player must hold for 1 second to score.

**Done** - `HoldNote` in `game/beat.py`. Hit the head on time, then keep the key held for 1 second (the bar shrinks as you hold). It scores 2x the grade points when the hold completes; releasing early shows `DROPPED` and counts as a miss.



### Task 3: BPM-Synced Spawning
> Notes should spawn on exact beats of a given BPM (e.g., 120 BPM) instead of a timer.

**Done** - set `BPM` in `game/game_engine.py` (default 120). Each note is spawned early enough, based on its fall speed, to reach the hit line exactly on its beat.


### Task 4: Grade Summary Screen
> After game over, show a breakdown: PERFECT count, GREAT count, OK count, MISS count, accuracy %.

**Done** - accuracy = (PERFECT + GREAT + OK) / (hits + misses).

### Bugs fixed
- `Misses: x/15` HUD text ran off the right edge of the window (now right-aligned).
- Difficulty ramp (`frame % 600`) was nested inside the spawn block, so it almost never fired.
- Tapping an empty lane showed `MISS` but did not increase the Misses counter.
- A note was only marked missed 30px after it could no longer be hit.



## Folder Structure

```
rhythm-tap/
├── main.py
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   ├── beat.py
│   └── sounds.py
└── README.md
```

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history

