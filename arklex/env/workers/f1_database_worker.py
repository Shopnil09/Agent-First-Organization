import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from arklex.env.workers.worker import BaseWorker, register_worker
from arklex.env.prompts import load_prompts
from arklex.env.tools.utils import ToolGenerator
from arklex.env.tools.database.f1_utils import F1DatabaseActions  
from arklex.utils.utils import chunk_string
from arklex.utils.graph_state import MessageState
from arklex.utils.model_config import MODEL

logger = logging.getLogger(__name__)


@register_worker
class Formula1Worker(BaseWorker):

    description = "Helps the user with Formula 1-related tasks such as searching for races, drivers, and teams"

    def __init__(self):
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        self.actions = {
            "SearchRace": "Search for a race",
            "SearchDriver": "Search for a driver",
            "SearchTeam": "Search for a team",
            "Others": "Other Formula 1 related queries"
        }
        self.DBActions = F1DatabaseActions() 
        self.action_graph = self._create_action_graph()

    def search_race(self, state: MessageState):
        return self.DBActions.search_race(state)

    def search_driver(self, state: MessageState):
        return self.DBActions.search_driver(state)

    def search_team(self, state: MessageState):
        return self.DBActions.search_team(state)

    def search_circuit(self, state: MessageState):
        return self.DBActions.search_circuit(state)

    def verify_action(self, msg_state: MessageState):
        user_intent = msg_state.orchestrator_message.attribute.get("task", "")
        actions_info = "\n".join([f"{name}: {desc}" for name, desc in self.actions.items()])
        actions_name = ", ".join(self.actions.keys())

        prompts = load_prompts(msg_state.bot_config)
        prompt = PromptTemplate.from_template(prompts["formula1_action_prompt"])  # ✅ F1-specific prompt
        input_prompt = prompt.invoke({
            "user_intent": user_intent,
            "actions_info": actions_info,
            "actions_name": actions_name
        })

        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        logger.info(f"Chunked prompt for deciding F1 DB action: {chunked_prompt}")

        final_chain = self.llm | StrOutputParser()
        try:
            answer = final_chain.invoke(chunked_prompt)
            for action_name in self.actions:
                if action_name in answer:
                    logger.info(f"Chosen F1 action: {action_name}")
                    return action_name
            logger.info("Defaulting to Others")
            return "Others"
        except Exception as e:
            logger.error(f"Error while choosing F1 action: {e}")
            return "Others"

    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        workflow.add_node("SearchRace", self.search_race)
        workflow.add_node("SearchDriver", self.search_driver)
        workflow.add_node("SearchTeam", self.search_team)
        workflow.add_node("Others", ToolGenerator.generate)
        workflow.add_node("tool_generator", ToolGenerator.context_generate)

        workflow.add_conditional_edges(START, self.verify_action)
        workflow.add_edge("SearchRace", "tool_generator")
        workflow.add_edge("SearchDriver", "tool_generator")
        workflow.add_edge("SearchTeam", "tool_generator")

        return workflow

    def _execute(self, msg_state: MessageState):
        self.DBActions.log_in()  # Might just be a placeholder in F1 context
        msg_state.slots = self.DBActions.init_slots(msg_state.slots, msg_state.bot_config)
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        return result
