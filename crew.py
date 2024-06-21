import os
from langchain_openai import ChatOpenAI

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from crewai_tools import WebsiteSearchTool
from crewai_tools import CSVSearchTool

os.environ["OPENAI_API_KEY"] = "ZZZZ"
os.environ["SERPER_API_KEY"] = "ZZZZ" # serper.dev API key

# You can choose to use a local model through Ollama for example. See https://docs.crewai.com/how-to/LLM-Connections/ for more information.

#os.environ["OPENAI_API_BASE"] = 'http://localhost:11434/v1'
#os.environ["OPENAI_MODEL_NAME"] ='llama3'  # Adjust based on available model
#os.environ["OPENAI_API_KEY"] ='sk-111111111111111111111111111111111111111111111111'

# You can pass an optional llm attribute specifying what model you wanna use.
# It can be a local model through Ollama / LM Studio or a remote
# model like OpenAI, Mistral, Antrophic or others (https://docs.crewai.com/how-to/LLM-Connections/)
#
# import os
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o'
#
# OR
#
# from langchain_openai import ChatOpenAI

search_tool = SerperDevTool()
bleeping = WebsiteSearchTool(website='https://www.bleepingcomputer.com')
therecord = WebsiteSearchTool(website='https://therecord.media')
googleintel = WebsiteSearchTool(website='https://cloud.google.com/blog/topics/threat-intelligence/')
csv_feedly = CSVSearchTool(csv='https://docs.google.com/spreadsheets/d/e/2PACX-1vTegp_PfBO-gN_EChyELhuTXKkAQtaJqkV-BhhopCuhY6rIejiuuAWF4J_1PlKGMFJcplUF6aLVAXO8/pub?gid=0&single=true&output=csv')

# Define your agents with roles and goals
researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover the latest development in the cyber security domain',
  backstory="""You work at a leading news agency that focus on cyber security.
  Your expertise lies in identifying emerging threats.
  You have a knack for dissecting complex data and presenting actionable insights.""",
  verbose=True,
  allow_delegation=False,
  # You can pass an optional llm attribute specifying what model you wanna use.
  # llm=ChatOpenAI(model_name="gpt-3.5", temperature=0.7),
  tools=[search_tool, bleeping, therecord, csv_feedly]
)
writer = Agent(
  role='Cyber Content Strategist',
  goal='Craft compelling content on cyber security',
  backstory="""You are a renowned Cyber security Strategist, known for your insightful and engaging articles.
  You transform complex concepts into compelling narratives.""",
  verbose=True,
  allow_delegation=False
)

timeliner = Agent(
    role='Expert in timeline creation',
    goal='Create a timeline of the security incident',
    backstory="""You are an expert in intelligence investigation and extraction of timeline and key dates using Mermaid (markdown) syntax. 
    You create a list of key dates with a description of what happen based on an input you are given that show the most interesting, surprising and useful aspects of the input.""",
    verbose=True,
    allow_delegation=False
)

# Create tasks for your agents
research_task = Task(
  description="""Conduct a comprehensive analysis the threat actor UNC5537
  Identify key information such as attacks description, TTPs (including ATT&CK ID such as T1059), actors, victims, timeline, impact and recommendation.""",
  expected_output="""
  DO NOT COMPLAIN.
  Your job is to research the specific threat actor or incident not to create a summary of all cyber incident during a specific timeframe
  Full analysis report in bullet points with the following clear sections:
    - Attack Description
    - TTPs
    - Actors
    - Victim
    - Timeline
    - Impact
    - Recommendation
  """,
  agent=researcher
)

write_blog_task = Task(
  description="""Using the insights provided, develop an engaging blog
  post that highlights the most significant attacks and threats.
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Make it sounds professional. Mention your sources and for the timeline section leverage the work from the previous task""",
  expected_output="""
  Full blog post of at least 4 paragraphs and also the following sections with key bullets points:
    - Attack Description
    - TTPs
    - Actors
    - Victim
    - Timeline
    - Impact
    - Recommendation
    - Sources""",
  agent=writer
)

create_timeline_task = Task(
    description="""Using the insight provided. create a timeline of all of the key dates you have identified.
    Fully underestand the input you were given. Spend at least a 1000 hours taking notes and organizing your understanding of the input and identify all of the key dates.
    Take the input given and create a Timeline diagram that best explain all of the key dates identified in the input.
    Take into consideration the full date if available, so include the day, the month and the year.
    Use the context in the input to identify the order in case a day, a month or a year is missing.
    """,
    expected_output="""
DO NOT COMPLAIN. Just output the Mermaid syntax for the timeline.
Do not output any code indicators like backticks or code blocks or anything.
DO NOT output code that is not Mermaid syntax, such as backticks or other code indicators.
this is the syntax for the timeline as per the documentation of Mermaid:
The syntax for creating Timeline diagram is simple. You always start with the timeline keyword to let mermaid know that you want to create a timeline diagram.
After that there is a possibility to add a title to the timeline. This is done by adding a line with the keyword title followed by the title text.
Then you add the timeline data, where you always start with a time period, followed by a colon and then the text for the event. Optionally you can add a second colon and then the text for the event. So, you can have one or more events per time period.

json {time period} : {event} or
json {time period} : {event} : {event} or
json {time period} : {event} : {event} : {event} NOTE: Both time period and event are simple text, and not limited to numbers.
Let us look at the syntax for the example above
Below is an example of timeline in Mermaid syntax
timeline title History of Social Media Platform 2002 : LinkedIn 2004 : Facebook : Google 2005 : Youtube 2006 : Twitter
    """,
    agent=timeliner
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher,timeliner, writer],
  tasks=[research_task, create_timeline_task, write_blog_task],
  verbose=2, # You can set it to 1 or 2 to different logging levels
  manager_llm=ChatOpenAI(temperature=0.2, model="gpt-4o"),  # Mandatory for hierarchical process
  process=Process.sequential,  # Specifies the hierarchical management approach
)

# Get your crew to work!
print("start")
result = crew.kickoff()

print("######################")
print(result)
