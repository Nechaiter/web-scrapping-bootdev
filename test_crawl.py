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
      tests:list[tuple]=[(
          "https://crawler-test.com",
          """input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'""",
          "https://crawler-test.com"),
                         
                         ]
      
      for test in tests:
        input_url,input_body = 
        # actual = get_urls_from_html(input_body, input_url)
        # expected = ["https://crawler-test.com"]
        # self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main() 