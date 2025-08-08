from ollama import generate

class Response:
    def __init__(self, modelname, title, prompt, response):
        self.modelname = modelname
        self.prompt = prompt
        self.title = title
        self.response = response

def generate_using_model(modelname, title, prompt):
    text = generate(model=modelname, prompt=prompt)
    return Response(modelname, title, prompt, text.response)

responses = []
modelName = "llama3.1"
prompt = "What is Performance Testing?"
responses.append(generate_using_model(modelName, "Performance Testing", prompt))

prompt = "What is Exploratory Testing?"
responses.append(generate_using_model(modelName, "Exploratory Testing", prompt))

for response in responses:
    print(f"# {modelName}\n\n## {response.title}\n\n{response.response}\n\n")


