from functools import wraps
from jinja2 import Template
import inspect


def prompt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        signature = inspect.signature(func)
        context = dict(zip(signature.parameters.keys(), args))
        context.update(kwargs)
        template_str = func.__doc__
        template = Template(template_str)
        return template.render(context)
    return wrapper


def basic_rag_prompt():
    template = '''
        Context information is below.
        ---------------------
        {{ context_str }}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: {{ question }}
        Answer:
    '''
    return Template(template)


def rag_with_examplar_prompt():
    template = '''
        Your task is to answer the given question based on the provided context using concise Chinese and follows the style of given examples.
        Here are some examples of the answer you should follow. The examples are in the format of "Question: Answer".
        ---------------------------------------------
        {% for example in examples %}
        {{ example[0] }}: {{ example[1] }}
        {% endfor %}
        ---------------------------------------------
        Context information is below.
        ---------------------
        {{ retrieved_chunk }}
        ---------------------
        Given the context information and not prior knowledge, take a deep breath, answer the query following the steps:
        1. Review the context information carefully. Check if the context information contains the answer to the question. Only use the relevant information ```<relevant_context>``` from the context to answer the question.
        2. For the ```<relevant_context>```, extract key information from it. Be careful, only extract the most relevant information to the question from ```<relevant_context>``` to ```<relevant_info>```.
        3. Summarize the ```<relevant_info>``` and produce the final answer. Be concise and follow the style of the examples.
        Think step by step and answer the question. Do not print the thinking process in the answer. Only print the final answer.
        Query: {{ question }}
        Answer:
    '''
    return Template(template)


def rag_with_memory_prompt():
    template = '''
    The original query is as follows: {{ quetion }}
    We have provided an existing answer: {{ memory }}
    We have some more context below. The context is split into items with a number and '\n'.
    ------------
    {{ retrieved_chunk }}
    ------------
    Take a deep breath, you should generate a refined answer by following steps:
    1. Review each item carefully. Check if an item contains any information that may relate to the original query.
    2. If there are items relevant to the query, choose the top 5 relevant items and check if they can help refine the original answer. 
    3. If not, you should use the original answer as the final answer.
    4. Your answer should be concise (not more than 100 words) and should follow the style of the examples.
    Here are some examples. The examples are in the format of "Question: Answer".
    ------------
    {% for example in examples %}
    {{ example[0] }}: {{ example[1] }}
    {% endfor %}
    ------------
    Refined Answer: <Refined answer>
    Check the <Refined answer>, you should delete all the other information in <refined answer> that not related to the answer, and generate the <final answer>
    Examples:
    根据部门负责人的安排进行工作汇报即可。无需更改原有答案，因为提供的上下文信息与原问题无关。 -> 根据部门负责人的安排进行工作汇报即可。
    Only output the <final answer>. Do not print any other information.
    '''
    return Template(template)


def rag_with_memory_prompt_cn():
    template = '''
    原始问题如下: {{ quetion }}
    我们提供了一个现有答案: {{ memory }}
    我们在下面提供了更多的上下文。这些上下文标记了1,2....等，并用\n进行了分割
    ------------
    {{ retrieved_chunk }}
    ------------
    您应该按照以下步骤生成一个精炼的答案:
    1. 判断每一条context信息是否与原始问题相关。
    2. 选择最相关的5条context信息，看看它是否可以帮助完善原始答案。如果没有，您应该使用原始答案作为最终答案。
    3. 你的回答必须简洁（不超过100个字）并且应该遵循示例的风格。
    这里有一些例子
    ------------
    {% for example in examples %}
    {{ example }}
    {% endfor %}
    ------------
    只需输出精炼的答案。不要打印任何其他信息。
    '''
    return Template(template)


def memory_prompt():
    template = '''
        You are a memory assistant. You will receive a user query and check your memory to answer the query.
        Here are the information in your memory.
        -----
        {% for example in memory %}
        {{ loop.index }}. {{ example }}
        {% endfor %}
        -----
        Given the information in your memory and not prior knowledge, answer the query following the steps:
        1. Review the information in your memory carefully. Pick up the top relevant query from the memory to answer the query.
        2. If the information in your memory does not contain the answer to the question, answer "Fuiyo, I don't know the answer to this question."
        3. Answer the index of the top relevant query in your memory. Don't answer the question directly. Don't print any other information.
        Query: {{ query }}
        Answer:
    '''
    return Template(template)


def keyword_promt():
    template = '''
        Your task is to extract keywords from the given question. Assume you are searching for the answer to the question in documents.
        Please think 5 keywords that you would use to search for the answer to the question. Your answer should be a list of 5 keywords separated by commas. 
        Query: {{ query }}
        Answer:
    '''
    return Template(template)


def rerank_prompt():
    template = '''
        Your task is to rerank the given documents based on the given query. You will receive a query and a list of documents. The documents are split with '\n'.
        You need to check the relevance of the documents to the query. If no document is relevant to the query, you should answer ```{"documents": []}```
        If there are some of documents which are relevant to the query. You need to rerank the documents based on the relevance to the query. 
        Please choose the top {{ topk }} most relevant documents and provide the reranked list of the chosen {{ topk }} documents. The list should be in the format of "Document ID".
        Query: {{ query }}
        Documents: {{ documents }}
        Extrac the answer. Do not give any explaination or other information.
    '''
    return Template(template)


@prompt
def router_prompt(choices, question, history):
    '''
        Given the user question and history below, classify it as either being about 
        {% for choice in choices %}
        `{{ choice }}`, 
        {% endfor %}.
        Do not respond with more than one word.
        <question> {{ question }} </question> 
        <history>
            {% for message in history %}
            {{ loop.index }}. {{ message["content"] }}
            {% endfor %}
        </history>
        Classification:
    '''


@prompt
def qa_prompt(query, context):
    '''
    Use the following context as your learned knowledge, inside <context></context> XML tags, divided into pieces with index 1. 2. ... by '\n'.\n\n
    <context>\n
    {{ context }}
    </context>\n\n
    When answer to user:\n 
    - Choose pieces of information that are related to the query. \n 
    - If there exists markdown notation like ```[!image](<url>)``` in your chosen pieces, put them to the end of your answer.\n
    - If you don't know, just say that you don't know.\n
    - If you don't know when you are not sure, ask for clarification.\n
    Avoid mentioning that you obtained the information from the context.\n
    And answer according to the language of the user's question.\n\n
    
    Question: {{ query }}
    '''


if __name__ == '__main__':
    from openai import OpenAI
    from dotenv import load_dotenv
    import os

    load_dotenv()
    client = OpenAI(api_key=os.getenv("DASHSCOPE_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = "qwen2-72b-instruct"
    
    def llm(query: str, stream=False, history=None, json_model=None) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": query}],
            stream=stream,
            temperature=0.1
        )
        if stream:
            return response
        return response.choices[0].message.content
    
    query = keyword_promt().render(query="转正流程是怎样的？")
    
    resp = llm(query=query)
    for r in resp.split(','):
        print(r)