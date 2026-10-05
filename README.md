# learning-games

Educational games for students, built from the Egyptian curriculum. Each game teaches part of a textbook with short study cards, then quizzes the student after every section.

Live: https://elarabyelaidy19.github.io/learning-games/

## Games

| Game | Subject | Covers |
|---|---|---|
| [مفتاح التواريخ](https://elarabyelaidy19.github.io/learning-games/history-bac2-unit1/) | History, 2nd year Egyptian Baccalaureate, term 1 | Unit 1, lessons 1–4 |

## Layout

- `index.html`: the games list (landing page).
- `<game>/index.html`: a self-contained game, served as is.
- `<game>/src/`: the game's source, when it has one.

## Adding a game

1. Create a folder such as `geography-bac2-unit1/` with an `index.html`.
2. Add a card for it to the list in the root `index.html`, and a row to the table above.
3. Push to `main`. GitHub Pages redeploys automatically.

## Editing مفتاح التواريخ

The content lives in `history-bac2-unit1/src/content/lesson1.json` … `lesson4.json` (study cards, quiz questions, book exercises). `template.html` holds the game engine, and `keys.json` maps each of the book's 11 key dates to the section that unlocks it.

After editing, rebuild:

```
python3 history-bac2-unit1/src/build.py
```

The build checks every question (option counts, answer indexes, blanks, match and sort shapes) and writes `history-bac2-unit1/index.html`.
