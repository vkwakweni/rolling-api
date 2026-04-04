from tests.integration.base import BaseIntegrationTestCase
from app.services.ai.orchestrator import AIReportOrchestrator
from app.services.ai.provider import MockAIProvider
from app.repositories.analyses import create_analysis_result
from app.repositories.ai import list_ai_analysis_reports_for_analysis_run, list_agent_traces_by_analysis_run

class TestOrchestrator(BaseIntegrationTestCase):
    mock_provider = MockAIProvider()
    orchestrator = AIReportOrchestrator(model_name="mock_model",
                                        provider=mock_provider)

    def test_no_result_for_run(self) -> None:
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]

        project = self.create_project(analyst_id=analyst_id)
        project_id = project["project_id"]

        analysis_run = self.create_analysis_run(project_id=project_id,
                                                analyst_id=analyst_id)
        analysis_run_id = analysis_run["analysis_run_id"]

        before_ai_report_count = len(list_ai_analysis_reports_for_analysis_run(analyst_id=analyst_id,
                                                                                analysis_run_id=analysis_run_id))
        before_agent_trace_count = len(list_agent_traces_by_analysis_run(analyst_id=analyst_id,
                                                                         analysis_run_id=analysis_run_id))

        with self.assertRaises(ValueError) as e:
            self.orchestrator.generate_ai_report_for_analysis_run(analyst_id=analyst_id,
                                                                  analysis_run_id=analysis_run_id)
        self.assertIn("empty result set", str(e.exception).lower())
        
        after_ai_report_count = len(list_ai_analysis_reports_for_analysis_run(analyst_id=analyst_id,
                                                                               analysis_run_id=analysis_run_id))
        after_agent_trace_count = len(list_agent_traces_by_analysis_run(analyst_id=analyst_id,
                                                                        analysis_run_id=analysis_run_id))
        self.assertEqual(before_ai_report_count, after_ai_report_count)
        self.assertEqual(before_agent_trace_count, after_agent_trace_count)

    def test_no_report_for_run(self) -> None:
        analyst = self.create_analyst()
        analyst_id = analyst["analyst_id"]

        project = self.create_project(analyst_id=analyst_id)
        project_id = project["project_id"]

        analysis_run = self.create_analysis_run(project_id=project_id,
                                                analyst_id=analyst_id)
        analysis_run_id = analysis_run["analysis_run_id"]

        create_analysis_result(analysis_run_id=analysis_run_id,
                               result_type="mock result",
                               result_payload={"param1": "value1"})
        
        before_ai_report_count = len(list_ai_analysis_reports_for_analysis_run(analyst_id=analyst_id,
                                                                                analysis_run_id=analysis_run_id))
        before_agent_trace_count = len(list_agent_traces_by_analysis_run(analyst_id=analyst_id,
                                                                         analysis_run_id=analysis_run_id))

        with self.assertRaises(ValueError) as e:
            self.orchestrator.generate_ai_report_for_analysis_run(analyst_id=analyst_id,
                                                                  analysis_run_id=analysis_run_id)
        self.assertIn("empty report", str(e.exception).lower())

        after_ai_report_count = len(list_ai_analysis_reports_for_analysis_run(analyst_id=analyst_id,
                                                                               analysis_run_id=analysis_run_id))
        after_agent_trace_count = len(list_agent_traces_by_analysis_run(analyst_id=analyst_id,
                                                                        analysis_run_id=analysis_run_id))
        self.assertEqual(before_ai_report_count, after_ai_report_count)
        self.assertEqual(before_agent_trace_count, after_agent_trace_count)

    def test_analyst_cannot_access_run(self) -> None:
        analyst_owner = self.create_analyst()
        analyst_owner_id = analyst_owner["analyst_id"]

        analyst_other = self.create_analyst()
        analyst_other_id = analyst_other["analyst_id"]

        project = self.create_project(analyst_id=analyst_owner_id)
        project_id = project["project_id"]

        analysis_run = self.create_analysis_run(project_id=project_id,
                                                analyst_id=analyst_owner_id)
        analysis_run_id = analysis_run["analysis_run_id"]

        before_ai_report_count = len(list_ai_analysis_reports_for_analysis_run(analyst_id=analyst_owner_id,
                                                                                analysis_run_id=analysis_run_id))
        before_agent_trace_count = len(list_agent_traces_by_analysis_run(analyst_id=analyst_owner_id,
                                                                         analysis_run_id=analysis_run_id))

        with self.assertRaises(PermissionError) as e:
            self.orchestrator.generate_ai_report_for_analysis_run(analyst_id=analyst_other_id,
                                                                  analysis_run_id=analysis_run_id)
        self.assertIn("cannot access", str(e.exception).lower())

        after_ai_report_count = len(list_ai_analysis_reports_for_analysis_run(analyst_id=analyst_owner_id,
                                                                               analysis_run_id=analysis_run_id))
        after_agent_trace_count = len(list_agent_traces_by_analysis_run(analyst_id=analyst_owner_id,
                                                                        analysis_run_id=analysis_run_id))
        self.assertEqual(before_ai_report_count, after_ai_report_count)
        self.assertEqual(before_agent_trace_count, after_agent_trace_count)
