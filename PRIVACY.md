# Privacy

Human Design is a set of instructions, reference files, data and Python
scripts that your coding agent reads and runs on your machine. It has no
server and collects no data.

- The scripts use the Python standard library and make no network requests.
- `render_check.py` starts the Chrome, Chromium or Edge already installed on
  your machine, in headless mode with a temporary profile, and talks to it over
  the DevTools protocol on 127.0.0.1. It loads only the file or URL you give it.
- `fingerprint.py --save NAME` stores a small JSON summary of a design
  (typeface names, colour families, radius, habits; no source code or content)
  in `~/.human-design/fingerprints`, and only when you pass `--save`.
  `palette.py` reads that folder to avoid repeating your colours. Nothing is
  written anywhere else unless you ask for a file.
- When the skill tells your agent to find photographs, the agent searches free
  photo libraries (for example Pexels, Unsplash, Openverse) with its own web
  tools. That is your agent's activity, under its own privacy terms.

Questions: open an issue at https://github.com/thinhledev/human-design/issues.
