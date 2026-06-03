# JDW Billboarding

A library for parsing "billboard" format text into Jackdaw audio system commands.

## Overview

Billboard Notation is a domain-specific language for multi-track musical composition that extends [Shuttle Notation](https://github.com/estrandv/shuttle-notation-python) with organizational structure, effects, routing, and real-time control.

## Features

- **Multi-track sequencing**: Define multiple instruments playing simultaneously
- **Effect chains**: Per-section audio effects with parameters
- **Group filtering**: Selectively render instrument groups
- **Drone synthesis**: Continuous tones modulated by track data
- **Sampler support**: Sample playback with pad configurations
- **Real-time commands**: Dynamic control and configuration
- **Shuttle integration**: Full Shuttle Notation syntax for track content

## Documentation

- **[Billboard Specification](BILLBOARD_SPEC.md)**: Complete language specification
- **[Shuttle Notation Spec](https://github.com/estrandv/shuttle-notation-python)**: Base notation system

## Dependencies

- [shuttle-notation-python](https://github.com/estrandv/shuttle-notation-python)
- pythonosc

## Syntax Highlighting

- [VSCode Extension](https://github.com/estrandv/jdw-billboarding-vscode)

## Quick Example

```billboard
DEFAULT amp0.5,sus1.0

>>> drums bass keys

COMMAND /set_bpm 120

@moogBass:bass susT0.5,amp1
(c4:4 c4:4 bb3:4 a3:2 bb3:2):0.5
€reverb:space room0.9,mix0.4

*@SP_Roland808:drums ofs0,sus20,amp0.6 1:0 2:14 3:26
(14:1.5 14:0.5 x:1 14:1)*4
€clamp:limiter under4500,over20

@FMRhodes:keys chorus0.4,susT1.1
(c5:4 c5:4 bb4:4 a4:2 bb4:2):time0.5,sus8
```

## Installation

```bash
pip install -e .
```

## Usage

```python
from jdw_billboarding.lib.billboard_construction import parse_billboard

billboard_text = """
>>> melody
@synth:melody amp0.5
c4 d4 e4 f4
"""

billboard = parse_billboard(billboard_text)
```

## License

[Your license here]
