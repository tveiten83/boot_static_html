import unittest
from textnode import TextNode, TextType
from markdown_extract import extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
from markdown_blocks import markdown_to_blocks, block_to_block_type, BlockType
from markdown_to_html import markdown_to_html_node

class TestTextNode(unittest.TestCase):

    # --- Equality tests ---
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)

    def test_eq_url_none(self):
        node = TextNode("Hello", TextType.TEXT, None)
        node2 = TextNode("Hello", TextType.TEXT)
        self.assertEqual(node, node2)

    # --- Not equal tests ---
    def test_not_eq_different_text(self):
        node = TextNode("Hello", TextType.BOLD)
        node2 = TextNode("World", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_text_type(self):
        node = TextNode("Hello", TextType.BOLD)
        node2 = TextNode("Hello", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_url(self):
        node = TextNode("Click", TextType.LINK, "https://a.com")
        node2 = TextNode("Click", TextType.LINK, "https://b.com")
        self.assertNotEqual(node, node2)

    def test_not_eq_url_vs_none(self):
        node = TextNode("Click", TextType.LINK, "https://example.com")
        node2 = TextNode("Click", TextType.LINK)
        self.assertNotEqual(node, node2)


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_single_image(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
        self.assertEqual(extract_markdown_images(text), [("rick roll", "https://i.imgur.com/aKaOqIh.gif")])

    def test_extract_multiple_images(self):
        text = "![img1](https://example.com/1.png) and ![img2](https://example.com/2.png)"
        self.assertEqual(extract_markdown_images(text), [
            ("img1", "https://example.com/1.png"),
            ("img2", "https://example.com/2.png"),
        ])

    def test_extract_images_empty(self):
        self.assertEqual(extract_markdown_images("No images here"), [])

    def test_extract_images_ignores_links(self):
        self.assertEqual(extract_markdown_images("This is a [link](https://example.com)"), [])

    def test_extract_single_link(self):
        text = "This is a [boot dev](https://www.boot.dev) link"
        self.assertEqual(extract_markdown_links(text), [("boot dev", "https://www.boot.dev")])

    def test_extract_multiple_links(self):
        text = "[google](https://google.com) and [youtube](https://youtube.com)"
        self.assertEqual(extract_markdown_links(text), [
            ("google", "https://google.com"),
            ("youtube", "https://youtube.com"),
        ])

    def test_extract_links_empty(self):
        self.assertEqual(extract_markdown_links("No links here"), [])

    def test_extract_links_ignores_images(self):
        self.assertEqual(extract_markdown_links("![img](https://example.com/img.png)"), [])

    def test_split_nodes_image(self):
        node = TextNode("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)", TextType.TEXT)
        self.assertListEqual(split_nodes_image([node]), [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ])

    def test_split_nodes_image_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual(split_nodes_image([node]), [node])

    def test_split_nodes_link(self):
        node = TextNode("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com)", TextType.TEXT)
        self.assertListEqual(split_nodes_link([node]), [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com"),
        ])

    def test_split_nodes_link_no_links(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual(split_nodes_link([node]), [node])

    def test_split_nodes_non_text_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        self.assertListEqual(split_nodes_image([node]), [node])
        self.assertListEqual(split_nodes_link([node]), [node])

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(text_to_textnodes(text), [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ])

    def test_text_to_textnodes_plain(self):
        self.assertListEqual(text_to_textnodes("Just plain text"), [
            TextNode("Just plain text", TextType.TEXT)
        ])


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items"""
        self.assertEqual(markdown_to_blocks(md), [
            "This is **bolded** paragraph",
            "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            "- This is a list\n- with items",
        ])

    def test_markdown_to_blocks_strips_whitespace(self):
        md = "  block one  \n\n  block two  "
        self.assertEqual(markdown_to_blocks(md), ["block one", "block two"])

    def test_markdown_to_blocks_removes_empty(self):
        md = "block one\n\n\n\nblock two"
        self.assertEqual(markdown_to_blocks(md), ["block one", "block two"])

    def test_markdown_to_blocks_single_block(self):
        md = "just one block"
        self.assertEqual(markdown_to_blocks(md), ["just one block"])


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Hello"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Hello"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Hello"), BlockType.HEADING)

    def test_code(self):
        self.assertEqual(block_to_block_type("```\nsome code\n```"), BlockType.CODE)

    def test_quote(self):
        self.assertEqual(block_to_block_type(">line one\n>line two"), BlockType.QUOTE)

    def test_unordered_list(self):
        self.assertEqual(block_to_block_type("- item one\n- item two"), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        self.assertEqual(block_to_block_type("1. first\n2. second\n3. third"), BlockType.ORDERED_LIST)

    def test_ordered_list_must_start_at_1(self):
        self.assertEqual(block_to_block_type("2. first\n3. second"), BlockType.PARAGRAPH)

    def test_paragraph(self):
        self.assertEqual(block_to_block_type("Just some text"), BlockType.PARAGRAPH)

    def test_not_heading_without_space(self):
        self.assertEqual(block_to_block_type("#Hello"), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """```
This is text that _should_ remain
the **same** even with inline stuff
```"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = "## Hello world"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><h2>Hello world</h2></div>")

    def test_unordered_list(self):
        md = "- item one\n- item two"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><ul><li>item one</li><li>item two</li></ul></div>")

    def test_ordered_list(self):
        md = "1. first\n2. second"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><ol><li>first</li><li>second</li></ol></div>")

    def test_quote(self):
        md = "> line one\n> line two"
        node = markdown_to_html_node(md)
        self.assertEqual(node.to_html(), "<div><blockquote>line one\nline two</blockquote></div>")

if __name__ == "__main__":
    unittest.main()
