from __future__ import annotations

import json
from pathlib import Path


LEVELS = [
    {
        "filename": "level_01_core_intro.json",
        "id": 1,
        "name": "Core Platform",
        "difficulty": 1,
        "description": "A Bloxorz-style platform level. Expected shortest solution length: 11 moves.",
        "grid": [
            "################",
            "################",
            "##S.....########",
            "##......########",
            "##..........####",
            "#######......###",
            "#######..G...###",
            "#######......###",
            "################",
            "################",
        ],
    },
    {
        "filename": "level_02_core_turning.json",
        "id": 2,
        "name": "Narrow Left Turn",
        "difficulty": 2,
        "description": "A narrow turning route that requires careful orientation changes. Shortest: 15 moves.",
        "grid": [
            "##############",
            "##############",
            "##...#########",
            "##...#########",
            "##G#.#########",
            "##...#########",
            "##...#########",
            "##.#....######",
            "##...##.....##",
            "##...##....S##",
            "#########...##",
            "##############",
            "##############",
        ],
    },
    {
        "filename": "level_03_core_voids.json",
        "id": 3,
        "name": "Vertical Gate",
        "difficulty": 3,
        "description": "A route with vertical gates and narrow safe areas. Shortest: 16 moves.",
        "grid": [
            "############",
            "############",
            "#######...##",
            "#####.....##",
            "#####...####",
            "#####.#.####",
            "#####.#.####",
            "#####.#.####",
            "###...#.####",
            "##S..##G####",
            "############",
            "############",
        ],
    },
    {
        "filename": "level_04_core_maze.json",
        "id": 4,
        "name": "Long Ledge",
        "difficulty": 4,
        "description": "A long ledge level with several falling risks. Shortest: 19 moves.",
        "grid": [
            "#####################",
            "#####################",
            "#########......######",
            "#########..###..#####",
            "######.....###..#####",
            "##G.....#######...###",
            "################..###",
            "################..###",
            "################..S##",
            "#####################",
            "#####################",
        ],
    },
    {
        "filename": "level_05_core_broken_causeway.json",
        "id": 5,
        "name": "Broken Causeway",
        "difficulty": 5,
        "description": "A broken causeway with several direction changes. Shortest: 25 moves.",
        "grid": [
            "#####################",
            "#####################",
            "#######...###########",
            "##S.......###########",
            "#####..##.###########",
            "#####..##...#########",
            "#########...#########",
            "#########....###G####",
            "#########....###.####",
            "############...#.####",
            "#############......##",
            "################...##",
            "################...##",
            "#####################",
            "#####################",
        ],
    },
    {
        "filename": "level_06_core_spiral_descent.json",
        "id": 6,
        "name": "Spiral Descent",
        "difficulty": 6,
        "description": "A winding route with a distant goal. Shortest: 25 moves.",
        "grid": [
            "###################",
            "###################",
            "##############...##",
            "##############...##",
            "##############.#S##",
            "##############.####",
            "##############.####",
            "########.......####",
            "#######...###..####",
            "#######.#####..####",
            "##G#......#########",
            "##...##...#########",
            "##...##############",
            "###################",
            "###################",
        ],
    },
    {
        "filename": "level_07_core_island_maze.json",
        "id": 7,
        "name": "Island Maze",
        "difficulty": 7,
        "description": "A larger island-like maze with dead ends. Shortest: 29 moves.",
        "grid": [
            "######################",
            "######################",
            "################S...##",
            "################....##",
            "################....##",
            "##################..##",
            "##################..##",
            "###################.##",
            "###############.....##",
            "##.........####.....##",
            "##......#.......######",
            "##G##...###..#########",
            "###########..#########",
            "######################",
            "######################",
        ],
    },
    {
        "filename": "level_08_core_deep_zigzag.json",
        "id": 8,
        "name": "Deep Zigzag",
        "difficulty": 8,
        "description": "A deep zigzag route designed for solver testing. Shortest: 36 moves.",
        "grid": [
            "##################",
            "##################",
            "#####...##########",
            "#####...##########",
            "###...#.##########",
            "###..##...########",
            "###..##...########",
            "##S..##...########",
            "#######..#########",
            "#######...########",
            "#########.########",
            "#########.####G###",
            "#########.###..###",
            "#########.###..###",
            "#########.###.####",
            "#########.....####",
            "#########..##.####",
            "#########..##...##",
            "#############...##",
            "##################",
            "##################",
        ],
    },
    {
        "filename": "level_09_core_dense_labyrinth.json",
        "id": 9,
        "name": "Dense Labyrinth",
        "difficulty": 9,
        "description": "Dense corridors with many orientation traps. Shortest: 36 moves.",
        "grid": [
            "##############",
            "##############",
            "######...#####",
            "######...#####",
            "#####..#######",
            "#####..#######",
            "##G##S.#######",
            "##.###.#######",
            "##.###.#######",
            "##.###..######",
            "##.###.....###",
            "##.####....###",
            "##.#######.###",
            "##.#####....##",
            "##.##....#..##",
            "##.......#..##",
            "###......#####",
            "###...########",
            "##############",
            "##############",
        ],
    },
    {
        "filename": "level_10_core_final_challenge.json",
        "id": 10,
        "name": "Final Core Challenge",
        "difficulty": 10,
        "description": "The hardest core-only level in this set. Shortest: 40 moves.",
        "grid": [
            "#####################",
            "#####################",
            "#################G###",
            "#################..##",
            "####....#########..##",
            "####....########...##",
            "####.##....S####..###",
            "##......##..#.....###",
            "##...#......#..######",
            "##...#..##.....######",
            "######..#############",
            "######..#############",
            "######..#############",
            "####....#############",
            "####...##############",
            "#####################",
            "#####################",
        ],
    },
]


LEGEND = {
    "#": "void",
    ".": "floor",
    "S": "start",
    "G": "goal",
}


def validate_level(level: dict) -> None:
    grid = level["grid"]

    row_lengths = {len(row) for row in grid}
    if len(row_lengths) != 1:
        raise ValueError(f"{level['filename']} has non-rectangular rows: {row_lengths}")

    start_count = sum(row.count("S") for row in grid)
    goal_count = sum(row.count("G") for row in grid)

    if start_count != 1:
        raise ValueError(f"{level['filename']} must have exactly one S, found {start_count}")

    if goal_count != 1:
        raise ValueError(f"{level['filename']} must have exactly one G, found {goal_count}")


def main() -> None:
    source_root = Path(__file__).resolve().parents[1]
    levels_dir = source_root / "levels"
    levels_dir.mkdir(parents=True, exist_ok=True)

    # Xóa các level cũ để tránh app load dư file.
    for old_file in levels_dir.glob("level_*.json"):
        old_file.unlink()

    for level in LEVELS:
        validate_level(level)

        data = {
            "id": level["id"],
            "name": level["name"],
            "difficulty": level["difficulty"],
            "category": "core",
            "description": level["description"],
            "grid": level["grid"],
            "legend": LEGEND,
            "bridges": [],
            "switches": [],
            "split": None,
        }

        output_path = levels_dir / level["filename"]

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        print(f"Wrote {output_path}")

    print("Done. 10 core levels generated successfully.")


if __name__ == "__main__":
    main()