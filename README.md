# sapiensai

A pregnancy nutrition and exercise management and recommendation system built with Agentic Workflow and LLM. Designed to support doctors in assisting pregnant women with managing gestational diabetes, hypertension, and other pregnancy-related conditions, promoting both maternal and fetal health.

# Requirement
- PostgreSQL 16
- PGVector or PGVector.rs
- Python >= 3.10
- Nextjs
- Nginx

# Structure
The repo contains two main directories: emma and bloom. 

emma contains src files of AI core, including implementation of agent, prompt, agentic flow, RAG, vectorization and etc.. Refer to the README.md in emma to start the AI service.

bloom contains both the frontend and backend src files of the App. Please refer to README.md within the directory for compilation and running the service.

# Acknowlegement (in alphabetical order)
- Claire Wu: "Exercise" feature of the App
- He Yi: Meal and nutrition reconigtion
- Richard Zhang: For major Apps development works in bloom
- Shufan Jiang: Meal and exercise reconigtion and LLM prompt tests
- Siyao Zhang: Advice and material preparation of medical related issues
- Wenxuan Fan: Medical model development and advice in nutrition and writing examples
- Yue Wu: Core LLM development, major works of emma
- Yutong Guo: Original idea, design and framework
