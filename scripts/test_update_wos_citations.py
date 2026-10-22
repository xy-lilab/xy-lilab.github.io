import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import update_wos_citations as subject


class WoSCitationTests(unittest.TestCase):
    entries = [{"key": "paper", "doi": "10.1000/example"}]

    def hit(self, uid="WOS:1", doi="10.1000/example", citations=None):
        return {"uid": uid, "identifiers": {"doi": doi},
                "citations": citations if citations is not None else [{"db": "WOS", "count": 0}]}

    def test_zero_is_a_real_matched_count_but_missing_is_not_zero(self):
        matched = subject.match_records(self.entries, [self.hit()])["paper"]
        missing = subject.match_records(self.entries, [self.hit(doi="10.1000/other")])["paper"]
        self.assertEqual((matched["status"], matched["citations"]), ("matched", 0))
        self.assertEqual(missing["status"], "unmatched")
        self.assertNotIn("citations", missing)

    def test_only_core_collection_count_is_used(self):
        hit = self.hit(citations=[{"db": "OTHER", "count": 99}, {"db": "WOS", "count": 7}])
        self.assertEqual(subject.match_records(self.entries, [hit])["paper"]["citations"], 7)
        hit["citations"] = [{"db": "OTHER", "count": 99}]
        record = subject.match_records(self.entries, [hit])["paper"]
        self.assertEqual(record["status"], "count_unavailable")
        self.assertNotIn("citations", record)

    def test_multiple_distinct_records_do_not_get_summed(self):
        record = subject.match_records(self.entries, [self.hit(), self.hit(uid="WOS:2")])["paper"]
        self.assertEqual(record["status"], "ambiguous")
        self.assertNotIn("citations", record)

    def test_early_access_duplicate_is_resolved_only_if_identity_and_counts_agree(self):
        early = self.hit()
        early.update(title="Study of <i>ATF7</i>", types=["Article", "Early Access"],
                     names={"authors": [{"wosStandard": "Li, J"}]})
        final = self.hit(uid="WOS:2")
        final.update(title="Study of ATF7", types=["Article"], names=early["names"],
                     source={"volume": "14", "pages": {"range": "10-20"}})
        record = subject.match_records(self.entries, [early, final])["paper"]
        self.assertEqual((record["status"], record["uid"], record["citations"]), ("matched", "WOS:2", 0))
        self.assertEqual(record["alternate_uids"], ["WOS:1"])
        final["citations"] = [{"db": "WOS", "count": 2}]
        self.assertEqual(subject.match_records(self.entries, [early, final])["paper"]["status"], "ambiguous")

    @patch.object(subject.time, "sleep")
    @patch.object(subject.subprocess, "run")
    def test_all_result_pages_are_retrieved(self, run, sleep):
        hits = [self.hit(uid=f"WOS:{n}") for n in range(51)]
        run.side_effect = [subprocess.CompletedProcess([], 0, json.dumps({
            "metadata": {"total": 51}, "hits": batch, "_request": {"database": "WOS"},
        })) for batch in (hits[:50], hits[50:])]
        self.assertEqual(len(subject.fetch_batch(self.entries)), 51)
        self.assertEqual(run.call_args_list[1].args[0][-1], "2")

    @patch.object(subject, "write_snapshot")
    @patch.object(subject, "fetch_batch")
    @patch.object(subject, "extract_dois_from_bib")
    def test_partial_api_failure_does_not_replace_previous_snapshot(self, extract, fetch, write):
        extract.return_value = self.entries + [{"key": "other", "doi": "10.1000/other"}]
        fetch.side_effect = [[self.hit()], RuntimeError("API unavailable")]
        with patch.object(subject, "BATCH_SIZE", 1), patch.object(sys, "argv", ["test"]), \
                patch("sys.stdout", new_callable=io.StringIO):
            with self.assertRaises(RuntimeError):
                subject.main()
        write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
