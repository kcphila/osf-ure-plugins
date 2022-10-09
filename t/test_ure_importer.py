import pytest
import os,sys,re
import pdb,warnings
import textwrap

sys.path.insert(0, os.path.dirname(__file__) + '/..')
import ure
input_dir = os.path.dirname(__file__) + '/input'


#def test_simple_tables():
#    ''' Test docx -> markdown import of features from t/input/simple_tables.docx'''
#    compare_import_to_markdown("simple_tables.docx")

#def test_basic_formatting():
#    compare_import_to_markdown("ure_formatting_test.docx")

def test_new_test():
    # Use this to see what the markdown output will be for a new file to import.

    print_rendered_markdown("Basic Formatting.docx")
    pass

def compare_import_to_markdown(filename):
    """ Helper function to compare the markdown rendered by an importer to expected markdown output.
    
    This imports the markdown from the proivded filename, which is expected to be in the t/input 
    directory, to saved markdown output, which is expected to be in the t/md directory and 
    will be loaded by calling `load_md_file`     
    """

    importer = ure.importer.from_file(input_dir + '/' + filename)
    assert importer, f"Importer created for {filename}"
    imported_md = importer.markdown
    assert imported_md, f"markdown created from document {filename}"
    
    actual_md = load_md_file(filename)
    assert actual_md, f"raw markdown comparison files found"
    markdown_iter = iter(actual_md)

    i = 0
    for node_title, node_data in imported_md:
        actual_node = next(markdown_iter)
        assert node_title == actual_node[0], f"Node {i} title is '{node_title}', but the comparison data thinks it should be '{actual_node[0]}'"

        actual_wiki_iter = iter(actual_node[1])
        w = 0
        for wiki_title, wiki_text in node_data:
            actual_wiki = next(actual_wiki_iter)
            assert wiki_title == actual_wiki[0], f"Node {i}, Wiki {w} title is '{wiki_title}', but the comparison data thinks it should be '{actual_wiki[0]}'"
            assert wiki_text == actual_wiki[1], f"Node {i}, Wiki {w} ('{wiki_title}') does not have matching text!"
            w += 1
        i += 1

def load_md_file(test_file):
    """ takes a filename with any extension and loads the structure from the t/md file.
    
    This is intended to be shorthand to load the file or files from t/md based on an input document.

    The files saved in t/md can be in one of several formats:
        - just a single `filename.md` if there's only one wiki output to compare
        - a series `filename.0.md`, `filename.1.md` if there are multiple wikis
        - a series `filename.0.0.md`, `filename.0.1.md` if there are multiple nodes and wikis 

    Args:
        test_file: the filename to constuct a base from. This is expected to be an input filename,
            and the extension will be stripped.
    
    Returns:
        A parallel nested list structure like what will be returned by the ure.importer  
    """

    base_filename = re.sub(r'\.[^\.]+$', '', test_file)
    
    if os.path.exists(f"t/md/{base_filename}.0.0.md"):
        # files are broken down by project-component AND multiple wikis
        iprj = 0        
        while os.path.exists(f"t/md/{base_filename}.{iprj}.0.md"):
            iwiki = 0
            while os.path.exists(f"t/md/{base_filename}.{iprj}.{iwiki}.md"):
                iwiki += 1
    elif os.path.exists(f"t/md/{base_filename}.0.md"):
        node_wikis = []
        node_title = None
        iwiki = 0
        while os.path.exists(f"t/md/{base_filename}.{iwiki}.md"):
            with open(f"t/md/{base_filename}.{iwiki}.md") as fh:
                if iwiki == 0:
                    node_title = fh.readline().strip()
                title = fh.readline()
                text = fh.read()
                node_wikis.append([title.strip(), text.strip()])        
            iwiki += 1
        return([[node_title, node_wikis]])
    elif os.path.exists(f"t/md/{base_filename}.md"):
        node_wikis = []
        node_title = None
        with open(f"t/md/{base_filename}.md") as fh:
            node_title = fh.readline().strip()
            wiki_title = fh.readline().strip()
            text = fh.read().strip()
        return([[node_title, [[wiki_title, text]]]])
    else:
        raise Exception(f"Cannot find a file with a base name {test_file}")


def print_rendered_markdown(test_file):
    """ Prints out the markdown generated by a file in the t/input directory

    This is used when writing new tests. It will print out the text as currently rendered, 
    which can be reified into a test easily.

    Remember to run pytest `t/test_ure_importer.py -s -vv`

    Args:
        test_file: the fileanme within the t/input folder that will get parsed.
    
    
    """

    importer = ure.importer.from_file(input_dir + '/' + test_file)
    md = importer.markdown
    
    m = re.fullmatch(r'(.*)\.([^\.]+)', test_file)
    test_func = m.group(1)
    ext = m.group(2)

    print(f"""
    \ndef test_{test_func}():
    ''' Test {ext} -> markdown import of features from t/input/{test_file}'''

    importer = ure.importer.from_file(input_dir + '/' + "{test_file}")
    md = importer.markdown
    
    assert md[0][0] == '{md[0][0]}', "Project title is correct"
    """)
    i = 0
    for wiki_title, wiki_text in md[0][1]:
        print(f"""
    # Check Wiki {i}
    wiki_{i} = md[0][1][0]
    assert wiki_{i}[0] == '{wiki_title}', "Wiki {i} title is correct\"
    assert wiki_{i}[1] == textwrap.dedent('''\n""" \
            + textwrap.indent(wiki_text, '        ') \
            + f"\n        ''').strip(), \"Wiki {i} text is correct\"")
