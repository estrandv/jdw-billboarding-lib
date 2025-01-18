from decimal import Decimal


"""

    A scale is a set of midi-notes that the scale includes.

    Let's say we have scale MEEP: [0 2 3 5 11]

    We play note 0, which is MEEP[0] = 0

    But then comes overshoot: what is note 23?
    - Operate on len(MEEP) - 1 = 4 (max index)
    - 23 % 4 = 3 (this is our actual index)
    - 23 / 4 = 5.75, but rounded downward with int(n) we get 5 (octave boost)
    - There are 11 indices in a full scale
        - c1=0, b1=11, c2=12
        - C#1=1, C#2 = 13
        - So to add a full octave to any given note, we do +12

    - Needed extra arguments:
        - Scale name: e.g. "cmaj", or if using math: "c" and "maj"
        - Starting octave: an additional octave boost, so as to remove the need for arbitrary high numbers

    SCALE MATH
    - Each scale is just a set of distances on a chromatic scale
    - So CMAJ is C(0), D(+2), E(+2), F(+1), G(+2), A(+2), B(+2)
    - Given "e maj":
        - 0 = e
        - 2 = f#
        - 4 = g#
        - 5 = a
        - 7 = b
        - 9 = (looparound) c#2
        - 11 = d#2
    - ... but the looparound doesn't really apply, since D#1 is also part of the sale
    - Steps:
        - Determine letter chromatic index: e=4
        - Gather array by adding distances to root note, implicitly including root note as index 0: [4, 6, 8, 9, 11, 13, 15]
        - Resolve on chromatic scale using modulus of 11 (lenth of chroma scale): [4, 6, 8, 9, 11, 1, 3]
        - Sort the resulting array: [1,3,4,6,8,9,11]
        => Now you have your scale

    META STEPS
    1. Construct the scale array
    2. Resolve notes on the scale

"""

def _generate_scale(root_note: int, scale_type_key: str) -> list[int]:
    scale_distances = SCALE_MATH[scale_type_key] if scale_type_key in SCALE_MATH else SCALE_MATH["maj"]

    raw_scale_indices: list[int] = [root_note]
    index_step = root_note
    for dis in scale_distances:
        index_step += dis
        raw_scale_indices.append(index_step)

    chromatic_indices = [i % 11 for i in raw_scale_indices] # 11 = length -1 of chroma scale
    # Duplicates are possible
    return sorted(list(set(chromatic_indices)))

# Note_id: typically the index of your note; "I want to play note 22 in c maj7"
def resolve_index(note_id: int, scale_root_letter: str, scale_type_key: str) -> int:
    root_note = MIDI_MAP[scale_root_letter] if scale_root_letter in MIDI_MAP else 0
    my_scale = _generate_scale(root_note, scale_type_key)
    scale_indices = len(my_scale) - 1
    raw_scaled_index = my_scale[note_id % scale_indices]
    added_octaves = int(note_id / scale_indices)
    added_value = (12 * added_octaves)
    return raw_scaled_index + added_value

# https://stackoverflow.com/questions/13926280/musical-note-string-c-4-f-3-etc-to-midi-note-value-in-python
# [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
MIDI_MAP: dict[str, int] = {
    "c": 0,
    "c#": 1,
    "db": 1,
    "d": 2,
    "d#": 3,
    "eb": 3,
    "e": 4,
    "f": 5,
    "f#": 6,
    "gb": 6,
    "g": 7,
    "g#": 8,
    "ab": 8,
    "a": 9,
    "a#": 10,
    "bb": 10,
    "b": 11
}

SCALE_MATH: dict[str, list[int]] = {
    "maj": [2, 2, 1, 2, 2, 2] # 0=c is implicit
}

SCALES: dict[str, list[int]] = {
    "cmaj": [0,2,4,5,7,9,11]
}


def note_letter_to_midi(note_string: str) -> int:

    if note_string in MIDI_MAP:
        return MIDI_MAP[note_string]
    else:
        return -1
