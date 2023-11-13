import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper


load_dotenv()


llm = OpenAI(temperature=0)
zapier = ZapierNLAWrapper()
toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
agent = initialize_agent(
    toolkit.get_tools(), llm, agent="zero-shot-react-description", verbose=True
)
agent.run(
    "Send an Email to cycaccionlegalsas@gmail.com via gmail that is a pitch for why you should visit https://starmorph.com to help your small business integrate GPT-3 services today. Provide a hyperlink to the website and make the email likely to convert to website visitors."
)
