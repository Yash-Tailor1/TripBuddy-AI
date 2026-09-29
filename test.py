from Tools.tavily_tool import tavily_search
from Tools.flight_tool import search_flights


# result = tavily_search("best hotels in India")
# print(result)

res = search_flights("Plan a 7 Nepal trip from bangladesh")
print(res)