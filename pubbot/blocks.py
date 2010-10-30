# Copyright 2010 John Carr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Data on block ids: What tool to mine with, how much damage they can take etc

blocks = {
    # Shovel
    0x03: {
        "name": "sand",
        "preferred_tool": 0x115,
        "times": {
            0x00: 1.05,
            0x10d: 0.7,
            0x111: 0.49,
            0x100: 0.44,
            0x115: 0.39,
            }
        },
    0x0C: {
        "name": "sand",
        "preferred_tool": 0x115,
        "times": {
            0x00: 1.05,
            0x10d: 0.7,
            0x111: 0.49,
            0x100: 0.44,
            0x115: 0.39,
            }
        },
    0x0D: {
        "name": "gravel",
        "preferred_tool": 0x115,
        "times": {
            0x00: 1.19,
            0x10d: 0.74,
            0x111: 0.54,
            0x100: 0.44,
            0x115: 0.39,
            }
        },

    # Pickaxes
    0x01: {
        "name": "stone",
        "preferred_tool": 0x116,
        "times": {
            0x00: 7.68,
            0x10e: 1.44,
            0x112: 0.89,
            0x101: 0.68,
            0x116: 0.59,
            }
        },
    0x04: {
        "name": "cobblestone",
        "preferred_tool": 0x116,
        "times": {
            0x00: 10.19,
            0x10e: 1.79,
            0x112: 1.04,
            0x101: 0.79,
            0x116: 0.68,
            }
        },
    0x10: {
        "name": "coal ore",
        "preferred_tool": 0x116,
        "times": {
            0x00: 15.22,
            0x10e: 2.54,
            0x112: 1.44,
            0x101: 1.04,
            0x116: 0.89,
            }
        },
    0x0f: {
        "name": "iron ore",
        "preferred_tool": 0x116,
        "times": {
            0x00: 15.22,
            0x10e: 15.22,
            0x112: 1.44,
            0x101: 1.04,
            0x116: 0.89,
            }
        },
    0x0e: {
        "name": "gold ore",
        "preferred_tool": 0x116,
        "times": {
            0x00: 15.22,
            0x10e: 15.22,
            0x112: 15.22,
            0x101: 1.04,
            0x116: 0.89,
            }
        },
    0x38: {
        "name": "diamond ore",
        "preferred_tool": 0x116,
        "times": {
            0x00: 15.22,
            0x10e: 15.22,
            0x112: 15.22,
            0x101: 1.04,
            0x116: 0.89,
            }
        },
    0x2A: {
        "name": "iron block",
        "preferred_tool": 0x116,
        "times": {
            0x00: 25.28,
            0x10e: 25.28,
            0x112: 2.19,
            0x101: 1.54,
            0x116: 1.24,
            }
        },
    0x29: {
        "name": "gold block",
        "preferred_tool": 0x116,
        "times": {
            0x00: 15.22,
            0x10e: 15.22,
            0x112: 15.22,
            0x101: 1.54,
            0x116: 1.24,
            }
        },
    0x39: {
        "name": "diamond block",
        "preferred_tool": 0x116,
        "times": {
            0x00: 25.28,
            0x10e: 25.28,
            0x112: 25.28,
            0x101: 1.54,
            0x116: 1.24,
            }
        },
    0x31: {
        "name": "obsidian",
        "preferred_tool": 0x116,
        "times": {
            0x00: 50.29,
            0x10e: 50.29,
            0x112: 50.29,
            0x101: 50.29,
            0x116: 15.35,
            }
        },
    0x35: {
        "name": "stairs",
        "preferred_tool": 0x116,
        "times": {
            0x00: 10.26,
            0x10e: 1.79,
            0x112: 1.04,
            0x101: 0.79,
            0x116: 0.68,
            }
        },
    0x3D: {
        "name": "furnace",
        "preferred_tool": 0x116,
        "times": {
            0x00: 17.67,
            0x10e: 5.52,
            0x112: 5.52,
            0x101: 5.52,
            0x116: 5.52,
            }
        },

    # Axe
    0x11: {
        "name": "log",
        "preferred_tool": 0x117,
        "times": {
            0x00: 3.34,
            0x10f: 1.79,
            0x113: 1.04,
            0x102: 0.79,
            0x117: 0.68,
            }
        },
    0x05: {
        "name": "wood",
        "preferred_tool": 0x117,
        "times": {
            0x00: 3.34,
            0x10f: 1.04,
            0x113: 1.04,
            0x102: 0.79,
            0x117: 0.68,
            }
        },
    0x3A: {
        "name": "workbench",
        "preferred_tool": 0x117,
        "times": {
            0x00: 4.06,
            0x10f: 4.06,
            0x113: 4.06,
            0x102: 4.06,
            0x117: 4.06,
            }
        },
    0x36: {
        "name": "chest",
        "preferred_tool": 0x117,
        "times": {
            0x00: 4.06,
            0x10f: 2.15,
            0x113: 1.21,
            0x102: 0.91,
            0x117: 0.76,
            }
        },

    # Weapons
    0x14: {
        "name": "glass",
        "preferred_tool": 0x114,
        "times": {
            0x00: 0.74,
            0x10c: 0.58,
            0x110: 0.58,
            0x10b: 0.58,
            0x114: 0.58,
            }
        },
    0x12: {
        "name": "leaves",
        "preferred_tool": 0x114,
        "times": {
            0x00: 0.59,
            0x10c: 0.5,
            0x110: 0.5,
            0x10b: 0.5,
            0x114: 0.5,
            }
        },
    }

