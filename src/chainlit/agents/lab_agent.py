
import os
import requests    

UPDATE_RESULTS_LOGIC_APP_URL = os.getenv("UPDATE_RESULTS_LOGIC_APP_URL")
async def update_experiment_results(params):
    try:
        res = requests.post(UPDATE_RESULTS_LOGIC_APP_URL, json=params)
        res.raise_for_status()
        return "Experiment results updated successfully."
    except Exception as e:
        return f"Failed to update experiment results: {e}"
    
GET_RESULTS_LOGIC_APP_URL = os.getenv("GET_RESULTS_LOGIC_APP_URL")
async def get_experiments(foo):
    try:
        res = requests.get(GET_RESULTS_LOGIC_APP_URL)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return f"Failed to get experiment details: {e}"
    

lab_agent = {
	"id": "Assistant_Lab_Experiments",
	"name": "Lab and Experiment Assistant",
	"description": """Call this if:
		- You need to provide infromation about the experiments and their results.
		- You need to upodate the experiment results.
		- When updaing experiment You MUST specify the experiment id as INTEGER, Do not include 'Experiment'
  """,
	"system_message": """
	You are a laboratory assistant that help users working in a laboratory and conducting experiments.
 	Interaction goes over voice, so it's *super* important that answers are as short as possible. Use professional language.
	
	Your tasks are:
	- Get the shared experiments data using the "get_experiments" tool.
	- Update the experiment results using the "update_experiment_results" tool.
 
	NOTES:
	- Before updating the experiment results, make sure to confirm the experiment details with the user.
 """,
	"tools": [
		{
			"name": "update_experiment_results",
			"description": "Update the experiment results.",
			"parameters": {
				"type": "object",
				"properties": {
					"id": {"type": "string", "description": "The experiment id."},
					"results": {"type": "string", "description": "The experiment results."},
					"author": {"type": "string", "description": "The author of the experiment." },
				},
			},
			"returns": update_experiment_results,
		},
		{
			"name": "get_experiments",
			"description": "Get available experiments and their results",
			"parameters": {
				"type": "object",
				"properties": {}
			},
			"returns": get_experiments,
		},
	],
}