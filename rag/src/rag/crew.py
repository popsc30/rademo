from unittest.mock import MagicMock
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from rag.tools.rerank_tool import RerankTool

@CrewBase
class Rag():
    """Defines the crew responsible for generating the final report."""
    
    def __init__(self, mock: bool = False):
        self.mock = mock

    @agent
    def search_synthesizer(self) -> Agent:
        """
        An agent specialized in synthesizing information from a list of documents.
        """
        agent_config = {
            'config': self.agents_config['search_synthesizer'],
            'verbose': True,
            'tools': [RerankTool()]
        }
        if self.mock:
            print("Crew is running in mock mode. Using MagicMock for LLM.")
            mock_llm = MagicMock()
            mock_llm.model_name = "mock_llm"
            mock_llm.invoke.return_value = "This is a preliminary guide from the mock LLM."
            mock_llm.call = mock_llm.invoke
            agent_config['llm'] = mock_llm
            
        return Agent(**agent_config)

    @agent
    def report_writer(self) -> Agent:
        """
        An agent specialized in taking structured, step-by-step guides
        and formatting them into polished, user-friendly reports.
        """
        agent_config = {
            'config': self.agents_config['report_writer'],
            'verbose': True
        }
        if self.mock:
            print("Crew is running in mock mode. Using MagicMock for LLM.")
            mock_llm = MagicMock()
            mock_llm.model_name = "mock_llm"
            mock_llm.invoke.return_value = "This is a final report from the mock LLM."
            mock_llm.call = mock_llm.invoke
            agent_config['llm'] = mock_llm
            
        return Agent(**agent_config)

    @task
    def synthesize_guide_task(self) -> Task:
        """
        The task of synthesizing a preliminary guide from a list of documents.
        """
        return Task(
            config=self.tasks_config['synthesize_guide_task'],
            agent=self.search_synthesizer()
        )

    @task
    def report_generation_task(self) -> Task:
        """
        The task of transforming a preliminary guide into a final,
        well-formatted report.
        """
        return Task(
            config=self.tasks_config['report_generation_task'],
            agent=self.report_writer(),
            output_file='final_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates and configures the crew."""
        return Crew(
            agents=[self.search_synthesizer(), self.report_writer()],
            tasks=[self.synthesize_guide_task(), self.report_generation_task()],
            process=Process.sequential,
            verbose=True,
        )
