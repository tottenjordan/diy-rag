"""
Utility methods for displaying rich content results
"""
from IPython.display import display, HTML
import markdown as md
from typing import List

def get_chunk_content(results: List) -> List:
    return [
        doc.page_content.replace("\n", "<br>")
        + f'<br><br> <b><a href="">Source: {doc.metadata.get("source")}</a></b>'
        for doc in results
    ][:5]


CONTRASTING_COLORS = [
    "rgba(255, 0, 0, 0.2)",  # Semi-transparent red
    "rgba(0, 255, 0, 0.2)",  # Semi-transparent green
    "rgba(0, 0, 255, 0.2)",  # Semi-transparent blue
    "rgba(255, 255, 0, 0.2)",  # Semi-transparent yellow
    "rgba(0, 255, 255, 0.2)",  # Semi-transparent cyan
    "rgba(255, 0, 255, 0.2)",  # Semi-transparent magenta
    "rgba(255, 165, 0, 0.2)",  # Semi-transparent orange
    "rgba(255, 105, 180, 0.2)",  # Semi-transparent pink
    "rgba(75, 0, 130, 0.2)",  # Semi-transparent indigo
    "rgba(255, 192, 203, 0.2)",  # Semi-transparent light pink
    "rgba(64, 224, 208, 0.2)",  # Semi-transparent turquoise
    "rgba(128, 0, 128, 0.2)",  # Semi-transparent purple
    "rgba(210, 105, 30, 0.2)",  # Semi-transparent chocolate
    "rgba(220, 20, 60, 0.2)",  # Semi-transparent crimson
    "rgba(95, 158, 160, 0.2)",  # Semi-transparent cadet blue
    "rgba(255, 99, 71, 0.2)",  # Semi-transparent tomato
    "rgba(144, 238, 144, 0.2)",  # Semi-transparent light green
    "rgba(70, 130, 180, 0.2)",  # Semi-transparent steel blue
]


def convert_markdown_to_html(text: str) -> str:
    # Convert Markdown to HTML, ensuring embedded HTML is preserved and interpreted correctly.
    md_extensions = [
        "extra",
        "abbr",
        "attr_list",
        "def_list",
        "fenced_code",
        "footnotes",
        "md_in_html",
        "tables",
        "admonition",
        "codehilite",
        "legacy_attrs",
        "legacy_em",
        "meta",
        "nl2br",
        "sane_lists",
        "smarty",
        "toc",
        "wikilinks",
    ]
    return str(md.markdown(text, extensions=md_extensions))


# Utility function to create HTML table with colored results
def display_html_table(simple_results: List[str], reranked_results: List[str]) -> None:
    # Find all unique values in both lists
    unique_values = set(simple_results + reranked_results)

    # Ensure we have enough colors for all unique values
    # If not, colors will repeat, which might not be ideal but is necessary if the number of unique values exceeds the number of colors
    colors = CONTRASTING_COLORS * (len(unique_values) // len(CONTRASTING_COLORS) + 1)

    # Create a dictionary to map each unique value to a color
    color_map = dict(zip(unique_values, colors))

    # Initialize the HTML table with style for equal column widths
    html = """
    <style>
    td, th {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        color: #000;
    }
    tr {background-color: #ffffff;}
    /* Set table layout to fixed to respect column widths */
    table {
        table-layout: fixed;
        width: 100%; /* You can adjust the overall table width as needed */
        max-height: 100vh !important; /* Set the maximum height of the table */
        overflow-y: auto; /* Add a vertical scrollbar if the content exceeds the maximum height */
    }
    /* Set equal width for both columns */
    td, th {
        width: 50%;
    }
    .text-black {
        color: #000; /* Set the text color to black */
    }
    </style>
    <table>
    <tr><th>Retriever Results</th><th>Reranked Results</th></tr>
    """
    # Iterate over the results and assign the corresponding color to each cell
    for simple, reranked in zip(simple_results, reranked_results):
        html += f"""
        <tr>
            <td style='color: black; background-color: {color_map[simple]}; font-size: 8px;'>
                <p class='text-black'>{convert_markdown_to_html(simple)}</p>
            </td>
            <td style='color: black; background-color: {color_map[reranked]}; font-size: 8px;'>
                <p class='text-black'>{convert_markdown_to_html(reranked)}</p>
            </td>
        </tr>
        """
    html += "</table>"
    display(HTML(html))


def get_sxs_comparison(
    simple_retriever, reranking_api_retriever, query, search_kwargs
) -> List:
    simple_results = get_chunk_content(
        simple_retriever.invoke(query, search_kwargs=search_kwargs)
    )
    reranked_results = get_chunk_content(
        reranking_api_retriever.invoke(query, search_kwargs=search_kwargs)
    )
    display_html_table(simple_results, reranked_results)

    return reranked_results


def display_grounded_generation(response) -> None:
    # Extract the answer with citations and cited chunks
    answer_with_citations = response.answer_with_citations
    cited_chunks = response.cited_chunks

    # Build HTML for the chunks
    chunks_html = "".join(
        [
            f"<div id='chunk-{index}' class='chunk'>"
            + f"<div class='source'>Source {index}: <a href='{chunk['source'].metadata['source']}' target='_blank'>{chunk['source'].metadata['source']}</a></div>"
            + f"<p>{chunk['chunk_text']}</p>"
            + "</div>"
            for index, chunk in enumerate(cited_chunks)
        ]
    )

    # Replace citation indices with hoverable spans
    for index in range(len(cited_chunks)):
        answer_with_citations = answer_with_citations.replace(
            f"[{index}]",
            f"<span class='citation' onmouseover='highlight({index})' onmouseout='unhighlight({index})'>[{index}]</span>",
        )

    # The complete HTML
    html_content = f"""
    <style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #e7f0fd;
        padding: 20px;
    }}
    .answer-box {{
        background-color: #f8f9fa;
        border-left: 4px solid #0056b3;
        padding: 20px;
        margin-bottom: 20px;
        color: #000;
    }}
    .citation {{
        background-color: transparent;
        cursor: pointer;
    }}
    .chunk {{
        background-color: #ffffff;
        border-left: 4px solid #007bff;
        padding: 10px;
        margin-bottom: 10px;
        transition: background-color 0.3s;
        color: #000;
    }}
    .source {{
        font-weight: bold;
        margin-bottom: 5px;
    }}
    a {{
        text-decoration: none;
        color: #0056b3;
    }}
    a:hover {{
        text-decoration: underline;
    }}
    </style>
    <div class='answer-box'>{answer_with_citations}</div>
    <div class='chunks-box'>{chunks_html}</div>
    <script>
    function highlight(index) {{
        // Highlight the citation in the answer
        document.querySelectorAll('.citation').forEach(function(citation) {{
            if (citation.textContent === '[' + index + ']') {{
                citation.style.backgroundColor = '#ffff99';
            }}
        }});
        // Highlight the corresponding chunk
        document.getElementById('chunk-' + index).style.backgroundColor = '#ffff99';
    }}
    function unhighlight(index) {{
        // Unhighlight the citation in the answer
        document.querySelectorAll('.citation').forEach(function(citation) {{
            if (citation.textContent === '[' + index + ']') {{
                citation.style.backgroundColor = 'transparent';
            }}
        }});
        // Unhighlight the corresponding chunk
        document.getElementById('chunk-' + index).style.backgroundColor = '#ffffff';
    }}
    </script>
    """
    display(HTML(html_content))