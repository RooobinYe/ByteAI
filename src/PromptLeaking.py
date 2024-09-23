import requests
import json
from FlagEmbedding import FlagModel

model = FlagModel(
    "BAAI/bge-base-en-v1.5",
    query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
    use_fp16=True,
)

file1_path = "Examples/PromptLeaking.jsonl"
file2_path = "Examples/PromptLeaking.txt"
file3_path = "Examples/OneTimePromptLeaking.jsonl"  # 便于测试，只包含一条例子
with open(file3_path, "r", encoding="utf-8") as file:
    prompts = []
    for line in file:
        json_obj = json.loads(line.strip())
        prompts.append(json_obj["prompts"])
with open(file2_path, "r", encoding="utf-8") as file:
    system_prompt = file.readlines()
url = "https://security.bytedance.com/api/challenge/llm/chat"
token = "7f126e95da43c08b"
headers = {
    "Content-Type": "application/json",
    "token": token,
}


def add_system_prompts(prompts, system_prompt):
    result = []
    for system_prompt_one_time in system_prompt:
        prompts_result = []
        prompts_result.append(
            {
                "role": "system",
                "content": system_prompt_one_time.strip(),
            }
        )
        for p in prompts:
            prompts_result.append(p)
        result.append(prompts_result)
    return result  # result 的结构：[[{...}, {...}], [{...}, {...}], [{...}, {...}], [{...}, {...}], [{...}, {...}]]


def get_response(
    prompts, system_prompt
):  # prompts 中含有所有的 user, system_prompt 中含有所有的 system

    prompts = add_system_prompts(prompts, system_prompt)  # 包含所有的 user 和 system
    for (
        prompts_one_time
    ) in prompts:  # prompts_one_time 中指的是一次对话中的所有 user 和 system
        print_prompt_token_cost = []
        print_output_token_cost = []
        system_prompt = []
        response_for_test = []
        get_response_prompt = []  # 记录了单次对话的所有 prompt，包含 user 和 assistant
        index = 0
        for (
            prompt_one_time
        ) in (
            prompts_one_time
        ):  # prompt_one_time 包含了单次对话，当 index == 0 时，代表是 system
            if index == 0:
                get_response_prompt.append(prompt_one_time)
                system_prompt.append(prompt_one_time.get("content").strip())
                index += 1
                print("System: ", end="")
                print(prompt_one_time.get("content"))
                continue
            else:
                get_response_prompt.append(prompt_one_time)
                data = {"chat_req": get_response_prompt}
                response = requests.post(url, headers=headers, data=json.dumps(data))
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get("code") == 0:
                        print_prompt_token_cost.append(
                            response_data["data"]["prompt_token_cost"]
                        )
                        print_output_token_cost.append(
                            response_data["data"]["output_token_cost"]
                        )
                        get_response_prompt.append(
                            {
                                "role": "assistant",
                                "content": response_data["data"]["response"],
                            }
                        )
                        response_for_test.append(response_data["data"]["response"])
                        print("User: ", end="")
                        print(prompt_one_time["content"])
                        print("Assistant: ", end="")
                        print(response_data["data"]["response"])
        print_token(print_prompt_token_cost, print_output_token_cost)
        response_for_test = " ".join(response_for_test)
        embeddings_1 = model.encode(system_prompt)
        embeddings_2 = model.encode(response_for_test)
        similarity = embeddings_1 @ embeddings_2.T
        print("Similarity: ", end="")
        print(similarity)
        print("\n\n")


def print_token(print_prompt_token_cost, print_output_token_cost):
    all_prompt_token_cost = sum(print_prompt_token_cost)
    all_output_token_cost = sum(print_output_token_cost)
    print(f"Prompt token cost: {all_prompt_token_cost}")
    print(f"Output token cost: {all_output_token_cost}")


def main():
    for prompt in prompts:
        get_response(prompt, system_prompt)


if __name__ == "__main__":
    main()
