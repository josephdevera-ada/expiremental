import os
import requests
from typing import Literal, List, Optional
from datetime import datetime


from blueprints.function_tools import Pipeline as FunctionTools


class Pipeline(FunctionTools):
    class Valves(FunctionTools.Valves):
        # Add your custom parameters here
        API_BASE_URL: str = ""
        API_TOKEN: str = ""
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def get_current_time(
            self,
        ) -> str:
            """
            Get the current time.

            :return: The current time.
            """

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            return f"Current Time = {current_time}"

        def get_current_weather(
            self,
            location: str,
            unit: Literal["metric", "fahrenheit"] = "fahrenheit",
        ) -> str:
            """
            Get the current weather for a location. If the location is not found, return an empty string.

            :param location: The location to get the weather for.
            :param unit: The unit to get the weather in. Default is fahrenheit.
            :return: The current weather for the location.
            """

            # https://openweathermap.org/api

            if self.pipeline.valves.API_BASE_URL == "":
                return "OpenWeatherMap API Key not set, ask the user to set it up."
            else:
                units = "imperial" if unit == "fahrenheit" else "metric"
                params = {
                    "q": location,
                    "appid": self.pipeline.valves.API_BASE_URL,
                    "units": units,
                }

                response = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather", params=params
                )
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = response.json()

                weather_description = data["weather"][0]["description"]
                temperature = data["main"]["temp"]

                return f"{location}: {weather_description.capitalize()}, {temperature}°{unit.capitalize()[0]}"

        def calculator(self, equation: str) -> str:
            """
            Calculate the result of an equation.

            :param equation: The equation to calculate.
            """

            # Avoid using eval in production code
            # https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html
            try:
                result = eval(equation)
                return f"{equation} = {result}"
            except Exception as e:
                print(e)
                return "Invalid equation"
            
        async def get_user_information(self, user_id: int) -> str:
            """
            Execute the API request and get the profile information for a given user ID.
            :param user_id: The ID of the user to fetch.
            :return: A string that returns the correct value
            """
            if self.pipeline.valves.API_BASE_URL == "" or self.pipeline.valves.API_TOKEN:
                return "Base URL API/Token not set, ask the user to set it up."
            
            base_url = f"{self.pipeline.valves.API_BASE_URL}/{user_id}"
            headers = {
                "Authorization": "Basic Z3VvcWlhbmcuemhhbmdAYWRhLmFzaWE6UVFAQFdXLmFkYS40c2k0",
                "Content-Type": "application/json",
            }

            try:
                response = requests.get(base_url, headers=headers)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
                data = response.json()

                if "error" in data:
                    return f"Error fetching profile information: {data['error']}"

                return f"User information: {data}"
            except requests.RequestException as e:
                return f"Error fetching profile information: {str(e)}"

    def __init__(self):
        super().__init__()
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "my_tools_pipeline"
        self.name = "My Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
                "API_BASE_URL": os.getenv("API_BASE_URL", ""),
                "API_TOKEN": os.getenv("API_TOKEN", ""),
            },
        )
        self.tools = self.Tools(self)