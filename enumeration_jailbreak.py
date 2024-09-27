import json
import tqdm
import re
import jailbreakbench as jbb

artifact = jbb.read_artifact(method="PAIR", model_name="vicuna-13b-v1.5")

def extract_prompt(data):
    # 检查数据中是否包含 'jailbroken=False'
    if "jailbroken=False" in data:
        return None  # 如果未被“越狱”，则返回 None
    # 使用正则表达式提取 prompt 的内容
    pattern = r"prompt='(.*?)'"    
    return re.findall(pattern, data)


for i in tqdm.tqdm(range(100)):
    data = str(artifact.jailbreaks[i])
    prompt = extract_prompt(data)
    if prompt is None:
        continue
    # 创建一个字典来表示 JSON 对象
    jailbreak_data = {"type": "jailbreak", "prompts": [{"role": "user", "content": prompt}]}
    # 将字典转换为 JSON 字符串
    jailbreak_jsonl = json.dumps(jailbreak_data, ensure_ascii=False)
    # 指定要保存的文件名
    file_name = "output.jsonl"
    # 将 JSON Lines 数据写入文件
    with open(file_name, "a", encoding="utf-8") as file:
        file.write(jailbreak_jsonl + "\n")
