import os
import sqlite3
import logging
import pandas as pd

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from arklex.utils.utils import chunk_string
from arklex.utils.model_config import MODEL
from arklex.utils.graph_state import Slot, SlotDetail, MessageState, StatusEnum
from arklex.env.prompts import load_prompts

logger = logging.getLogger(__name__)

DBNAME = "formula1_db.sqlite"

F1_SLOTS = [
    {
        "name": "name",
        "type": "string",
        "value": "",
        "description": "Name of the race",
        "prompt": "What race are you interested in?"
    },
    {
        "name": "season",
        "type": "integer",
        "value": "",
        "description": "Season year (e.g. 2024)",
        "prompt": "Which season are you referring to?"
    },
    {
        "name": "round",
        "type": "integer",
        "value": "",
        "description": "Round number of the race",
        "prompt": "Which round of the season?"
    },
    {
        "name": "location",
        "type": "string",
        "value": "",
        "description": "Location of the circuit",
        "prompt": "What circuit location are you referring to?"
    }
]


class F1DatabaseActions:
    def __init__(self):
        self.db_path = os.path.join(os.environ.get("DATA_DIR"), DBNAME)
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)

    def log_in(self):
        logger.info("No user validation needed for F1. Returning True.")
        return True

    def init_slots(self, slots: list[Slot], bot_config) -> list[Slot]:
        if not slots:
            slots = F1_SLOTS
        self.slots = []
        self.slot_prompts = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for slot in slots:
            query = f"SELECT DISTINCT {slot['name']} FROM race"
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                value_list = [r[0] for r in results]
                self.slots.append(self.verify_slot(slot, value_list, bot_config))
                if not self.slots[-1].confirmed:
                    self.slot_prompts.append(slot["prompt"])
            except Exception as e:
                logger.warning(f"Slot '{slot['name']}' failed during DB query: {e}")
        cursor.close()
        conn.close()
        return self.slots

    def verify_slot(self, slot: Slot, value_list: list, bot_config) -> Slot:
        slot_detail = SlotDetail(**slot, verified_value="", confirmed=False)
        prompts = load_prompts(bot_config)
        prompt = PromptTemplate.from_template(prompts["formula1_slot_prompt"])
        input_prompt = prompt.invoke({
            "slot": {"name": slot["name"], "description": slot["description"], "slot": slot["type"]},
            "value": slot["value"],
            "value_list": value_list
        })
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        logger.info(f"F1 Slot Verification Prompt: {chunked_prompt}")

        final_chain = self.llm | StrOutputParser()
        try:
            answer = final_chain.invoke(chunked_prompt)
            logger.info(f"Slot verification result: {answer}")
            for value in value_list:
                if str(value).lower() in answer.lower():
                    slot_detail.verified_value = value
                    slot_detail.confirmed = True
                    return slot_detail
        except Exception as e:
            logger.error(f"F1 slot verification error: {e}")
        return slot_detail

    def search_race(self, msg_state: MessageState) -> MessageState:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT race.name AS race_name, season, round, race.date,
                   circuit.name AS circuit_name, circuit.location, circuit.country
            FROM race
            JOIN circuit ON race.circuit_id = circuit.id
            WHERE 1 = 1
        """
        params = []
        for slot in self.slots:
            if slot.confirmed:
                col = f"race.{slot.name}" if slot.name in ['name', 'season', 'round'] else f"circuit.{slot.name}"
                query += f" AND {col} = ?"
                params.append(slot.verified_value)

        query += " LIMIT 10"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]
        cursor.close()
        conn.close()

        if not rows:
            msg_state.status = StatusEnum.INCOMPLETE
            msg_state.message_flow = "No races found matching your criteria."
        else:
            results = [dict(zip(column_names, row)) for row in rows]
            df = pd.DataFrame(results)
            msg_state.status = StatusEnum.COMPLETE
            msg_state.message_flow = "Matching races:\n" + df.to_string(index=False)
        return msg_state

    def search_driver(self, msg_state: MessageState) -> MessageState:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT first_name, last_name, nationality, date_of_birth
            FROM driver
            WHERE 1 = 1
        """
        params = []
        for slot in self.slots:
            if slot.confirmed and slot.name in ['first_name', 'last_name', 'nationality']:
                query += f" AND {slot.name} = ?"
                params.append(slot.verified_value)

        query += " LIMIT 10"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]
        cursor.close()
        conn.close()

        if not rows:
            msg_state.status = StatusEnum.INCOMPLETE
            msg_state.message_flow = "No drivers found matching your criteria."
        else:
            results = [dict(zip(column_names, row)) for row in rows]
            df = pd.DataFrame(results)
            msg_state.status = StatusEnum.COMPLETE
            msg_state.message_flow = "Matching drivers:\n" + df.to_string(index=False)
        return msg_state

    def search_team(self, msg_state: MessageState) -> MessageState:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT name, base_country, principal_name
            FROM team
            WHERE 1 = 1
        """
        params = []
        for slot in self.slots:
            if slot.confirmed and slot.name in ['name', 'base_country']:
                query += f" AND {slot.name} = ?"
                params.append(slot.verified_value)

        query += " LIMIT 10"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [col[0] for col in cursor.description]
        cursor.close()
        conn.close()

        if not rows:
            msg_state.status = StatusEnum.INCOMPLETE
            msg_state.message_flow = "No teams found matching your criteria."
        else:
            results = [dict(zip(column_names, row)) for row in rows]
            df = pd.DataFrame(results)
            msg_state.status = StatusEnum.COMPLETE
            msg_state.message_flow = "Matching teams:\n" + df.to_string(index=False)
        return msg_state
