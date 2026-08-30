import unittest
import xml.etree.ElementTree as ET

import fetch_publications as subject


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


if __name__ == "__main__":
    unittest.main()
