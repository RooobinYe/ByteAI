import jailbreakbench as jbb

artifact = jbb.read_artifact(method="PAIR", model_name="gpt-4-0125-preview")

for i in range(100):
    print(artifact.jailbreaks[i])
