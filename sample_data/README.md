# QuickQuiz Studio Sample Data

This directory contains reference and offline demonstration data for QuickQuiz Studio.

## Files

- `sample_article.txt`: A sample technical article describing Python 3.14 features. Used as sample text input or MCP web-fetch demonstration target.
- `preset_quiz.json`: A pre-generated, verified 3-question quiz in standard QuickQuiz JSON schema. Allows instant offline execution during demonstrations without external API latency.

## Quiz Schema Requirements

Each quiz object must adhere to the following structure:
- `title` (str): Quiz title.
- `source_topic` (str): Origin article or topic name.
- `questions` (list): Array of question objects.
  - `id` (int): Unique question identifier.
  - `question` (str): Question prompt.
  - `choices` (list[str]): Exactly 4 unique answer choices.
  - `correct_index` (int): 0-indexed integer pointing to the correct choice (0 <= index <= 3).
  - `explanation` (str): Educational rationale explaining why the correct choice is valid.
