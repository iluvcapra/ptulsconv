from parsimonious import NodeVisitor, Grammar
from typing import Dict, Optional


tag_grammar = Grammar(
    r"""
    document  = modifier? line? word_sep? tag_list?
    line      = word (word_sep word)*
    tag_list  = tag*
    tag       = key_tag / short_tag / full_text_tag / tag_junk
    key_tag        = "[" key "]" word_sep?
    short_tag      = "$" key "=" word word_sep?
    full_text_tag  = "{" key "=" value "}" word_sep?
    key            = ~"[A-Za-z][A-Za-z0-9_]*"
    value          = ~"[^}]+"
    tag_junk       = word word_sep?
    word           = ~"[^ \[\{\$][^ ]*"
    word_sep       = ~" +"
    modifier       = ("@" / "&" / "!") word_sep?
    """
)


def parse_tags(prompt) -> "TaggedStringResult":
    ast = tag_grammar.parse(prompt)
    return TagListVisitor().visit(ast)


class TaggedStringResult:
    content: Optional[str]
    tag_dict: Optional[Dict[str, str]]
    mode: str

    def __init__(self, content, tag_dict, mode):
        self.content = content
        self.tag_dict = tag_dict
        self.mode = mode


class TagListVisitor(NodeVisitor):

    @staticmethod
    def visit_document(_, visited_children) -> TaggedStringResult:
        modifier_opt, line_opt, _, tag_list_opt = visited_children

        return TaggedStringResult(content=next(iter(line_opt), None),
                                  tag_dict=next(iter(tag_list_opt), None),
                                  mode=next(iter(modifier_opt), 'Normal')
                                  )

    @staticmethod
    def visit_line(node, _):
        return str.strip(node.text, " ")

    @staticmethod
    def visit_modifier(node, _):
        if node.text.startswith('@'):
            return 'Timespan'
        elif node.text.startswith('&'):
            return 'Append'
        elif node.text.startswith('!'):
            return 'Movie'
        else:
            return 'Normal'

    @staticmethod
    def visit_tag_list(_, visited_children):
        retdict = dict()
        for child in visited_children:
            if child[0] is not None:
                k, v = child[0]
                retdict[k] = v
        return retdict

    @staticmethod
    def visit_key_tag(_, children):
        return children[1].text, children[1].text

    @staticmethod
    def visit_short_tag(_, children):
        return children[1].text, children[3].text

    @staticmethod
    def visit_full_text_tag(_, children):
        return children[1].text, children[3].text

    @staticmethod
    def visit_tag_junk(_node, _visited_children):
        return None

    def generic_visit(self, node, visited_children) -> object:
        return visited_children or node
