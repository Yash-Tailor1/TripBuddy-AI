from Tools.tavily_tool import tavily_search
from Tools.flight_tool import search_flights
from backend import run_travel_agent


# result = tavily_search("best hotels in India")
# print(result)

# res = search_flights("Plan a 7 Nepal trip from bangladesh")
# print(res)

user_input = input("Enter travel request: ")

response = run_travel_agent(
    user_input=user_input,
    thread_id="test_user"
)

print("\n Final Response:\n")
print(response["answer"])