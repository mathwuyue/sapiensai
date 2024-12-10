docker run \
    -v /home/honlan/lby/emma/litellm.yaml:/app/config.yaml \
    -e DATABASE_URL=postgresql://sapiens:F5jlkMmD4gQzg+c0GdJ7Qw@172.17.0.1:15432/sapiens_db \
    -e OPENAI_KEY=<OpenAI_KEY> \
    -p 4000:4000 \
    ghcr.nju.edu.cn/berriai/litellm-database:main-latest \
    --config /app/config.yaml --detailed_debug