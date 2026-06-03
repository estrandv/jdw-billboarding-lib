# Billboard Notation Language Specification

**Version:** 1.0  
**Last Updated:** 2026-06-03

## Table of Contents

1. [Overview](#overview)
2. [Relationship to Shuttle Notation](#relationship-to-shuttle-notation)
3. [Lexical Structure](#lexical-structure)
4. [Line Types and Classification](#line-types-and-classification)
5. [Grammar](#grammar)
6. [Semantic Rules](#semantic-rules)
7. [Data Model](#data-model)
8. [Examples](#examples)
9. [Implementation Notes](#implementation-notes)

---

## Overview

Billboard Notation is a domain-specific language for defining multi-track musical compositions with effects, routing, and real-time control. It extends [Shuttle Notation](../shuttle-notation-python/LANGUAGE_SPEC.md) to provide:

- **Multi-track sequencing**: Multiple instruments playing simultaneously
- **Effect chains**: Per-section audio effects with parameters
- **Group filtering**: Selective rendering of instrument groups
- **Drone synthesis**: Continuous tones modulated by track data
- **Sampler support**: Sample playback with pad configurations
- **Real-time commands**: Dynamic control and configuration
- **Hierarchical organization**: Sections with shared properties

### Primary Use Case

Musical composition and live performance control for the Jackdaw audio system, but applicable to any multi-track sequential audio system.

### Core Features

1. **Synth Sections**: Instrument definitions with multiple tracks
2. **Track Definitions**: Shuttle notation sequences with group assignment
3. **Effect Definitions**: Audio processing chains per section
4. **Group Filters**: Control which sections render
5. **Commands**: System-level configuration and control
6. **Default Arguments**: Global parameter defaults
7. **Comments**: Documentation and temporary disabling

---

## Relationship to Shuttle Notation

Billboard builds on Shuttle Notation as its foundation:

- **Track content** is written in Shuttle Notation syntax
- **Arguments** use Shuttle's inheritance and operator system
- **Elements** resolve to `ResolvedElement` objects from Shuttle
- Billboard adds **organizational structure** around Shuttle sequences

Key differences:
- Billboard organizes multiple Shuttle sequences into sections
- Billboard adds audio-specific concepts (effects, routing, drones)
- Billboard provides filtering and command systems

---

## Lexical Structure

### Whitespace and Line Continuation

- **Newlines**: Primary line separator
- **Backslash continuation**: `\` at end of line continues to next line
- **Tabs and spaces**: Normalized to single spaces
- **Multiple spaces**: Collapsed to single space

### Comments

- **Symbol**: `#`
- **Scope**: From `#` to end of line
- **Placement**: Can appear at start of line or inline
- **Effect**: Line is ignored but structure is preserved for indexing

```
# This is a comment
@synth  # This is also a comment
#@synth  # This synth section is disabled
```

### Reserved Symbols

| Symbol | Purpose | Context |
|--------|---------|---------|
| `>>>` | Group filter header | Start of line |
| `@` | Synth section header | Start of line |
| `*@` | Selected synth header | Start of line |
| `€` | Effect definition | After synth header |
| `#` | Comment marker | Any position |
| `<>` | Track metadata | Start of track line |
| `:` | Argument separator | Throughout |
| `,` | Argument list separator | Throughout |
| `;` | Metadata separator | Inside `<>` |

### Keywords

- `DEFAULT` - Global default arguments statement
- `COMMAND` - Generic command (all contexts)
- `UPDATE_COMMAND` - Update-only command
- `QUEUE_COMMAND` - Queue-only command
- `SP_` - Sampler prefix for instruments
- `DR_` - Drone prefix for instruments

---

## Line Types and Classification

Billboard files are parsed line-by-line, with each line classified into one of these types:

### 1. Group Filter (`>>>`)

**Syntax**: `>>> <group_name> [<group_name> ...]`

**Purpose**: Controls which synth sections are rendered based on their group assignment.

**Rules**:
- Must start with `>>>`
- Followed by space-separated group names
- Only the first unbroken chain of filters is used
- Commented filters don't break the chain
- Empty group name matches sections without groups

**Example**:
```
>>> drums bass keys
>>> vocals  # This is ignored (not in first chain)
```

### 2. Synth Header (`@` or `*@`)

**Syntax**: `[@|*@]<instrument_name>[:<group_name>] [<default_args>] [<additional_config>]`

**Purpose**: Declares a new instrument section with tracks and effects.

**Components**:
- `@` - Normal synth header
- `*@` - Selected synth (keyboard configuration exported)
- `instrument_name` - Synth/sampler identifier
- `:group_name` - Optional group for filtering
- `default_args` - Shuttle notation arguments (inherited by all tracks)
- `additional_config` - Sampler pad configuration or other data

**Prefixes**:
- `SP_` - Sampler instrument (plays audio samples)
- `DR_` - Drone instrument (continuous tone modulated by tracks)

**Example**:
```
@moogBass:bass amp0.5,sus2.0
*@SP_Roland808:drums ofs0,sus20,amp0.6 1:0 2:14 3:26
@DR_aPad:ambient amp0.0,out90
```

### 3. Track Definition

**Syntax**: `[<metadata>] <shuttle_notation>`

**Purpose**: Defines a sequence of notes/events for the current synth section.

**Metadata Format**: `<group_override[;arg_override]>`
- `group_override` - Override section's group assignment
- `arg_override` - Additional arguments (with operators)

**Rules**:
- Only recognized after a synth header
- Each track gets a unique index (0, 1, 2, ...)
- Commented tracks still increment the index
- Empty lines are ignored
- Cannot use `€` notation with `<>` metadata

**Example**:
```
@synth:melody amp0.5
c4 d4 e4 f4
<harmony;amp*1.5> g4 a4 b4 c5
# This track is disabled but counts as index 2
<bass> c3 e3 g3
```

### 4. Effect Definition (`€`)

**Syntax**: `€<effect_type>:<unique_id> [<args>]`

**Purpose**: Adds an audio effect to the current synth section.

**Components**:
- `effect_type` - Effect algorithm name (e.g., `reverb`, `delay`)
- `unique_id` - Identifier for this effect instance
- `args` - Effect parameters in Shuttle notation format

**Rules**:
- Must appear after synth header, before next header
- Each effect needs a unique ID within its section
- External ID format: `effect_<group>_<unique_id>`

**Example**:
```
@synth:keys
c4 d4 e4
€reverb:main room0.9,mix0.5
€delay:echo time0.25,feedback0.3
```

### 5. Command

**Syntax**: `[COMMAND_TYPE] <address> [<args>...]`

**Purpose**: System-level configuration and control messages.

**Command Types**:
- `COMMAND` - Applies to all contexts (default)
- `UPDATE_COMMAND` - Only for update operations
- `QUEUE_COMMAND` - Only for queue operations

**Common Commands**:
- `/set_bpm <bpm>` - Set tempo
- `/set_scale <root> <type> <octave>` - Set scale for note resolution
- `/transpose <steps>` - Transpose all notes by semitones

**Example**:
```
COMMAND /set_bpm 120
UPDATE_COMMAND /set_scale c maj 4
QUEUE_COMMAND /transpose 5
```

### 6. Default Statement

**Syntax**: `DEFAULT <args>`

**Purpose**: Sets global default arguments for all tracks.

**Rules**:
- Only the last `DEFAULT` statement is used
- Arguments are overridden by synth header arguments
- Uses Shuttle notation argument format

**Example**:
```
DEFAULT amp0.5,sus1.0,time0.5
```

### 7. Comment

**Syntax**: `# <text>`

**Purpose**: Documentation or disabled content.

**Rules**:
- Pure comment lines (no other content)
- Preserved in parsing for structure
- Not processed semantically

---

## Grammar

### EBNF Notation

```ebnf
(* Top-level *)
billboard         = line { newline line } ;

line              = group_filter
                  | synth_header
                  | track_definition
                  | effect_definition
                  | command
                  | default_statement
                  | comment
                  | empty ;

(* Line Types *)
group_filter      = ">>>" whitespace group_name { whitespace group_name } ;

synth_header      = [ "*" ] "@" synth_spec [ whitespace default_args ] [ whitespace additional_config ] ;

synth_spec        = [ prefix ] instrument_name [ ":" group_name ] ;

prefix            = "SP_" | "DR_" ;

track_definition  = [ track_metadata ] shuttle_sequence ;

track_metadata    = "<" group_override [ ";" arg_override ] ">" ;

effect_definition = "€" effect_type ":" unique_id [ whitespace args ] ;

command           = [ command_type whitespace ] address { whitespace arg } ;

command_type      = "COMMAND" | "UPDATE_COMMAND" | "QUEUE_COMMAND" ;

default_statement = "DEFAULT" whitespace args ;

comment           = "#" { any_character } ;

(* Shuttle Integration *)
shuttle_sequence  = (* See Shuttle Notation spec *) ;

args              = (* Shuttle notation args format *) ;

(* Primitives *)
instrument_name   = identifier ;
group_name        = identifier ;
effect_type       = identifier ;
unique_id         = identifier ;
address           = "/" identifier ;
arg               = identifier | number ;
identifier        = letter { letter | digit | "_" } ;
number            = [ "-" ] digit { digit } [ "." digit { digit } ] ;
whitespace        = " " | "\t" ;
newline           = "\n" | "\r\n" ;
```

### Precedence and Structure

1. **File level**: Lines processed sequentially
2. **Filter chain**: Only first unbroken sequence of filters used
3. **Section scope**: Synth header starts new section
4. **Track indexing**: Sequential within section (includes commented)
5. **Argument inheritance**: DEFAULT → Synth Header → Track Metadata → Shuttle Elements

---

## Semantic Rules

### Section Processing

Each synth section is processed independently:

1. **Parse header** - Extract instrument, group, defaults
2. **Collect tracks** - Parse Shuttle sequences with metadata
3. **Collect effects** - Parse effect definitions
4. **Create drones** - If `DR_` prefix, create effect per track
5. **Resolve elements** - Convert Shuttle to `ElementMessage` objects
6. **Apply filtering** - Check if section's group is in active filters

### Track Resolution

Tracks are resolved through multiple stages:

1. **Combine defaults**: `DEFAULT` + synth header args
2. **Parse Shuttle**: Convert track content to `ResolvedElement[]`
3. **Apply metadata**: Override group and apply arg operators
4. **Convert to messages**: Create `ElementMessage` with routing info

### Argument Inheritance Chain

Arguments flow through multiple levels:

```
DEFAULT args
  ↓ (overridden by)
Synth Header args
  ↓ (overridden by)
Track Metadata args
  ↓ (overridden by)
Shuttle Section args
  ↓ (overridden by)
Shuttle Element args
```

### Argument Override Operators

Track metadata can use operators to modify inherited values:

- `=` or no operator: Set value
- `+`: Add to inherited value
- `-`: Subtract from inherited value
- `*`: Multiply inherited value

**Example**:
```
@synth amp0.5
c4 d4                    # amp=0.5
<;amp+0.2> e4 f4        # amp=0.7
<;amp*2> g4 a4          # amp=1.0
```

### Group Filtering

Sections are included in output if:

1. No filters are defined (all sections included), OR
2. Section's group appears in any filter line, OR
3. Section has no group and empty string is in filters

**Example**:
```
>>> drums bass
>>> keys

@synth:drums    # Included (drums in filter)
@synth:bass     # Included (bass in filter)
@synth:keys     # Included (keys in filter)
@synth:vocals   # Excluded (vocals not in filter)
@synth          # Excluded (no group, "" not in filter)
```

### Drone Behavior

Sections with `DR_` prefix create continuous tones:

1. One effect (drone) created per track
2. Track elements send modulation messages to drone
3. Drone external ID: `effect_<group>_<track_index>`
4. Amp is forced to 0 on creation (set during playback)

### Sampler Configuration

Sections with `SP_` prefix play audio samples:

1. `additional_config` defines pad mappings
2. Format: `<index>:<sample_id> ...` (Shuttle notation)
3. Selected samplers (`*@SP_`) export keyboard config
4. Elements reference sample IDs via index

**Example**:
```
*@SP_Roland808:drums 1:0 2:14 3:26 4:32
14 14 26 32    # Plays samples 14, 14, 26, 32
```

### Command Processing

Commands are collected and applied:

1. **Parse time**: `/set_scale`, `/transpose` affect element resolution
2. **Runtime**: Other commands sent to audio system
3. **Context filtering**: Commands filtered by `COMMAND_TYPE`

### Track Naming

Tracks are assigned unique names:

**Format**: `<instrument>_<group>_<index>`

**Example**:
```
@moogBass:melody
c4 d4        # Track: moogBass_melody_0
e4 f4        # Track: moogBass_melody_1
```

### Effect Naming

Effects are assigned external IDs:

**Format**: `effect_<group>_<unique_id>`

**Example**:
```
@synth:keys
€reverb:main    # ID: effect_keys_main
€delay:echo     # ID: effect_keys_echo
```

---

## Data Model

### Core Classes

#### BillboardLine
```python
@dataclass
class BillboardLine:
    content: str              # Raw line content
    type: BillboardLineType   # Classification
```

#### BillboardLineType (Enum)
```python
class BillboardLineType(Enum):
    COMMENT = 0
    GROUP_FILTER = 1
    SYNTH_HEADER = 2
    TRACK_DEFINITION = 3
    EFFECT_DEFINITION = 4
    COMMAND = 5
    DEFAULT_STATEMENT = 6
```

#### SynthHeader
```python
@dataclass
class SynthHeader:
    instrument_name: str
    is_drone: bool
    is_sampler: bool
    is_selected: bool
    default_args_string: str
    additional_args_string: str
    group_name: str
```

#### TrackDefinition
```python
@dataclass
class TrackDefinition:
    content: str              # Shuttle notation
    group_override: str
    arg_override: str
    index: int                # Sequential track number
```

#### EffectDefinition
```python
@dataclass
class EffectDefinition:
    instrument_name: str      # Effect type
    unique_suffix: str        # Unique ID
    args_string: str          # Effect parameters
```

#### SynthSection
```python
@dataclass
class SynthSection:
    header: SynthHeader
    tracks: list[TrackDefinition]
    effects: list[EffectDefinition]
```

#### BillboardCommand
```python
@dataclass
class BillboardCommand:
    address: str              # Command path (e.g., "/set_bpm")
    context: CommandContext   # When to apply
    args: list[str]           # Command arguments
```

#### CommandContext (Enum)
```python
class CommandContext(Enum):
    ALL = 0
    UPDATE = 1
    QUEUE = 2
```

#### Billboard
```python
@dataclass
class Billboard:
    sections: list[BillboardSynthSection]
    filters: list[list[str]]
    commands: list[BillboardCommand]
```

---

## Examples

### Basic Multi-Track Composition

```
DEFAULT amp0.5,sus1.0

>>> melody bass

@moogBass:melody
c4 d4 e4 f4
g4 a4 b4 c5

@eBass:bass
c3 c3 g3 g3
```

### With Effects

```
@synth:keys amp0.7
c4 e4 g4 c5
€reverb:main room0.9,mix0.5
€delay:echo time0.25,feedback0.3
```

### Track Metadata Override

```
@synth:melody amp0.5
c4 d4 e4 f4
<harmony;amp*1.5> g4 a4 b4 c5
<bass;amp*0.8> c3 e3 g3 c4
```

### Sampler with Pads

```
*@SP_Roland808:drums ofs0,sus20,amp0.6 1:0 2:14 3:26 4:32
14 14 26 32
14 26 14 32
```

### Drone Synthesis

```
@DR_aPad:ambient amp0.0,out90
(c5 e5 g5):amp0.7,gate1
€reverb:a room0.9,mix0.35
```

### Commands and Scale

```
COMMAND /set_bpm 120
COMMAND /set_scale c maj 4
UPDATE_COMMAND /transpose 5

@synth:melody
c4 d4 e4 f4    # Will be transposed +5 semitones
```

### Line Continuation

```
@synth:melody
(c4 d4 e4 f4 \
 g4 a4 b4 c5):amp0.5,sus2.0
```

### Complex Example

```
DEFAULT amp0.5,sus1.0,time0.5

>>> drums bass keys

COMMAND /set_bpm 120
COMMAND /set_scale c maj 4

*@SP_Roland808:drums ofs0,sus20,amp0.6 1:0 2:14 3:26
(14:1.5 14:0.5 x:1 14:1)*4
€reverb:main room0.4,mix0.25
€clamp:limiter under4500,over20

@moogBass:bass susT0.5,sus0.01,amp1
(c4:4 c4:4 bb3:4 a3:2 bb3:2):0.5
€delay:echo echo0.25,echt4
€reverb:space room0.9,mix0.4

@FMRhodes:keys chorus0.4,susT1.1
(c5:4 c5:4 bb4:4 a4:2 bb4:2):time0.5,sus8
<harmony;amp*0.8> (e5 g5 c6 e6):sus4.0
€clamp:soft under1900,over140
```

---

## Implementation Notes

### Parser Architecture

The reference implementation uses a multi-stage parser:

1. **Line Classification** (`line_classify.py`): Categorize each line by type
2. **Filtering** (`filtering.py`): Extract filters, commands, defaults
3. **Section Parsing** (`parsing.py`): Parse synth headers, tracks, effects
4. **Billboard Construction** (`billboard_construction.py`): Build final structure
5. **Shuttle Integration**: Delegate to Shuttle parser for track content

### Parsing Stages Detail

**Stage 1: Line Classification**
- Split by newlines (handling `\` continuation)
- Normalize whitespace
- Classify each line by leading symbols
- Preserve commented lines for structure

**Stage 2: Filtering and Extraction**
- Extract first unbroken chain of group filters
- Find last `DEFAULT` statement
- Collect all command lines
- Group lines by synth sections

**Stage 3: Section Parsing**
- Parse synth header (instrument, group, args)
- Parse each track (content, metadata, index)
- Parse each effect (type, ID, args)
- Build `SynthSection` objects

**Stage 4: Billboard Construction**
- Process each section with defaults
- Resolve Shuttle sequences to elements
- Apply metadata overrides
- Create effects and drones
- Build final `Billboard` object

**Stage 5: Element Conversion**
- Convert `ResolvedElement` to `ElementMessage`
- Apply scale and transposition
- Route to appropriate instrument/effect
- Generate OSC messages for audio system

### Key Functions

- `classify_lines()` - Line type detection
- `extract_group_filters()` - Filter chain extraction
- `extract_synth_chunks()` - Section grouping
- `parse_synth_header()` - Header parsing
- `parse_track_definition()` - Track parsing with metadata
- `parse_effect_definition()` - Effect parsing
- `parse_track()` - Shuttle integration
- `process_synth_section()` - Section to messages
- `parse_billboard()` - Main entry point

### Edge Cases

1. **Empty sections**: Valid, produces no tracks
2. **Commented tracks**: Count toward index but don't render
3. **No filters**: All sections included
4. **Empty group name**: Matches sections without groups
5. **Duplicate effect IDs**: Last one wins (implementation-defined)
6. **Invalid Shuttle syntax**: Propagates Shuttle parser errors
7. **Missing group in filter**: Section excluded
8. **Multiple DEFAULT**: Last one used

### Tree-Sitter Considerations

For implementing a tree-sitter grammar:

1. **Line-based parsing**: Each line is independent unit
2. **Context sensitivity**: Track lines only valid after synth header
3. **Shuttle delegation**: Track content is opaque Shuttle syntax
4. **Comment handling**: Can appear on any line
5. **Whitespace significance**: Space separates tokens
6. **Continuation**: Backslash-newline is single token

### Extension Points

The language is designed to be extensible:

1. **New line types**: Add to `BillboardLineType` enum
2. **New command types**: Add to command parsing
3. **New prefixes**: Extend `SP_`, `DR_` pattern
4. **Additional metadata**: Extend `<>` syntax
5. **Custom effects**: Effect types are open-ended
6. **Shuttle extensions**: Inherits Shuttle extensibility

---

## Formal Grammar Summary

For quick reference, the core grammar in compact form:

```
billboard    ::= line*
line         ::= filter | header | track | effect | command | default | comment
filter       ::= '>>>' name+
header       ::= ['*'] '@' [prefix] name [':' group] [args] [config]
prefix       ::= 'SP_' | 'DR_'
track        ::= ['<' group [';' args] '>'] shuttle_sequence
effect       ::= '€' type ':' id [args]
command      ::= [cmd_type] address arg*
cmd_type     ::= 'COMMAND' | 'UPDATE_COMMAND' | 'QUEUE_COMMAND'
default      ::= 'DEFAULT' args
comment      ::= '#' text
shuttle_seq  ::= (* See Shuttle Notation spec *)
```

---

## Version History

- **1.0** (2026-06-03): Initial specification based on reference implementation

---

## References

- Shuttle Notation Spec: `../shuttle-notation-python/LANGUAGE_SPEC.md`
- Reference Implementation: `jdw_billboarding/lib/`
- Test Suite: `jdw_billboarding/tests/` (if exists)
- VSCode Extension: https://github.com/estrandv/jdw-billboarding-vscode

---

## Appendix: Common Patterns

### Pattern: Layered Melody

```
@synth:melody amp0.5
c4 d4 e4 f4
<harmony;amp*0.7> e4 g4 b4 e5
<bass;amp*0.9> c3 c3 g3 g3
```

### Pattern: Alternating Drums

```
@SP_drums:rhythm
(14 / 26)*8        # Kick / Snare alternating
(x:2 95:1 x:1)*4   # Hi-hat pattern
```

### Pattern: Effect Chain

```
@synth:pad
(c4 e4 g4):sus8.0
€reverb:space room0.9,mix0.5
€delay:echo time0.5,feedback0.4
€clamp:limit under2000,over100
```

### Pattern: Dynamic Filtering

```
>>> intro
# ... intro sections ...

>>> verse
# ... verse sections ...

>>> chorus
# ... chorus sections ...
```

### Pattern: Drone with Modulation

```
@DR_pad:ambient amp0.0,out90
(c5:0,sus4 e5:1 g5:2):amp0.7,gate1
€reverb:space room0.9,mix0.35
```
