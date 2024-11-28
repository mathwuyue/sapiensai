import re
import time
import tracemalloc
import sys

# Define variables for magic numbers
MAX_HEADING_LENGTH = 7
MAX_HEADING_CONTENT_LENGTH = 200
MAX_HEADING_UNDERLINE_LENGTH = 200
MAX_HTML_HEADING_ATTRIBUTES_LENGTH = 100
MAX_LIST_ITEM_LENGTH = 200
MAX_NESTED_LIST_ITEMS = 6
MAX_LIST_INDENT_SPACES = 7
MAX_BLOCKQUOTE_LINE_LENGTH = 200
MAX_BLOCKQUOTE_LINES = 15
MAX_CODE_BLOCK_LENGTH = 1500
MAX_CODE_LANGUAGE_LENGTH = 20
MAX_INDENTED_CODE_LINES = 20
MAX_TABLE_CELL_LENGTH = 200
MAX_TABLE_ROWS = 20
MAX_HTML_TABLE_LENGTH = 2000
MIN_HORIZONTAL_RULE_LENGTH = 3
MAX_SENTENCE_LENGTH = 400
MAX_QUOTED_TEXT_LENGTH = 300
MAX_PARENTHETICAL_CONTENT_LENGTH = 200
MAX_NESTED_PARENTHESES = 5
MAX_MATH_INLINE_LENGTH = 100
MAX_MATH_BLOCK_LENGTH = 500
MAX_PARAGRAPH_LENGTH = 1000
MAX_STANDALONE_LINE_LENGTH = 800
MAX_HTML_TAG_ATTRIBUTES_LENGTH = 100
MAX_HTML_TAG_CONTENT_LENGTH = 1000
LOOKAHEAD_RANGE = 100  # Number of characters to look ahead for a sentence boundary

# Define the regex pattern
chunk_regex = re.compile(
    "(" +
    # 1. Headings (Setext-style, Markdown, and HTML-style, with length constraints)
    rf"(?:^(?:[#*=-]{{1,{MAX_HEADING_LENGTH}}}|\w[^\r\n]{{0,{MAX_HEADING_CONTENT_LENGTH}}}\r?\n[-=]{{2,{MAX_HEADING_UNDERLINE_LENGTH}}}|<h[1-6][^>]{{0,{MAX_HTML_HEADING_ATTRIBUTES_LENGTH}}}>)[^\r\n]{{1,{MAX_HEADING_CONTENT_LENGTH}}}(?:</h[1-6]>)?(?:\r?\n|$))" +
    "|" +
    # New pattern for citations
    rf"(?:\[\d+\][^\r\n]{{1,{MAX_STANDALONE_LINE_LENGTH}}})" +
    "|" +
    # 2. List items (bulleted, numbered, lettered, or task lists, including nested, up to three levels, with length constraints)
    rf"(?:(?:^|\r?\n)[ \t]{{0,3}}(?:[-*+•]|\d{{1,3}}\.\w\.|\[[ xX]\])[ \t]+(?:(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))|(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?:.{{1,{LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))?))" +
    rf"(?:(?:\r?\n[ \t]{{2,5}}(?:[-*+•]|\d{{1,3}}\.\w\.|\[[ xX]\])[ \t]+(?:(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))|(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?:.{{1,{LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))?)))" +
    rf"{{0,{MAX_NESTED_LIST_ITEMS}}}(?:\r?\n[ \t]{{4,{MAX_LIST_INDENT_SPACES}}}(?:[-*+•]|\d{{1,3}}\.\w\.|\[[ xX]\])[ \t]+(?:(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))|(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{1,{MAX_LIST_ITEM_LENGTH}}}\b(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?:.{{1,{LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))?)))" +
    rf"{{0,{MAX_NESTED_LIST_ITEMS}}})?)" +
    "|" +
    # 3. Block quotes (including nested quotes and citations, up to three levels, with length constraints)
    rf"(?:(?:^>(?:>|\\s{{2,}}){{0,2}}(?:(?:\b[^\r\n]{{0,{MAX_BLOCKQUOTE_LINE_LENGTH}}}\b(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))|(?:\b[^\r\n]{{0,{MAX_BLOCKQUOTE_LINE_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{0,{MAX_BLOCKQUOTE_LINE_LENGTH}}}\b(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?:.{{1,{LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))?))\r?\n?){1,{MAX_BLOCKQUOTE_LINES}})" +
    "|" +
    # 4. Code blocks (fenced, indented, or HTML pre/code tags, with length constraints)
    rf"(?:(?:^|\r?\n)(?:```|~~~)(?:\w{{0,{MAX_CODE_LANGUAGE_LENGTH}}})?\r?\n[\s\S]{{0,{MAX_CODE_BLOCK_LENGTH}}}?(?:```|~~~)\r?\n?" +
    rf"|(?:(?:^|\r?\n)(?: {{4}}|\t)[^\r\n]{{0,{MAX_LIST_ITEM_LENGTH}}}(?:\r?\n(?: {{4}}|\t)[^\r\n]{{0,{MAX_LIST_ITEM_LENGTH}}}){{0,{MAX_INDENTED_CODE_LINES}}}\r?\n?)" +
    rf"|(?:<pre>(?:<code>)?[\s\S]{{0,{MAX_CODE_BLOCK_LENGTH}}}?(?:</code>)?</pre>))" +
    "|" +
    # 5. Tables (Markdown, grid tables, and HTML tables, with length constraints)
    rf"(?:(?:^|\r?\n)(?:\|[^\r\n]{{0,{MAX_TABLE_CELL_LENGTH}}}\|(?:\r?\n\|[-:]{{1,{MAX_TABLE_CELL_LENGTH}}}\|){{0,1}}(?:\r?\n\|[^\r\n]{{0,{MAX_TABLE_CELL_LENGTH}}}\|){{0,{MAX_TABLE_ROWS}}}" +
    rf"|<table>[\s\S]{{0,{MAX_HTML_TABLE_LENGTH}}}?</table>))" +
    "|" +
    # 6. Horizontal rules (Markdown and HTML hr tag)
    rf"(?:^(?:[-*_]){{{MIN_HORIZONTAL_RULE_LENGTH},}}\s*$|<hr\s*/?>)" +
    "|" +
    # 10. Standalone lines or phrases (including single-line blocks and HTML elements, with length constraints)
    rf"(?:^(?:<[a-zA-Z][^>]{{0,{MAX_HTML_TAG_ATTRIBUTES_LENGTH}}}>)?(?:(?:[^\r\n]{{1,{MAX_STANDALONE_LINE_LENGTH}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))" +
    rf"|(?:[^\r\n]{{1,{MAX_STANDALONE_LINE_LENGTH}}}(?=[\r\n]|$))" +
    rf"|(?:[^\r\n]{{1,{MAX_STANDALONE_LINE_LENGTH}}}(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?:.{{1,{LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\U0001F600-\U0001F64F])(?=\s|$))?))" +
    rf"(?:<[/a-zA-Z][^>]{{0,{MAX_HTML_TAG_ATTRIBUTES_LENGTH}}}>)?)" +
    ")"
)

def test_regex_patterns():
    # Test cases
    test_texts = [
        "## This is a heading\n",
        "[1] This is a citation.\n",
        "- List item 1\n- List item 2\n",
        "> Blockquote example.\n",
        "```\nCode block\n```\n",
        "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n",
        "---\n",
        "<p>This is a standalone line.</p>\n"
    ]

    for text in test_texts:
        match = chunk_regex.search(text)
        print(f"Testing: {text.strip()}\nMatch: {bool(match)}\n")

   
def format_bytes(size):
    """Function to format bytes to a human-readable string."""
    # Formatting to KB, MB, or GB as needed
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def main(input_file):
    # Read the input text file
    with open(input_file, 'r', encoding='utf-8') as f:
        test_text = f.read()

    # Start measuring time and memory
    start_time = time.time()
    tracemalloc.start()

    # Apply the regex
    matches = chunk_regex.findall(test_text)

    # End measuring time and memory
    execution_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Calculate memory used
    memory_used = peak

    # Output results
    print(f"Number of chunks: {len(matches)}")
    print(f"Execution time: {execution_time:.3f} seconds")
    print(f"Memory used: {format_bytes(memory_used)}")

    # Output the first 10 matches (or fewer if there are less than 10)
    print('\nFirst 10 chunks:')
    for i, match in enumerate(matches[:10]):
        print(f"{i + 1}: {match[:50]}...")

    # Output regex flags
    print(f"\nRegex flags: {chunk_regex.flags}")

    # Check for potential issues
    if execution_time > 5:
        print('\nWarning: Execution time exceeded 5 seconds. The regex might be too complex or the input too large.')
    if memory_used > 100 * 1024 * 1024:
        print('\nWarning: Memory usage exceeded 100 MB. Consider processing the input in smaller chunks.')

if __name__ == "__main__":
    test_regex_patterns()
    if len(sys.argv) != 2:
       print(f"Usage: python {sys.argv[0]} <input_file>")
       sys.exit(1)
    
    main(sys.argv[1])