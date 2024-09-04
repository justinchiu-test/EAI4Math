import re

def replacements(x):
    return (x
        .replace("\\begin{align*}", "$\\begin{align*}")
        .replace("\\end{align*}", "\\end{align*}$")
        .replace("\\[", "$")
        .replace("\\]", "$")
        .replace("\\(", "$")
        .replace("\\)", "$")
        .replace("$\$$", "\$")
        .replace("\n", "  \n")
    )


def split_text_and_keep_equations(text):
    # Define a regex pattern to identify LaTeX equations environments
    equation_pattern = r'(\\begin{align\*}.*?\\end{align\*})'
    equation_pattern = r'(\\\[.*?\\\])'
    equation_pattern = r'(\\\(.*?\\\))'
    #equation_pattern = r'(\\\\\[.*?\\\\\])|(\\\\\(.*?\\\\\))'
    
    # Use re.split to split the text while keeping the delimiters (equations)
    split_text_with_equations = re.split(equation_pattern, text, flags=re.DOTALL)

    return split_text_with_equations
