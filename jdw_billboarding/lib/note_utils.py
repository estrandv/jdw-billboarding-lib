from decimal import Decimal


"""

    Chords are most easily done dynamically; each "maj7" chord is the same distances but in a different scale.

    A chord is a progression of distances and not a set of notes.

    So you would take a chromatic set of notes, a starting note, and the steps needed by index.

    CMAJ is notes 0, 2, 4 (c, e, g).
        - Resolve the starting note. Ignore the value of the index (no distance), but use it as your starting point.
        - We now have index 0 in the array, from "c": 0.
        - MAJ chords use notes 0, 2 and 4 in their scale, so we determine the distances for these notes:
                - index2=dist2, index4=dist2(4)
                - 0+2 = 2, 2+2 = 4
                => 0, 2, 4

"""

"""

    NEXT CHALLENGE: REFACTORING

    This note mapping is only used to resolve frequencies, assuming notes to already be given.
        - A mod message will never make any use of additional notes, but can handle the redundancy by grabbing the first index.
        - We're mainly concerned with returning additional notes for NOTE_ON and NOTE_ON_TIMED, so those will need to return lists instead
            of singular messages and do some additional logic for the timing of the chord notes
        - Resolving frequency can comfortably return an array, which we then know how to handle in callers.

    Starting point:
        - We need to harmonize letter-to-midid with chord resolution, so that we always get a list of notes
            even for the singulars, and tinker with the distinction between is_chord() in here and nowhere else.


"""

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

# Steps per progression per scale (looping)
MAJOR_SCALE: list[int] = [1, 2, 2, 1, 2, 2, 2]
# The "0" in chords is not really important - so we just list the other parts
MAJ_CHORD: list[int] = [2, 4]

def get_chord(base_note: str, scale: list[int], chord_progression: list[int]) -> list[int]:

    base_midi = note_letter_to_midi(base_note)

    if base_midi == -1:
        return []

    notes: list[int] = [base_midi]
    final_index = len(scale) - 1
    for dist_index in chord_progression:


        octave: int = 0 # Oct is zero-indexed; "1" means "+1"

        # Determine how far to look ahead in the scale using the listed distance
        search_index = notes[-1] + dist_index
        divide: float = search_index / final_index

        # 13 / 12 = 1.083
        # 13 / 13 = 1
        # 12 / 13 = 0.9
        # 24 / 12 = 2

        if divide > 1:
            # Handle cases where the calculated distance overshoots the base scale and goes into next octave
            index = search_index % final_index
            octave: int = int(divide) # int() rounds down to nearest whole.
            # TODO: Not sure if octave bumping is affected by scales; e.g. is "note 1 in next octave" always a +12 for every scale?
            notes.append(scale[index] + (octave * 12)) # Assuming 12 notes per octave
        else:
            # Does fit in scale
            notes.append(scale[search_index])

    return notes


def note_letter_to_midi(note_string: str) -> int:

    if note_string in MIDI_MAP:
        return MIDI_MAP[note_string]
    else:
        return -1
