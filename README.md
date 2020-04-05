# HTML to Cheatsheet Generator

Generate a [Dash cheatsheet](https://github.com/Kapeli/cheatsheets) for Final
Cut Pro.

This code reads the shortcuts from the docuentation web site, and generaes a
Dash cheatsheet `*.rb` file.

## Installation

- [Install poetry](https://python-poetry.org/docs/#installation)
- `gem install cheatset`

## Usage

```shell
$ poetry run python html2cheatsheet.py
$ cheatset generate Final_Cut_Pro.rb
```

## To do

- Generalize this to work with other applications, *e.g.* Apple Motion.
- Simplify the installation – maybe port this to Ruby

## License

MIT
