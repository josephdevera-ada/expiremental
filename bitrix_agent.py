from langchain_community.llms.ollama import Ollama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType
import requests

from typing import List, Union, Generator, Iterator
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        pass

    def __init__(self):
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "openai_pipeline"
        
        self.name = "Bitrix Agent"
        BITRIX_BASE_URL: str = ""
        BITRIX_API_TOKEN: str = ""
        
        REQUEST_HEADERS: dict[str: str] = {
            "Authorization": f"Basic {self.pipeline.valves.BITRIX_API_TOKEN}",
            "Content-Type": "application/json",
        }
        pass

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass
    
    async def get_rpa_items(self) -> dict:
        """
        Execute the API request and get the profile information for a given user ID.
        :param user_id: The ID of the user to fetch.
        :return: A string that returns the correct value
        """
        if self.pipeline.valves.BITRIX_BASE_URL == "" or self.pipeline.valves.BITRIX_API_TOKEN:
            return "Base url and or token not set."
        
        method = f"{self.pipeline.valves.API_BASE_URL}/rpa.item.list"

        try:
            response = requests.get(method, headers=self.pipeline.valves.REQUEST_HEADERS)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            data = response.json()

            if "error" in data:
                return f"Error fetching list information: {data['error']}"

            return data
        except requests.RequestException as e:
            return f"Error fetching list information: {str(e)}"

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        llm = Ollama(
            base_url='https://gpt.ada.asia/ollama',
            headers={'Authorization': "Bearer sk-08ea5fd0508b4bc9b3a718f40b905994"},
            model='llama3:8b',
        )

        db = SQLDatabase.from_uri(
            'mysql+pymysql://vapor:ucM8DexNZh0V2E6MhnGXbdi9vF5qFdfCQD0IMuUw@fbx-development.cfmcz3ssrek5.ap-southeast-1.rds.amazonaws.com:3306/vapor',
            sample_rows_in_table_info=3,
        )

        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
        )

        response = agent_executor.invoke(user_message)
        
        return response
