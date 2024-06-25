from langchain_community.llms.ollama import Ollama
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType

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
        self.name = "Sql Agent"
        pass

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

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
