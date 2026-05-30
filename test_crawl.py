import unittest
from crawl import normalize_url

class Test_crawl(unittest.TestCase):
    def test_normalize_url(self):

        inputs_url: list[str] = [
            "https://www.boot.dev/blog/path/",
            "https:/www.boot.dev/blog/path/",
            "https:www.boot.dev/blog/path/",
            "https://www.boot.dev/blog/path",
            "http://www.boot.dev/blog/path/",
            "http://www.boot.dev/blog/path",
        ]
        expected = "www.boot.dev/blog/path"

        for link in inputs_url:
            actual:str = normalize_url(link)
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main() 