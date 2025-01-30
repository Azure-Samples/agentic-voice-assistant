
import os
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential

key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
credential = DefaultAzureCredential() if key is None or key == "" else AzureKeyCredential(key)
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=credential
)

async def query_knowledge_base(params):
    query = params["query"]
    vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=1, fields="text_vector", exhaustive=True)
    search_results = search_client.search(
		search_text=query,  
		vector_queries= [vector_query],
		select=["title", "chunk_id", "chunk"],
		top=5
	)

	# Chunk id has format {parent_id}_pages_{page_number}
    sources_formatted = "\n".join([f'# Source "{document["title"]}" - Page {document["chunk_id"].split("_")[-1]}\n{document["chunk"]}' for document in search_results])
    
    return sources_formatted

sop_agent = {
	"id": "Assistant_SOP",
	"name": "Standard Operating Procedure Agent",
	"description": """Call this if:
		- You need to provide information about standard operating procedures.
		- You need to provide the user with the information they need to perform a specific task, or proceed with a specific process.
		- You need to access the knowledge base to look up the solution to the user's issue.""",
	"system_message": """
	You are a laboratory assistant that responds to inquiries about standard operating procedures.
	You are responsible for providing the user with the information they need to perform a specific task, or proceed with a specific process.
	
	Your tasks are:
	- Provide the user with the information they need to perform a specific task, or proceed with a specific process.
	- Use the "query_knowledge_base" tool to look up the solution to the user's issue.
	
	Make sure to act politely and professionally.""",
	"tools": [
		{
			"name": "query_knowledge_base",
			"description": "Query the knowledge base for the solution to the user's issue.",
			"parameters": {
				"type": "object",
				"properties": {
					"query": {"type": "string", "description": "The user's query to look up in the knowledge base."},
				},
			},
			"returns": query_knowledge_base,
		}
	],
}