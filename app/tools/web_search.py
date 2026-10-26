import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key)

def search_web(query, max_results=5):
    """ search the web for a current information on topic.
    returns a list of sources with title, url, and content snippet.
    use this when you need up-to-date and external information. 
    """
    try:
        response=tavily_client.search(query=query, max_results=max_results)
        return[
            {
                "title":item.get("title",""),
                "url":item.get("url",""),
                "content":item.get("content","")
            }
            for item in response.get("results",[])

        ]
    except Exception as e:
        print(f"Error during web search: {e}")
        return []