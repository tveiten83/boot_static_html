from parentnode import ParentNode
from leafnode import LeafNode
from markdown_blocks import markdown_to_blocks, block_to_block_type, BlockType
from markdown_extract import text_to_textnodes
from text_node_to_html_node import text_node_to_html_node
from textnode import TextNode, TextType


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(tn) for tn in text_nodes]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.HEADING:
                level = 0
                while block[level] == "#":
                    level += 1
                text = block[level + 1:]
                children.append(ParentNode(f"h{level}", text_to_children(text)))
            case BlockType.CODE:
                text = block[4:-3]  # strip opening ```\n and closing ```
                code_node = LeafNode("code", text)
                children.append(ParentNode("pre", [code_node]))
            case BlockType.QUOTE:
                lines = block.split("\n")
                text = "\n".join(line.lstrip(">").strip() for line in lines)
                children.append(ParentNode("blockquote", text_to_children(text)))
            case BlockType.UNORDERED_LIST:
                lines = block.split("\n")
                items = [ParentNode("li", text_to_children(line[2:])) for line in lines]
                children.append(ParentNode("ul", items))
            case BlockType.ORDERED_LIST:
                lines = block.split("\n")
                items = [ParentNode("li", text_to_children(line.split(". ", 1)[1])) for line in lines]
                children.append(ParentNode("ol", items))
            case BlockType.PARAGRAPH:
                text = " ".join(block.split("\n"))
                children.append(ParentNode("p", text_to_children(text)))
    return ParentNode("div", children)
