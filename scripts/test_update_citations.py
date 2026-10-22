import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import update_citations as subject
import wos_client


class CitationRefreshTests(unittest.TestCase):
    def test_missing_bib_count_does_not_overwrite_next_article(self):
        text = """@article{first,
  title={First paper},
}
@article{second,
  title={Second paper},
  citation_count={99},
}
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.bib"
            path.write_text(text)
            with patch.object(subject, "BIB_FILE", path):
                subject.update_bib_citations({"first": 7})
            updated = path.read_text()
        self.assertIn("  citation_count={7},\n}\n@article{second", updated)
        self.assertIn("  citation_count={99},", updated)

    @patch.object(subject.urllib.request, "urlopen")
    def test_openalex_zero_is_valid_but_missing_count_is_not_zero(self, open_url):
        open_url.return_value = io.BytesIO(json.dumps({"cited_by_count": 0}).encode())
        self.assertEqual(subject.fetch_citation_count("10.1000/test"), 0)
        open_url.return_value = io.BytesIO(b'{}')
        with self.assertRaises(RuntimeError):
            subject.fetch_citation_count("10.1000/test")

    @patch.object(subject.urllib.request, "urlopen")
    def test_openalex_404_is_unmatched_but_authentication_failure_is_fatal(self, open_url):
        open_url.side_effect = urllib.error.HTTPError("url", 404, "not found", {}, None)
        self.assertIsNone(subject.fetch_citation_count("10.1000/test"))
        open_url.side_effect = urllib.error.HTTPError("url", 401, "auth", {}, None)
        with self.assertRaises(RuntimeError):
            subject.fetch_citation_count("10.1000/test")

    @patch.object(subject, "write_citations_yml")
    @patch.object(subject, "fetch_citation_count", side_effect=RuntimeError("API failed"))
    @patch.object(subject, "extract_dois_from_bib", return_value=[{"key": "first", "doi": "10.1000/test"}])
    def test_api_failure_does_not_write_partial_snapshot(self, extract, fetch, write):
        with patch("sys.stdout", new_callable=io.StringIO), self.assertRaises(RuntimeError):
            subject.main()
        write.assert_not_called()

    @patch.dict(wos_client.os.environ, {"WOS_API_KEY": "test-secret"})
    @patch.object(wos_client.subprocess, "run")
    def test_actions_key_does_not_require_local_keychain(self, run):
        self.assertEqual(wos_client.credential(), "test-secret")
        run.assert_not_called()

    def test_wos_redirect_does_not_forward_credentials(self):
        self.assertIsNone(wos_client.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com"))


if __name__ == "__main__":
    unittest.main()
