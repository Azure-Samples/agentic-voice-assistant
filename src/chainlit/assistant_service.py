import json
import re
import logging

import util
util.load_dotenv_from_azd()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AssistantService:
    def __init__(self, language: str = "English"):
        self.language = language
        self.agents = {}
  
    def get_tools_for_assistant(self, id):
        # Get tools for agent
        # This includes the agent's own tools and other agents as tools
        agent_real_tools = self.agents[id]['tools']
        other_agents_as_tools = [
            {
                'name': ag['id'],
                'description': ag['description'],
                'parameters': {
                    'type': 'object',
                    'properties': {}
                },
                'returns': lambda foo: ag['id']
            }
            for k, ag in self.agents.items() if k != id
        ]

        tools_definitions = [
            {
                'type': 'function',
                'name': tool['name'],
                'parameters': tool['parameters'],
                'description': tool['description']
            }
            for tool in agent_real_tools + other_agents_as_tools
        ]
        return tools_definitions

    def register_agent(self, agent):
        agent['system_message'] = self.format_string(agent['system_message'], {'language': self.language})
        self.agents[agent['id']] = agent

    def get_agent(self, id):
        return self.agents.get(id)

    def register_root_agent(self, root_agent):

        # Ensure every other agent has a tool to switch back to the root agent
        for k, ag in self.agents.items():
            ag['tools'].append({
                'name': root_agent['id'],
                'description': f"If customer asks any question that is outside of your work scope, DO use this to switch back to {root_agent['id']}.",
                'parameters': {
                    'type': 'object',
                    'properties': {}
                },
                'returns': lambda arg: root_agent['id']
            })

        # Register root agent, also with "root" key
        root_agent['system_message'] = self.format_string(root_agent['system_message'], {'language': self.language})
        self.agents["root"] = self.agents[root_agent['id']] = root_agent

    async def get_tool_response(self, tool_name, parameters, call_id):
        print(f"getToolResponse: tool_name={tool_name}, parameters={parameters}, call_id={call_id}")
        
        # Invoked tool is either a real tool or an agent
        all_tools = [tool for ag in self.agents.values() for tool in ag['tools']]
        all_agents_as_tools = [
            {
                'name': ag['id'],
                'description': ag['description'],
                'parameters': {'type': 'object', 'properties': {}},
                'returns': lambda foo: ag['id']
            }
            for ag in self.agents.values()
        ]
        tools = all_tools + all_agents_as_tools
        
        # Get tool by name
        tool = next((t for t in tools if t['name'] == tool_name), None)
        
        # Execute tool
        # If tool_name matches "assistant", it means we are switching to another agent
        if re.search(r'assistant', tool_name, re.IGNORECASE):
            agent = self.agents[tool_name]
            logger.debug(f"Switching to agent {agent['id']}")
            config_message = {
                'type': 'session.update',
                'session': {
                    'turn_detection': {
                        'type': 'server_vad'
                    },
                    'instructions': self.format_string(agent['system_message'], {'language': self.language}),
                    # NOTE we dont' simply use agent['tools'] here because we want to include other agents as tools
                    'tools': self.get_tools_for_assistant(tool_name)
                }
            }
            return config_message
        else:            
            content = await tool['returns'](parameters)
            logger.debug(f"Tool {tool_name} returned content: {content}")
            response = {
                'type': 'conversation.item.create',
                'item': {
                    'type': 'function_call_output',
                    'call_id': call_id,
                    'output': content
                }
            }
            return response

    def format_string(self, string, params):
        # TODO additional logic may be added here, 
        # like providing common instructions for all agents to follow voice-specific guidelines
        return string.format(**params)
