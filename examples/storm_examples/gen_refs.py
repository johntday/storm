#!/usr/bin/env python3
import json
import re
from argparse import ArgumentParser


def link(label: str,
         url: str
         ) -> str:
    """
    Create a HTML link with target="_blank" rel="noopener noreferrer"
    """
    if not label or not url:
        raise ValueError("Label and URL must not be empty")
    return f'<a target="_blank" rel="noopener noreferrer" href="{url}">[{label}]</a>'


def process_article(input_filename,
                    citation_filename,
                    output_filename
                    ):
    """
    Process the article markdown file to add references and reformat citations.
    
    Args:
        input_filename: Path to the input markdown file
        citation_filename: Path to the citation JSON file
        output_filename: Path to the output markdown file
    """
    # Backup the input file
    # REMOVED - NOT NEEDED
    # backup_filename = f"{input_filename}.bak"
    # shutil.copy2(input_filename, backup_filename)
    # print(f"Backed up {input_filename} to {backup_filename}")

    # Read the input markdown file
    with open(input_filename, 'r', encoding='utf-8') as f:
        article_content = f.read()

    # Read the citation JSON file
    with open(citation_filename, 'r', encoding='utf-8') as f:
        citation_data = json.load(f)

    # Create a mapping from citation index to URL
    index_to_url = {}
    index_to_title = {}

    for url, info in citation_data["url_to_info"].items():
        index = citation_data["url_to_unified_index"].get(url)
        if index is not None:
            index_to_url[index] = url
            index_to_title[index] = info.get("title", "")

    # Find all citations in the article
    citation_pattern = r'\[(\d+)\]'
    citations = re.findall(citation_pattern, article_content)

    # Convert citations to unique integers
    unique_citations = set(map(int, citations))

    # Process the article in two steps:
    # 1. First, replace all citations with links
    for citation in unique_citations:
        if citation in index_to_url:
            url = index_to_url[citation]
            # Replace [citation] with a link while maintaining the original bracket format
            article_content = re.sub(
                r'\[(' + str(citation) + r')\](?!\()',
                lambda m: link(m.group(1), url),
                article_content
            )

    # 2. Then fix spacing issues
    # Find all citation links in the processed content
    citation_links = re.findall(r'<a target="_blank"[^>]+>\[\d+\]</a>', article_content)

    # Sort by length (longest first) to avoid partial replacements
    citation_links.sort(key=len, reverse=True)

    # Add space between adjacent citation links and ensure proper spacing
    for citation_link in citation_links:
        # Add space after link if followed by another citation
        article_content = article_content.replace(citation_link + '<a', citation_link + ' <a')

        # Add space after link if followed by text (not punctuation)
        article_content = re.sub(r'(' + re.escape(citation_link) + r')([^\s\.,;:\[\]\(\)<])', r'\1 \2', article_content)

    # Fix spacing for citations at the beginning of lines
    article_content = re.sub(r'(\n\s*)(<a target="_blank"[^>]+>\[\d+\]</a>)', r'\1\2 ', article_content)

    # Fix spacing between text and HTML links
    article_content = re.sub(r'([^\s])(<a target="_blank")', r'\1 \2', article_content)

    # Remove any double spaces that might have been introduced
    article_content = re.sub(r'  +', ' ', article_content)

    # Create references section
    references_section = "\n# References\n\n"

    # Sort citations numerically
    sorted_citations = sorted(unique_citations)

    # Add each reference
    for citation in sorted_citations:
        if citation in index_to_url:
            url = index_to_url[citation]
            title = index_to_title[citation]
            references_section += f"[{citation}] {title} - {url}\n\n"

    # Add references section to the article
    article_content += references_section

    # Write the processed content to the output file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(article_content)

    print(f"Processed article written to {output_filename}")
    print(f"Added {len(unique_citations)} references")


def run_generate_references(filepath: str):
    """
    Entrypoint
    """

    input_filename = 'storm_gen_article_polished.txt'
    citation_filename = 'url_to_info.json'
    output_filename = 'storm_gen_article_polished.md'

    # Construct full paths
    input_filename = f'{filepath}/{input_filename}'
    citation_filename = f'{filepath}/{citation_filename}'
    output_filename = f'{filepath}/{output_filename}'

    process_article(input_filename, citation_filename, output_filename)


def main(args):
    run_generate_references(args.filepath)


if __name__ == "__main__":
    parser = ArgumentParser(description='Process article markdown file to add references and reformat citations.')
    parser.add_argument('--filepath', type=str, help='Path to the directory containing the input files')

    args = parser.parse_args()

    if not args.filepath:
        parser.error("--filepath is required")

    main(args)
