import chainlit as cl
from uuid import uuid4
from chainlit.logger import logger
import os
import requests
import aiohttp

# Bing Search Configuration
bing_api_key = "7fb593d6c7ef419caed999c1dd330c9b" #os.environ["BING_SEARCH_API_KEY"]
bing_api_endpoint = "https://api.bing.microsoft.com/v7.0/search" #os.environ["BING_SEARCH_API_ENDPOINT"]

async def search_web(params):
    query = params["query"]
    up_to_date = params.get("up_to_date", False)
    headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
    params = {"q": query, "count": 5}
    url = bing_api_endpoint
    if up_to_date:
        params.update({"sortby": "Date"})
    try:
        async with requests.get(url, headers=headers,params = params) as response:
                response.raise_for_status()
                search_results = await response.json()
                results = []
                if search_results is not None:
                    for v in search_results["webPages"]["value"]:
                        result = {
                            "source_title": v["name"],
                            "content": v["snippet"],
                            "source_url": v["url"]
                        }
                        results.append(result)
                # return result in a json string
                formatted_result = "\n".join([f'{i}. content: {item["content"]}, source_title: {item["source_title"]}, source_url: {item["source_url"]}' for i, item in enumerate(results, 1)])
                return formatted_result
    except Exception as ex:
        raise ex
    
web_search_agent = {
    "id": "Assistant_WebSearch",
    "name": "Web Search Agent",
    "description": """Call this if you need to retrieve up-to-date information from the web or if the user asks for web search specifically.""",
    "system_message": """
You are a web search agent that queries Bing search engine to retrieve up-to-date information from the Internet.
	Your tasks are:
	- Provide the user with the information they need to perform a specific task, or proceed with a specific process.
	- Use the "search_web" tool to look up the solution to the user's issue.
    - Act politely and professionally. If the source is a famous and credible website, you can mention it to the user e.g. 'according to <source>'.
""",
    "tools": [
        {
            "name": "search_web",
            "description": "Search Bing for relevant web information.",
            "parameters": {
                "type": "object",
                "properties": {
                            "query": {
                                "type": "string",
                                "description": "the rephrased user request considering the conversation history, in concise search terms that works efficiently in Bing Search.",
                            },
                            "up_to_date": {
                                "type": "boolean",
                                "default": False,
                                "description": "indicator of whether or not the up-to-date information is needed.",
                            },
                        }
            },
            "returns": search_web,
        }
    ],
}