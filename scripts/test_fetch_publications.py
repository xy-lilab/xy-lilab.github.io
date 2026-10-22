import unittest
import xml.etree.ElementTree as ET
import io
import json
import urllib.parse
from unittest.mock import patch

import fetch_publications as subject


class PublicationSearchTests(unittest.TestCase):
    def response(self, count, ids):
        return io.BytesIO(json.dumps({
            "esearchresult": {"count": str(count), "idlist": ids},
        }).encode())

    def test_query_keeps_historical_papers_and_scopes_to_roster(self):
        query = subject.build_pubmed_query(["Ji Li", "Yiya Zhang"])
        self.assertIn('"Li Ji"[Author] OR "Zhang Yiya"[Author]', query)
        self.assertIn('"Central South University"[Affiliation]', query)
        self.assertIn("2020:3000[Date - Publication]", query)
        with self.assertRaises(ValueError):
            subject.build_pubmed_query([])

    @patch.object(subject.time, "sleep")
    @patch.object(subject.urllib.request, "urlopen")
    def test_collects_later_pages_instead_of_truncating(self, urlopen, sleep):
        urlopen.side_effect = [self.response(3, ["1", "2"]), self.response(3, ["3"])]
        self.assertEqual(subject.pubmed_search("query", retmax=2), ["1", "2", "3"])
        params = [urllib.parse.parse_qs(urllib.parse.urlsplit(c.args[0]).query)
                  for c in urlopen.call_args_list]
        self.assertEqual([p["retstart"] for p in params], [["0"], ["2"]])
        self.assertEqual(params[0]["sort"], ["pub date"])
        sleep.assert_called_once()

    @patch.object(subject.urllib.request, "urlopen")
    def test_empty_search_is_valid(self, urlopen):
        urlopen.return_value = self.response(0, [])
        self.assertEqual(subject.pubmed_search("query"), [])

    @patch.object(subject.time, "sleep")
    @patch.object(subject.urllib.request, "urlopen")
    def test_incomplete_or_unstable_results_fail_instead_of_silent_loss(self, urlopen, sleep):
        cases = [
            [self.response(10001, ["1"])],
            [self.response(3, ["1"])],
            [self.response(3, ["1", "2"]), self.response(4, ["3", "4"])],
            [self.response(3, ["1", "2"]), self.response(3, ["2"])],
        ]
        for responses in cases:
            with self.subTest(pages=len(responses)):
                urlopen.side_effect = responses
                with self.assertRaises(RuntimeError):
                    subject.pubmed_search("query", retmax=2)


class AuthorEligibilityTests(unittest.TestCase):
    def test_bilingual_surname_generates_a_stable_ascii_route_key(self):
        paper = {"authors": [{"last": "Yang 杨李"}], "year": "2025",
                 "journal_abbrev": "Genomics Proteomics Bioinformatics",
                 "title": "Macrophage Response"}
        self.assertEqual(subject.generate_bib_key(paper), "yang2025genomicspr_macropha")

    def author(self, fore="Ji", first=True, affiliation="Department of Dermatology, Xiangya Hospital"):
        return {"last": "Li", "fore": fore, "is_first": first,
                "is_last": not first, "affiliations": affiliation.lower()}

    def test_requires_full_name_and_author_specific_lab_affiliation(self):
        self.assertTrue(subject.member_is_key_author([self.author()], "Ji Li"))
        for author in (
            self.author(fore=""), self.author(fore="J"), self.author(fore="Jing"),
            self.author(affiliation="Department of Cardiology, Central South University"),
            self.author(affiliation=""),
        ):
            with self.subTest(author=author):
                self.assertFalse(subject.member_is_key_author([author], "Ji Li"))

    def test_last_position_does_not_establish_corresponding_authorship(self):
        self.assertFalse(subject.member_is_key_author([self.author(first=False)], "Ji Li"))

    def test_pubmed_extraction_does_not_invent_corresponding_author(self):
        record = ET.fromstring('''<PubmedArticle><MedlineCitation><PMID>123</PMID>
          <Article><AuthorList><Author><ForeName>Other</ForeName><LastName>Name</LastName></Author>
          <Author><ForeName>Ji</ForeName><LastName>Li</LastName></Author></AuthorList></Article>
          </MedlineCitation></PubmedArticle>''')
        self.assertEqual(subject.extract_paper_data(record)["corresponding_authors"], "")


class AbstractExtractionTests(unittest.TestCase):
    def test_joins_all_labelled_pubmed_sections(self):
        article = ET.fromstring(
            """
            <Article>
              <Abstract>
                <AbstractText Label="BACKGROUND">First <i>section</i>.</AbstractText>
                <AbstractText Label="METHODS">Second section.</AbstractText>
              </Abstract>
            </Article>
            """
        )

        self.assertEqual(
            subject.extract_abstract_text(article),
            "BACKGROUND: First section. METHODS: Second section.",
        )

    def test_reconstructs_openalex_abstract_in_position_order(self):
        inverted = {"world.": [1], "Hello": [0]}
        self.assertEqual(subject.decode_openalex_abstract(inverted), "Hello world.")

    def test_inserts_abstract_after_pmid(self):
        bib = """@article{example2026,
  title={Example},
  year={2026},
  doi={10.1000/example},
  pmid={123},
  category={aging},
}
"""
        updated = subject.insert_abstracts(bib, {"example2026": "An abstract."})
        self.assertIn("  pmid={123},\n  abstract={An abstract.},\n", updated)

    def test_missing_entry_includes_publication_type_for_source_filtering(self):
        bib = """@article{letter2026,
  title={Example letter},
  year={2026},
  doi={10.1000/letter},
  publication_type={letter},
}
"""
        self.assertEqual(
            subject.missing_abstract_entries(bib),
            [{
                "key": "letter2026",
                "pmid": "",
                "doi": "10.1000/letter",
                "publication_type": "letter",
            }],
        )

    def test_secondary_index_fallback_excludes_non_abstract_article_types(self):
        letter = {"doi": "10.1000/letter", "publication_type": "letter"}
        case_report = {"doi": "10.1000/case", "publication_type": "case_report"}
        original = {"doi": "10.1000/original", "publication_type": "original"}
        self.assertFalse(subject.secondary_index_fallback_allowed(letter))
        self.assertFalse(subject.secondary_index_fallback_allowed(case_report))
        self.assertTrue(subject.secondary_index_fallback_allowed(original))

    def test_maps_semantic_scholar_results_by_doi_and_removes_prefix(self):
        records = [{
            "externalIds": {"DOI": "10.1000/EXAMPLE"},
            "abstract": "Abstract: A verified abstract.",
        }]
        self.assertEqual(
            subject.semantic_scholar_abstracts_from_records(records),
            {"10.1000/example": "A verified abstract."},
        )

    def test_rejects_indexing_fragments_and_non_abstract_types(self):
        original = {"publication_type": "original"}
        correction = {"publication_type": "correction"}
        self.assertEqual(
            subject.abstract_rejection_reason(
                original,
                "The data that support this study are available on request.",
            ),
            "data-availability statement",
        )
        self.assertEqual(
            subject.abstract_rejection_reason(
                original,
                "Please note: The publisher is not responsible for the content or functionality.",
            ),
            "publisher disclaimer",
        )
        self.assertIn(
            "do not carry formal abstracts",
            subject.abstract_rejection_reason(correction, "This corrects an article."),
        )
        self.assertEqual(
            subject.abstract_rejection_reason(original, "A genuine research abstract."),
            "",
        )

    def test_excludes_corrections_errata_and_corrigenda_as_outputs(self):
        for title in (
            "Correction: Example article",
            "Erratum for Example article",
            "Corrigendum to Example article",
        ):
            with self.subTest(title=title):
                self.assertFalse(subject.is_publication_output({
                    "title": title,
                    "abstract": "",
                }))
        self.assertTrue(subject.is_publication_output({
            "title": "A genuine research article",
            "abstract": "A genuine research abstract.",
        }))


if __name__ == "__main__":
    unittest.main()
