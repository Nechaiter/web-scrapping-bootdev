import unittest
import crawl

class Test_crawl(unittest.TestCase):
    def test_normalize_url(self):

        inputs_url: list[str] = [
            "https://www.boot.dev/blog/path/",
            "https:www.boot.dev/blog/path/",
            "https://www.boot.dev/blog/path",
            "http://www.boot.dev/blog/path/",
            "http://www.boot.dev/blog/path",
        ]
        expected = "www.boot.dev/blog/path"

        for link in inputs_url:

            actual:str = crawl.normalize_url(link)
            self.assertEqual(actual, expected)
        

    def test_heading(self):
        tests:list[tuple]=[("""<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>""","Welcome to Boot.dev"),(
            """
<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <h2>Hola</h2>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>""","Welcome to Boot.dev"),
(
            """
<html>
  <body>
    <h2>Hola</h2>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>""","Hola"),
(
"""
<html>
  <body>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>""","") 
        ]
        for test in tests:
            html,spected_heading = test
            actual_heading:str = crawl.get_heading_from_html(html)
            self.assertEqual(actual_heading,spected_heading)

    def test_paragraph(self) -> None:
        tests:list[tuple]=[("""<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>""","Learn to code by building real projects."),(
            """
<html>
  <body>
    <h1>Welcome to Boot.dev</h1>
    <h2>Hola</h2>
    <p>This is the second paragraph.</p>
    <main>
      <p>Learn to code by building real projects.</p>
      <p>This is the second paragraph.</p>
    </main>
  </body>
</html>""","Learn to code by building real projects."),
(
            """
<html>
  <body>
    <h2>Hola</h2>
        <p>This is the second paragraph.</p>
    <main>
    </main>
  </body>
</html>""",""),
(
"""
<html>
  <body>
    <main>
    </main>
  </body>
</html>""","") 
        ]

        for test in tests:
            html,spected_paragh = test
            actual_paragraph:str = crawl.get_first_paragraph_from_html(html)
            self.assertEqual(actual_paragraph,spected_paragh)

    def test_get_urls_from_html_absolute(self):
      # base_url, html, expected value
      tests:list[tuple]=[
        (
          "https://crawler-test.com",
          """<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>""",
          ["https://crawler-test.com"]
        ),
        (
          "https://crawler-test.com",
          """<html><body><a href="/paralelo.html"><span>Boot.dev</span></a></body></html>""",
          ["https://crawler-test.com/paralelo.html"]
        ),
        (
          "https://crawler-test.com",
          """<html><body><a href="blog.html"><span>Boot.dev</span></a></body></html>""",
          ["https://crawler-test.com/blog.html"]
        ),
        (
          "https://crawler-test.com/articles/",
          """<html><body><a href="../contact.html"><span>Boot.dev</span></a></body></html>""",
          ["https://crawler-test.com/articles/contact.html"]
        ),
        (
          "https://crawler-test.com/articles/2024/",
          """<html><body><a href="./post.html"><span>Boot.dev</span></a></body></html>""",
          ["https://crawler-test.com/articles/2024/post.html"]
        ),
        (
          "https://crawler-test.com/articles/2024/",
          """<html><body><a href="https://docs.boot.dev"><span>Docs</span></a><a href="/assets/style.css"><span>Style</span></a></body></html>""",
          ["https://docs.boot.dev", "https://crawler-test.com/articles/2024/assets/style.css"]
        ),
        (
          "https://crawler-test.com",
          """<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a><a href="/paralelo.html"><span>Boot.dev</span></a></body></html>""",
          ["https://crawler-test.com","https://crawler-test.com/paralelo.html"]
        ),
        (
          "https://crawler-test.com",
          """<html><body><a><span>Boot.dev</span></a></body></html>""",
          [""]
        ),
        (
          "https://crawler-test.com",
          """<html><body><a><span>Boot.dev</span></a><a href="/paralelo.html"><span>Boot.dev</span></a></body></html>""",
          ["","https://crawler-test.com/paralelo.html"]
        )
        ]
      
      for test in tests:
        input_url,input_html,expected_results = test 
        actual:list[str] = crawl.get_urls_from_html(input_html, input_url)
        if len(actual) != len(expected_results):
           print(actual,expected_results)
           self.fail("The number of links does not match between the actual and expected values.")
        self.assertEqual(actual, expected_results)

    def test_get_images_from_html_relative(self):

      tests:list[tuple]=[
        (
          "https://crawler-test.com",
          """<html><body></body><img src="/logo.png" alt="Logo"></html>""",
          ["https://crawler-test.com/logo.png"]
        ),
        (
          "https://example.com",
          """<html><body><img src="/images/photo.jpg" alt="Photo"><img src="/images/banner.jpg" alt="Banner"></body></html>""",
          ["https://example.com/images/photo.jpg", "https://example.com/images/banner.jpg"]
        ),
        (
          "https://example.com/pages",
          """<html><body><img src="https://example.com/absolute.png" alt="Absolute"><img src="/relative.png" alt="Relative"></body></html>""",
          ["https://example.com/absolute.png", "https://example.com/pages/relative.png"]
        ),
        (
          "https://mysite.com",
          """<html><body><img src="/icon1.svg" alt="Icon 1"><img src="/icon2.svg" alt="Icon 2"><img src="/icon3.svg" alt="Icon 3"></body></html>""",
          ["https://mysite.com/icon1.svg", "https://mysite.com/icon2.svg", "https://mysite.com/icon3.svg"]
        ),
        (
          "https://photos.com",
          """<html><body><img src="https://cdn.photos.com/image.jpg" alt="CDN Image"><img src="/local/image.jpg" alt="Local Image"></body></html>""",
          ["https://cdn.photos.com/image.jpg", "https://photos.com/local/image.jpg"]
        ),
        (
          "https://photos.com",
          """<html><body><img alt="CDN Image"><img src="" alt="Local Image"></body></html>""",
          ["", ""]
        ),
      ]

      for test in tests:
        input_url, input_body, expected = test
        actual = crawl.get_images_from_html(input_body, input_url)
        if len(actual) != len(expected):
           print(actual,expected)
           self.fail("The number of links does not match between the actual and expected values.")

        self.assertEqual(actual, expected) 
    


if __name__ == "__main__":
    unittest.main() 