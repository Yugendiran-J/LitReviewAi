import json
import os
from threading import Barrier
from types import SimpleNamespace
from unittest import TestCase, mock

from fastapi import HTTPException

from app.ai import candidate_service
from app.ai import pipeline_service as ai_pipeline_service
from app.services import literature_source_service
from app.services import ollama_service
from app.services import pubmed_service
from app.services import screening_model2_service
from app.ai import screening_model2_service as ai_screening_model2_service
from app.routes import literature_pipeline_router


class LiteratureSourceTests(TestCase):
    def test_pubmed_network_failure_is_reported_without_raw_request_details(self):
        with mock.patch.object(
            pubmed_service.requests,
            "get",
            side_effect=pubmed_service.requests.ConnectionError(
                "connection failed"
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "PubMed search request failed",
            ):
                pubmed_service.search_pubmed("AI literature screening")

    def test_ieee_xplore_requires_its_own_api_key(self):
        with mock.patch.dict(os.environ, {"IEEE_XPLORE_API_KEY": ""}):
            with self.assertRaisesRegex(
                ValueError,
                "IEEE_XPLORE_API_KEY",
            ):
                literature_source_service.search_ieee_xplore("machine learning")

    def test_source_availability_explains_api_limitations(self):
        with mock.patch.dict(
            os.environ,
            {"IEEE_XPLORE_API_KEY": "", "SERPAPI_API_KEY": ""},
        ):
            sources = {
                source["id"]: source
                for source in literature_source_service.get_literature_sources()
            }

        self.assertFalse(sources["ieee_xplore"]["available"])
        self.assertIn("IEEE_XPLORE_API_KEY", sources["ieee_xplore"]["description"])
        self.assertFalse(sources["google_scholar"]["available"])
        self.assertIn(
            "SERPAPI_API_KEY",
            sources["google_scholar"]["description"],
        )
        self.assertFalse(sources["researchgate"]["available"])

    def test_google_scholar_availability_requires_serpapi_key(self):
        with mock.patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}):
            sources = {
                source["id"]: source
                for source in literature_source_service.get_literature_sources()
            }

        self.assertTrue(sources["google_scholar"]["available"])

    def test_google_scholar_search_maps_serpapi_results(self):
        captured = {}

        def fake_get(url, params, headers, timeout):
            captured.update(
                url=url,
                params=params,
                headers=headers,
                timeout=timeout,
            )
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {
                    "organic_results": [
                        {
                            "title": "Evidence-based AI research",
                            "link": "https://example.test/paper",
                            "snippet": "A paper abstract.",
                            "publication_info": {
                                "authors": [
                                    {"name": "Example Author"},
                                    {"name": "Second Author"},
                                ],
                                "summary": "Example Author, Second Author - Journal, 2025",
                                "year": 2025,
                                "journal": "Example Journal",
                            },
                        },
                    ],
                },
            )

        with (
            mock.patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"}),
            mock.patch.object(
                literature_source_service.requests,
                "get",
                side_effect=fake_get,
            ),
        ):
            papers = literature_source_service.search_google_scholar(
                "AI AND research",
                max_results=25,
            )

        self.assertEqual(captured["url"], "https://serpapi.com/search.json")
        self.assertEqual(captured["params"]["engine"], "google_scholar")
        self.assertEqual(captured["params"]["api_key"], "test-key")
        self.assertEqual(captured["params"]["q"], "AI research")
        self.assertEqual(captured["params"]["num"], 20)
        self.assertEqual(
            papers,
            [
                {
                    "title": "Evidence-based AI research",
                    "authors": "Example Author, Second Author",
                    "abstract": "A paper abstract.",
                    "publication_year": 2025,
                    "journal": "Example Journal",
                    "doi": None,
                    "url": "https://example.test/paper",
                    "source": "Google Scholar",
                },
            ],
        )

    def test_google_scholar_errors_do_not_expose_serpapi_key(self):
        api_key = "test-secret-key"
        failure = literature_source_service.requests.Timeout(
            f"request failed for ?api_key={api_key}"
        )

        with (
            mock.patch.dict(os.environ, {"SERPAPI_API_KEY": api_key}),
            mock.patch.object(
                literature_source_service.requests,
                "get",
                side_effect=failure,
            ),
        ):
            with self.assertRaises(RuntimeError) as raised:
                literature_source_service.search_google_scholar("AI research")

        self.assertNotIn(api_key, str(raised.exception))

    def test_ieee_xplore_search_maps_papers(self):
        captured = {}

        def fake_get(url, params, headers, timeout):
            captured.update(
                url=url,
                params=params,
                headers=headers,
                timeout=timeout,
            )
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {
                    "articles": [
                        {
                            "article_title": "Evidence-based AI research",
                            "authors": {
                                "authors": [
                                    {"full_name": "Example Author"},
                                ],
                            },
                            "abstract": "A paper abstract.",
                            "publication_year": "2025",
                            "publication_title": "Example Journal",
                            "doi": "10.1234/example",
                            "html_url": (
                                "https://ieeexplore.ieee.org/document/1"
                            ),
                        },
                    ],
                },
            )

        with (
            mock.patch.dict(os.environ, {"IEEE_XPLORE_API_KEY": "test-key"}),
            mock.patch.object(
                literature_source_service.requests,
                "get",
                side_effect=fake_get,
            ),
        ):
            papers = literature_source_service.search_ieee_xplore(
                "AI AND research",
                max_results=7,
            )

        self.assertTrue(captured["url"].endswith("/search/articles"))
        self.assertEqual(captured["params"]["apikey"], "test-key")
        self.assertEqual(captured["params"]["max_records"], 7)
        self.assertEqual(
            papers,
            [
                {
                    "title": "Evidence-based AI research",
                    "authors": "Example Author",
                    "abstract": "A paper abstract.",
                    "publication_year": 2025,
                    "journal": "Example Journal",
                    "doi": "10.1234/example",
                    "url": "https://ieeexplore.ieee.org/document/1",
                    "source": "IEEE Xplore",
                },
            ],
        )

    def test_ieee_xplore_errors_do_not_expose_api_key(self):
        api_key = "test-secret-key"
        failure = literature_source_service.requests.Timeout(
            f"request failed for ?apikey={api_key}"
        )

        with (
            mock.patch.dict(os.environ, {"IEEE_XPLORE_API_KEY": api_key}),
            mock.patch.object(
                literature_source_service.requests,
                "get",
                side_effect=failure,
            ),
        ):
            with self.assertRaises(RuntimeError) as raised:
                literature_source_service.search_ieee_xplore("machine learning")

        self.assertNotIn(api_key, str(raised.exception))

    def test_ieee_xplore_reports_rejected_credentials_without_exposing_key(self):
        api_key = "test-secret-key"
        response = literature_source_service.requests.Response()
        response.status_code = 403
        failure = literature_source_service.requests.HTTPError(
            f"request failed for ?apikey={api_key}",
            response=response,
        )

        with (
            mock.patch.dict(os.environ, {"IEEE_XPLORE_API_KEY": api_key}),
            mock.patch.object(
                literature_source_service.requests,
                "get",
                side_effect=failure,
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "rejected the API credentials \\(HTTP 403\\)",
            ) as raised:
                literature_source_service.search_ieee_xplore("machine learning")

        self.assertNotIn(api_key, str(raised.exception))

    def test_candidate_collection_uses_successful_sources_when_one_fails(self):
        paper = {
            "title": "AI-assisted systematic review screening",
            "doi": "10.1234/test",
            "source": "Crossref",
        }
        scholar_paper = {
            "title": "Google Scholar result",
            "doi": "10.1234/scholar",
            "source": "Google Scholar",
        }
        with (
            mock.patch.object(
                candidate_service,
                "search_openalex",
                side_effect=RuntimeError("OpenAlex is unavailable"),
            ),
            mock.patch.object(
                candidate_service,
                "search_crossref",
                return_value=[paper.copy()],
            ),
            mock.patch.object(
                candidate_service,
                "search_google_scholar",
                return_value=[scholar_paper],
            ),
        ):
            result = candidate_service.collect_candidate_papers(
                ["AI literature screening"],
                sources=["openalex", "crossref", "google_scholar"],
            )

        self.assertEqual(result["total_candidates"], 2)
        self.assertEqual(
            result["source_errors"],
            ["openalex: OpenAlex is unavailable"],
        )
        self.assertEqual(result["papers"][0]["source"], "Crossref")
        self.assertEqual(result["source_counts"]["google_scholar"], 1)

    def test_candidate_collection_reports_when_all_selected_sources_fail(self):
        with mock.patch.object(
            candidate_service,
            "search_openalex",
            side_effect=RuntimeError("OpenAlex is unavailable"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Candidate search failed for all selected sources.*OpenAlex is unavailable",
            ):
                candidate_service.collect_candidate_papers(
                    ["AI literature screening"],
                    sources=["openalex"],
                )

    def test_candidate_sources_run_concurrently_in_stable_order(self):
        barrier = Barrier(3, timeout=2)

        def make_search(title, doi):
            def search(query, max_results):
                barrier.wait()
                return [{"title": title, "doi": doi}]

            return search

        with (
            mock.patch.object(
                candidate_service,
                "search_openalex",
                side_effect=make_search("OpenAlex paper", "10.1234/a"),
            ),
            mock.patch.object(
                candidate_service,
                "search_crossref",
                side_effect=make_search("Crossref paper", "10.1234/b"),
            ),
            mock.patch.object(
                candidate_service,
                "search_arxiv",
                side_effect=make_search("arXiv paper", "10.1234/c"),
            ),
        ):
            result = candidate_service.collect_candidate_papers(
                ["AI literature screening"],
                sources=["openalex", "crossref", "arxiv"],
            )

        self.assertEqual(
            [paper["title"] for paper in result["papers"]],
            ["OpenAlex paper", "Crossref paper", "arXiv paper"],
        )
        self.assertEqual(result["total_candidates"], 3)

    def test_model2_screens_concurrently_and_commits_on_caller_thread(self):
        barrier = Barrier(3, timeout=2)
        papers = [
            SimpleNamespace(
                id=paper_id,
                title=f"Paper {paper_id}",
                abstract="Abstract",
                full_text=None,
                publication_year=2025,
                source="Crossref",
                doi=f"10.1234/{paper_id}",
                url="https://example.test/paper",
            )
            for paper_id in range(1, 4)
        ]

        class FakeQuery:
            def filter(self, *_args):
                return self

            def order_by(self, *_args):
                return self

            def all(self):
                return papers

        class FakeDatabase:
            def __init__(self):
                self.added = []
                self.commits = 0

            def query(self, *_args):
                return FakeQuery()

            def add(self, record):
                self.added.append(record)

            def commit(self):
                self.commits += 1

        def fake_screen(**_kwargs):
            barrier.wait()
            return {
                "decision": "Include",
                "confidence": 0.9,
                "reason": "Relevant",
                "population_match": True,
                "intervention_match": True,
                "comparison_match": True,
                "outcome_match": True,
                "study_type_match": True,
            }

        db = FakeDatabase()
        with mock.patch.object(
            screening_model2_service,
            "screen_candidate_paper",
            side_effect=fake_screen,
        ):
            result = screening_model2_service.screen_project_papers(
                db=db,
                project_id=1,
                population="population",
                intervention="intervention",
                comparison="comparison",
                outcome="outcome",
                study_type="study",
            )

        self.assertEqual(result["ai_calls"], 3)
        self.assertEqual(
            [paper["paper_id"] for paper in result["results"]],
            [1, 2, 3],
        )
        self.assertEqual(len(db.added), 3)
        self.assertEqual(db.commits, 1)

    def test_ollama_generation_uses_local_model_and_non_streaming_api(self):
        response = mock.Mock()
        response.ok = True
        response.json.return_value = {"response": "Local model response"}

        with mock.patch.object(
            ollama_service.requests,
            "post",
            return_value=response,
        ) as post:
            result = ollama_service.generate_text(
                "Test prompt",
                format="json",
            )

        self.assertEqual(result, "Local model response")
        self.assertEqual(
            post.call_args.args[0],
            "http://127.0.0.1:11434/api/generate",
        )
        expected_payload = {
            "model": ollama_service.OLLAMA_MODEL,
            "prompt": "/no_think\nTest prompt",
            "stream": False,
            "format": "json",
            "options": {
                "num_predict": ollama_service.OLLAMA_MAX_OUTPUT_TOKENS,
            },
        }
        if ollama_service.OLLAMA_MODEL.lower().startswith("qwen3"):
            expected_payload["think"] = False

        self.assertEqual(post.call_args.kwargs["json"], expected_payload)

    def test_ollama_generation_accepts_a_smaller_output_limit(self):
        response = mock.Mock()
        response.ok = True
        response.json.return_value = {"response": "Generated JSON"}

        with mock.patch.object(
            ollama_service.requests,
            "post",
            return_value=response,
        ) as post:
            ollama_service.generate_text(
                "Test prompt",
                format="json",
                max_output_tokens=256,
            )

        self.assertEqual(
            post.call_args.kwargs["json"]["options"]["num_predict"],
            256,
        )

    def test_model2_uses_a_bounded_json_output_limit(self):
        response = {
            "decision": "Include",
            "confidence": 90,
            "reason": "The abstract matches the stated criteria.",
            "picos_analysis": {
                key: "Match"
                for key in (
                    "population",
                    "intervention",
                    "comparison",
                    "outcome",
                    "study_type",
                )
            },
        }
        with mock.patch.object(
            ai_screening_model2_service,
            "generate_text",
            return_value=json.dumps(response),
        ) as generate:
            ai_screening_model2_service.screen_candidate_paper(
                title="Relevant study",
                abstract="A relevant study abstract.",
                population="Adults",
                intervention="Treatment",
                comparison="Control",
                outcome="Recovery",
                study_type="Randomized trial",
            )

        self.assertEqual(
            generate.call_args.kwargs["max_output_tokens"],
            256,
        )

    def test_ai_model2_retries_malformed_json_once(self):
        response = {
            "decision": "Include",
            "confidence": 90,
            "reason": "The abstract matches the stated criteria.",
            "picos_analysis": {
                key: "Match"
                for key in (
                    "population",
                    "intervention",
                    "comparison",
                    "outcome",
                    "study_type",
                )
            },
        }
        with mock.patch.object(
            ai_screening_model2_service,
            "generate_text",
            side_effect=["{invalid", json.dumps(response)],
        ) as generate:
            result = ai_screening_model2_service.screen_candidate_paper(
                title="Relevant study",
                abstract="A relevant study abstract.",
                population="Adults",
                intervention="Treatment",
                comparison="Control",
                outcome="Recovery",
                study_type="Randomized trial",
            )

        self.assertEqual(generate.call_count, 2)
        self.assertEqual(result["decision"], "Include")

    def test_ai_model2_retries_invalid_picos_once(self):
        response = {
            "decision": "Include",
            "confidence": 90,
            "reason": "The abstract matches the stated criteria.",
            "picos_analysis": {
                key: "Match"
                for key in (
                    "population",
                    "intervention",
                    "comparison",
                    "outcome",
                    "study_type",
                )
            },
        }
        invalid_response = {
            **response,
            "picos_analysis": {"population": "Match"},
        }
        with mock.patch.object(
            ai_screening_model2_service,
            "generate_text",
            side_effect=[
                json.dumps(invalid_response),
                json.dumps(response),
            ],
        ) as generate:
            result = ai_screening_model2_service.screen_candidate_paper(
                title="Relevant study",
                abstract="A relevant study abstract.",
                population="Adults",
                intervention="Treatment",
                comparison="Control",
                outcome="Recovery",
                study_type="Randomized trial",
            )

        self.assertEqual(generate.call_count, 2)
        self.assertEqual(result["picos_analysis"]["study_type"], "Match")

    def test_ai_model2_batches_selected_papers_and_accepts_criteria(self):
        papers = [
            SimpleNamespace(
                id=paper_id,
                title=f"Paper {paper_id}",
                abstract=f"Abstract {paper_id}",
                publication_year=2025,
                source="PubMed",
                doi=f"10.1234/{paper_id}",
                url=f"https://example.test/{paper_id}",
            )
            for paper_id in (1, 2)
        ]

        class FakeQuery:
            def __init__(self, rows=None):
                self.rows = rows

            def filter(self, *_args):
                return self

            def all(self):
                return self.rows

            def first(self):
                return None

        class FakeDatabase:
            def __init__(self):
                self.added = []
                self.commits = 0

            def query(self, model):
                if model is ai_screening_model2_service.Paper:
                    return FakeQuery(papers)
                return FakeQuery()

            def add(self, record):
                self.added.append(record)

            def commit(self):
                self.commits += 1

        screening_results = [
            {
                "decision": "Include",
                "confidence": 90,
                "reason": "Meets the supplied criteria.",
                "picos_analysis": {
                    key: "Match"
                    for key in (
                        "population",
                        "intervention",
                        "comparison",
                        "outcome",
                        "study_type",
                    )
                },
            },
            {
                "decision": "Uncertain",
                "confidence": 55,
                "reason": "The abstract does not report the outcome.",
                "picos_analysis": {
                    "population": "Match",
                    "intervention": "Match",
                    "comparison": "Not reported",
                    "outcome": "Not reported",
                    "study_type": "Partial",
                },
            },
        ]
        db = FakeDatabase()
        with mock.patch.object(
            ai_screening_model2_service,
            "screen_candidate_paper",
            side_effect=screening_results,
        ) as screen_paper:
            results = ai_screening_model2_service.screen_project_papers(
                db=db,
                project_id=7,
                population="Adults",
                intervention="Treatment",
                comparison="Control",
                outcome="Recovery",
                study_type="Randomized trial",
                paper_ids=[1, 2],
                restriction="English language",
                limitations="Exclude pediatric-only studies.",
            )

        self.assertEqual(
            screen_paper.call_count,
            2,
        )
        for call in screen_paper.call_args_list:
            self.assertEqual(call.kwargs["restriction"], "English language")
            self.assertEqual(
                call.kwargs["limitations"],
                "Exclude pediatric-only studies.",
            )
        self.assertEqual(
            [result["decision"] for result in results],
            ["Include", "Uncertain"],
        )
        self.assertEqual(len(db.added), 2)
        self.assertEqual(db.commits, 3)

    def test_literature_pipeline_returns_model2_summary_expected_by_api(self):
        paper = SimpleNamespace(
            id=1,
            title="Relevant study",
            abstract="Adults received the intervention and outcomes were measured.",
            full_text=None,
            publication_year=2025,
            authors="A. Researcher",
            journal="Example Journal",
            doi="10.1234/example",
            url="https://example.test/paper",
            source="PubMed",
            pdf_path=None,
        )

        class FakeQuery:
            def __init__(self, rows):
                self.rows = rows

            def filter(self, *_args):
                return self

            def all(self):
                return self.rows

        class FakeDatabase:
            def __init__(self):
                self.paper_queries = 0

            def query(self, _model):
                self.paper_queries += 1
                return FakeQuery([paper] if self.paper_queries == 1 else [])

        screen_result = {
            "paper_id": paper.id,
            "title": paper.title,
            "decision": "Include",
            "confidence": 90,
            "reason": "Meets the stated criteria.",
            "picos_analysis": {
                "population": "Match",
                "intervention": "Match",
                "comparison": "Match",
                "outcome": "Match",
                "study_type": "Match",
            },
            "cached": False,
        }
        db = FakeDatabase()
        with (
            mock.patch.object(
                ai_pipeline_service,
                "generate_search_queries",
                return_value={"queries": ["research query"]},
            ),
            mock.patch.object(
                ai_pipeline_service,
                "collect_candidate_papers",
                return_value={
                    "papers": [{"title": paper.title}],
                    "total_candidates": 1,
                    "source_errors": [],
                },
            ),
            mock.patch.object(
                ai_pipeline_service,
                "save_candidate_papers",
                return_value=[paper],
            ),
            mock.patch.object(
                ai_pipeline_service,
                "update_candidate_abstracts",
                return_value={"updated": 1},
            ),
            mock.patch.object(
                ai_pipeline_service,
                "screen_project_papers",
                return_value=[screen_result],
            ),
        ):
            result = ai_pipeline_service.run_literature_pipeline(
                db=db,
                project_id=7,
                research_topic="Research topic",
                research_question="Research question",
                population="Adults",
                intervention="Treatment",
                comparison="Control",
                outcome="Recovery",
                study_type="Randomized trial",
                restriction="English language",
                limitations="Exclude pediatric-only studies.",
                sources=["pubmed"],
            )

        self.assertEqual(result["model2"]["total_screened"], 1)
        self.assertEqual(result["model2"]["included"], [screen_result])
        self.assertEqual(result["model2"]["shortlist"], [screen_result])

    def test_literature_endpoint_reports_ollama_timeouts_as_504(self):
        class FakeQuery:
            def filter(self, *_args):
                return self

            def first(self):
                return object()

        class FakeDatabase:
            def __init__(self):
                self.rollbacks = 0

            def query(self, _model):
                return FakeQuery()

            def rollback(self):
                self.rollbacks += 1

        db = FakeDatabase()
        request = literature_pipeline_router.LiteraturePipelineRequest(
            project_id=7,
            keyword="Research topic",
            sources=["pubmed"],
        )
        with (
            mock.patch.object(
                literature_pipeline_router,
                "run_end_to_end_pipeline",
                side_effect=ollama_service.OllamaTimeoutError("Ollama timed out."),
            ),
            self.assertRaises(HTTPException) as raised,
        ):
            literature_pipeline_router.run_literature_review(
                request=request,
                db=db,
                current_user=SimpleNamespace(id=3),
            )

        self.assertEqual(raised.exception.status_code, 504)
        self.assertEqual(db.rollbacks, 1)

    def test_ollama_read_timeout_uses_the_specific_timeout_error(self):
        with mock.patch.object(
            ollama_service.requests,
            "post",
            side_effect=ollama_service.requests.Timeout(),
        ):
            with self.assertRaises(ollama_service.OllamaTimeoutError):
                ollama_service.generate_text("Test prompt")

    def test_ollama_connection_failure_has_actionable_message(self):
        with mock.patch.object(
            ollama_service.requests,
            "post",
            side_effect=ollama_service.requests.ConnectionError(),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Cannot connect to Ollama.*ollama serve",
            ):
                ollama_service.generate_text("Test prompt")

    def test_ollama_reports_missing_model_from_local_server(self):
        response = mock.Mock()
        response.ok = False
        response.status_code = 404
        response.json.return_value = {
            "error": "model not found; try pulling it first"
        }

        with mock.patch.object(
            ollama_service.requests,
            "post",
            return_value=response,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Ollama request failed \\(404\\).*model not found",
            ):
                ollama_service.generate_text("Test prompt")
