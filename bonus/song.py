from strauss.audio_figure import AudioFigure
import numpy as np
import pandas as pd
from paths import ROOT

af = AudioFigure()

BPM = 117           # Beats per minute
SPM = BPM * 4       # Sixteenth-notes per minute
N_16 = SPM + 1      # Total number of 16th notes in the data (add one so the last beat coincides with the end of audio)
duration = 60       # How long (in seconds) we want our sonification to be - kept as a minute for easy calculations above
a_big_number = 1000 # Used to repeat a pattern until the end of song

# Volume levels
mixer = {
    'kick': 0.3,
    'snare': 0.3,
    'hi-hat': 0.1,
    'bass': 0.3,
    'synth1': 0.15,
    'synth2': 0.15,
}

pan = {
    'hi-hat': 0.6,
    'synth1': 0.3,
    'synth2': 0.6
}

drums = pd.DataFrame(
    {
        'time': np.arange(1, 470),
        'kick': [1 if n%8 == 1 else 0 for n in range(1, N_16 + 1)], # Add one to the N_16 as we are starting at 1 instead of 0
        'hi-hat': [1 if n%2 == 1 else 0 for n in range(1, N_16 + 1)],
        'snare': [1 if n%8 == 5 else 0 for n in range(1, N_16 + 1)],
    }
)

# print(drums.head(50))
# print(drums.tail(50))

# Note patterns
bass_pattern = [3, None, 1, None, 2, None, 3, None, 2, None, 1, None, 0, None, 1, None]
synth_pattern = (
    [0] + [None] * 5 + [1] + [None] * 9 +
    [2] + [None] * 5 + [1] + [None] * 9
)

data = {
    'bass': {
        # Step 1 is silent anchor (0), steps 2-32 are None (rests), steps 33-469 play every odd step (eighth notes)
        'time': [1] + ([None] * 31) + [n if n % 2 == 1 else None for n in range(33, N_16 + 1)],
        'pitch': [0] + ([None] * 31) + (bass_pattern * a_big_number),
        'volume': [0] + ([1] * (N_16 - 1))
    },
    'synth1': {
        # Step 1 anchor + 95 silent steps (steps 2-96) + pattern starting cleanly on step 97
        'time': [1] + ([None] * 95) + [x if x % 16 in (1, 7) else None for x in range(97, N_16 + 1)],
        'pitch': ([0] + ([None] * 95) + (synth_pattern * a_big_number))[:N_16],
        'volume': [0] + ([1] * (N_16 - 1))
    },
    'synth2': {
            # Step 1 anchor + 95 silent steps (steps 2-96) + pattern starting cleanly on step 97
            'time': [1] + ([None] * 95) + [x if x % 16 in (1, 7) else None for x in range(97, N_16 + 1)],
            'pitch': ([0] + ([None] * 95) + (synth_pattern * a_big_number))[:N_16],
            'volume': [0] + ([1] * (N_16 - 1))
        }
}

for k, v in data.items():
    # Ensure arrays don't end with None
    if v['time'][-1] is None:
        v['time'][-1] = N_16
        v['pitch'][-1] = 0
        v['volume'][-1] = 0

    
for track in drums.columns:
    if track == 'time': continue 
    af.sonify(drums, style=f'./styles/{track}.yml', duration=duration, level=mixer[track], fix_pan=pan.get(track, 0.5))

for track in data.keys():
    args = [data[track][k] for k in data[track].keys()]
    af.sonify(*args, style=f'./styles/{track}.yml', duration=duration, level=mixer[track], fix_pan=pan.get(track, 0.5))
    
af.save('output.wav', master_volume=0.7)

