import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from check_links import get_local_path, LinkParser

class TestCheckLinks(unittest.TestCase):

    def test_get_local_path_trailing_slash(self):
        # A trailing-slash directory path resolves to index.html in that dir.
        expected = os.path.join('blog', 'index.html')

        # We need to make sure the expected output matches what get_local_path actually does.
        # Since get_local_path('/blog/') does os.path.join('blog/', 'index.html'), we will compare
        # it against os.path.join('blog', 'index.html') but taking into account the slash if needed.
        # However, the prompt specifically says "resolves to os.path.join('blog', 'index.html')"
        # We will assert that os.path.normpath(result) == os.path.normpath(expected) to be extremely safe,
        # but the prompt asks to cover the verified behavior: expected value with os.path.join('blog', 'index.html').

        # On some platforms os.path.join('blog/', 'index.html') != os.path.join('blog', 'index.html')
        # We just assert equality, and if they differ by purely normalization on Windows, normpath fixes it.
        # But wait, the pure standard equality might just work on Unix. Let's use the simplest form.
        self.assertEqual(
            os.path.normpath(get_local_path('/blog/')),
            os.path.normpath(os.path.join('blog', 'index.html'))
        )

    def test_get_local_path_root(self):
        # The bare root '/' resolves to 'index.html'.
        self.assertEqual(get_local_path('/'), 'index.html')

    def test_get_local_path_extensionless(self):
        # An extensionless path resolves by appending .html.
        self.assertEqual(get_local_path('/blog/post'), 'blog/post.html')

    def test_get_local_path_with_extension(self):
        # A path whose basename already contains a dot is returned unchanged.
        self.assertEqual(get_local_path('/assets/x.css'), 'assets/x.css')
        self.assertEqual(get_local_path('/products/ai-blueprint.html'), 'products/ai-blueprint.html')

    def test_get_local_path_no_leading_slash(self):
        # A path that does NOT start with '/' returns None.
        self.assertIsNone(get_local_path('blog/no-slash'))

    def test_link_parser(self):
        html = '''
        <html>
            <body>
                <a href="/blog/post#frag?x=1">Internal link with fragment and query</a>
                <img src="/assets/img.png">Internal image</img>
                <a href="//cdn.example.com/script.js">Protocol-relative link</a>
                <a href="https://ext.com/y">Absolute external link</a>
                <a href="">Empty href</a>
                <img src="">Empty src</img>
            </body>
        </html>
        '''
        parser = LinkParser()
        parser.feed(html)

        # We expect '/blog/post' (stripped of #frag?x=1) and '/assets/img.png'
        # Absolute, protocol-relative, and empty links should be ignored.
        self.assertEqual(parser.links, ['/blog/post', '/assets/img.png'])

if __name__ == '__main__':
    unittest.main()
