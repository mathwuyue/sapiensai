## For Frontend and Backend application

### Getting Started

Setup venv:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
cd bloom
pip install -r requirements.txt
pnpm install
```

Setup database:

```bash
alembic upgrade head
```

Run the development server:

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.