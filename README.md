# NewsBot

A bot application for aggregating and delivering news updates.

## Description

NewsBot is an automated system that collects, processes, and delivers news content from various sources. This project aims to provide users with relevant and timely news updates.

## Features

- News aggregation from multiple sources
- Content filtering and categorization

## Installation

```bash
# Clone the repository
git clone https://github.com/amgadmadkour/newsbot.git

# Navigate to project directory
cd newsbot

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Usage

Run the project from the repository root:

```bash
uv run newsbot
```

The app reads RSS feed URLs from `config/feeds/*.txt`, fetches articles, prints them to the console, and writes logs to `newsbot.log`. Each feed file's name (e.g. `business.txt`, `general.txt`) is used as the category for the articles it contains.

To write the results as an HTML page grouped by category, with a category navigation list on the left-hand side, use `--html`:

```bash
# Writes to newsbot.html
uv run newsbot --html

# Or choose the output path
uv run newsbot --html report.html
```

## Running Tests

Run the unit test suite from the repository root:

```bash
uv run pytest
```

For quieter output:

```bash
uv run pytest -q
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
