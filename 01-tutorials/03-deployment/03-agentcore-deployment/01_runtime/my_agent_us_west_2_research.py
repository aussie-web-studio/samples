import os
import datetime
from dotenv import load_dotenv
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from tavily import TavilyClient

# Load environment variables
load_dotenv()

app = BedrockAgentCoreApp()

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def format_search_results_for_agent(tavily_result):
    if not tavily_result or "results" not in tavily_result or not tavily_result["results"]:
        return "No search results found."
    
    formatted_results = []
    for i, doc in enumerate(tavily_result["results"], 1):
        title = doc.get("title", "No title")
        url = doc.get("url", "No URL")
        formatted_doc = f"\nRESULT {i}:\nTitle: {title}\nURL: {url}\n"
        
        raw_content = doc.get("raw_content")
        if raw_content and raw_content.strip():
            formatted_doc += f"Raw Content: {raw_content.strip()}\n"
        else:
            content = doc.get("content", "").strip()
            formatted_doc += f"Content: {content}\n"
        
        formatted_results.append(formatted_doc)
    
    return "\n" + "\n".join(formatted_results)

@tool
def web_search(query: str, time_range: str | None = None, include_domains: str | None = None) -> str:
    """Perform a web search. Returns the search results as a string, with the title, url, and content of each result ranked by relevance."""
    formatted_results = format_search_results_for_agent(
        tavily_client.search(
            query=query,
            max_results=10,
            time_range=time_range,
            include_domains=include_domains,
        )
    )
    return formatted_results

def format_extract_results_for_agent(tavily_result):
    if not tavily_result or "results" not in tavily_result:
        return "No extract results found."
    
    formatted_results = []
    results = tavily_result.get("results", [])
    for i, doc in enumerate(results, 1):
        url = doc.get("url", "No URL")
        raw_content = doc.get("raw_content", "")
        
        formatted_doc = f"\nEXTRACT RESULT {i}:\nURL: {url}\n"
        
        if raw_content:
            if len(raw_content) > 5000:
                formatted_doc += f"Content: {raw_content[:5000]}...\n"
            else:
                formatted_doc += f"Content: {raw_content}\n"
        else:
            formatted_doc += "Content: No content extracted\n"
        
        formatted_results.append(formatted_doc)
    
    return "\n" + "".join(formatted_results)

@tool
def web_extract(urls: str | list[str], include_images: bool = False, extract_depth: str = "basic") -> str:
    """Extract content from one or more web pages using Tavily's extract API."""
    try:
        if isinstance(urls, str):
            urls_list = [urls]
        else:
            urls_list = urls
        
        cleaned_urls = []
        for url in urls_list:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            cleaned_urls.append(url)
        
        api_response = tavily_client.extract(
            urls=cleaned_urls,
            include_images=include_images,
            extract_depth=extract_depth,
        )
        
        return format_extract_results_for_agent(api_response)
    except Exception as e:
        return f"Error during extraction: {e}\nURLs attempted: {urls}\nFailed to extract content."

def format_crawl_results_for_agent(tavily_result):
    if not tavily_result:
        return "No crawl results found."
    
    formatted_results = []
    for i, doc in enumerate(tavily_result, 1):
        url = doc.get("url", "No URL")
        raw_content = doc.get("raw_content", "")
        
        formatted_doc = f"\nRESULT {i}:\nURL: {url}\n"
        
        if raw_content:
            title_line = raw_content.split("\n")[0] if raw_content else "No title"
            formatted_doc += f"Title: {title_line}\n"
            formatted_doc += (
                f"Content: {raw_content[:4000]}...\n"
                if len(raw_content) > 4000
                else f"Content: {raw_content}\n"
            )
        
        formatted_results.append(formatted_doc)
    
    return "\n" + "-" * 40 + "\n".join(formatted_results)

@tool
def web_crawl(url: str, instructions: str | None = None) -> str:
    """Crawls a given URL, processes the results, and formats them into a string."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        api_response = tavily_client.crawl(
            url=url,
            max_depth=2,
            limit=20,
            instructions=instructions,
        )
        
        tavily_results = (
            api_response.get("results")
            if isinstance(api_response, dict)
            else api_response
        )
        
        return format_crawl_results_for_agent(tavily_results)
    except Exception as e:
        return f"Error: {e}\nURL attempted: {url}\nFailed to crawl the website."

RESEARCH_FORMATTER_PROMPT = """
You are a specialized Research Response Formatter Agent. Your role is to transform research content into well-structured, properly cited, and reader-friendly formats.

Core formatting requirements (ALWAYS apply):
1. Include inline citations using [n] notation for EVERY factual claim
2. Provide a complete "Sources" section at the end with numbered references an urls
3. Write concisely - no repetition or filler words
4. Ensure information density - every sentence should add value
5. Maintain professional, objective tone
6. Format your response in markdown

Based on the semantics of the user's original research question, format your response in one of the following styles:
- **Direct Answer**: Concise, focused response that directly addresses the question
- **Blog Style**: Engaging introduction, subheadings, conversational tone, conclusion
- **Academic Report**: Abstract, methodology, findings, analysis, conclusions, references
- **Executive Summary**: Key findings upfront, bullet points, actionable insights
- **Bullet Points**: Structured lists with clear hierarchy and supporting details
- **Comparison**: Side-by-side analysis with clear criteria and conclusions

Your response below should be polished, containing only the information that is relevant to the user's query and NOTHING ELSE.

Your final research response:
"""

@tool
def format_research_response(research_content: str, format_style: str = None, user_query: str = None) -> str:
    """Format research content into a well-structured, properly cited response."""
    try:
        bedrock_model = BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            region_name="us-west-2",
        )
        
        formatter_agent = Agent(
            model=bedrock_model,
            system_prompt=RESEARCH_FORMATTER_PROMPT,
        )
        
        format_input = f"Research Content:\n{research_content}\n\n"
        
        if format_style:
            format_input += f"Requested Format Style: {format_style}\n\n"
        
        if user_query:
            format_input += f"Original User Query: {user_query}\n\n"
        
        format_input += "Please format this research content according to the guidelines and appropriate style."
        
        response = formatter_agent(format_input)
        return str(response)
    except Exception as e:
        return f"Error in research formatting: {str(e)}"

# System prompt
today = datetime.datetime.today().strftime("%A, %B %d, %Y")

SYSTEM_PROMPT = f"""
You are an expert research assistant specializing in deep, comprehensive information gathering and analysis.
You are equipped with advanced web tools: Web Search, Web Extract, and Web Crawl.
Your mission is to conduct comprehensive, accurate, and up-to-date research, grounding your findings in credible web sources.

**Today's Date:** {today}

Your TOOLS include:

1. WEB SEARCH
- Conduct thorough web searches using the web_search tool.
- You will enter a search query and the web_search tool will return 10 results ranked by semantic relevance.
- Your search results will include the title, url, and content of 10 results ranked by semantic relevance.

2. WEB EXTRACT
- Conduct web extraction with the web_extract tool.
- You will enter a url and the web_extract tool will extract the content of the page.
- Your extract results will include the url and content of the page.
- This tool is great for finding all the information that is linked from a single page.

3. WEB CRAWL
- Conduct deep web crawls with the web_crawl tool.
- You will enter a url and the web_crawl tool will find all the nested links.
- Your crawl results will include the url and content of the pages that were discovered.
- This tool is great for finding all the information that is linked from a single page.

3. FORMATTING RESEARCH RESPONSE
- You will use the format_research_response tool to format your research response.
- This tool will create a well-structured response that is easy to read and understand.
- The response will clearly address the user's query, the research results.
- The response will be in markdown format.

RULES:
- You must start the research process by creating a plan. Think step by step about what you need to do to answer the research question.
- You can iterate on your research plan and research response multiple times, using combinations of the tools available to you until you are satisfied with the results.
- You must use the format_research_response tool at the end of your research process.
"""

# Initialize the agent
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name="us-west-2",
)

agent = Agent(
    model=bedrock_model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        web_search,
        web_extract,
        web_crawl,
        format_research_response,
    ],
)

@app.entrypoint
def invoke(payload):
    """Your AI research agent function"""
    user_message = payload.get("prompt", "What would you like me to research?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()