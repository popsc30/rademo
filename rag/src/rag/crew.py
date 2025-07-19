from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from rag.tools.rerank_tool import RerankTool

@CrewBase
class RagCrew():
    """Defines the crew responsible for generating the final report."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def search_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['search_synthesizer'],
            tools=[RerankTool()],
            verbose=True
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
            verbose=True
        )

    @task
    def synthesize_guide_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_guide_task'],
            agent=self.search_synthesizer()
        )

    @task
    def report_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_generation_task'],
            agent=self.report_writer(),
            output_file='final_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates and configures the crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
