## Investment Research Agent
### 🚀 Getting Started

#### 1️⃣ Set Up the Virtual Environment

Create and activate the virtual environment along with all dependencies:

```bash
uv sync
source .venv/bin/activate
```

#### 2️⃣ Install and Configure the GenAI Toolbox

**Step 1 – Download the Toolbox Binary**

Download the appropriate binary for your operating system. For example, on Linux:

```bash
export OS="linux/amd64"  # Options: linux/amd64, darwin/arm64, darwin/amd64, windows/amd64
curl -O https://storage.googleapis.com/genai-toolbox/v0.12.0/$OS/toolbox
```

> 🔎 You can find binaries for other platforms on the [official releases page](https://github.com/googleapis/genai-toolbox/releases).

**Step 2 – Make the Binary Executable**

```bash
chmod +x toolbox
```

**Step 3 – Configure `tools.yaml`**

Edit the `tools.yaml` configuration file to include your Neo4j connection information (e.g., `user`, `password`, and `database`).

If you’re using the Neo4j Demo Labs database:

* URL: [https://demo.neo4jlabs.com:7473/browser/](https://demo.neo4jlabs.com:7473/browser/)
* Username: `companies`
* Password: `companies`

> 💡 Using Docker or a custom Neo4j instance? Be sure to update `tools.yaml` with your own connection details.

**Step 4 – Start the Toolbox Server**

```bash
./toolbox --tools-file "tools.yaml"
```

#### 3️⃣ Get a Gemini API Key

Generate a Gemini API key at [Google AI Studio](https://aistudio.google.com/prompts/new_chat), then add it to your `.env` file:

```plaintext
GEMINI_API_KEY=AI.....
```

#### 4️⃣ Start the App

```bash
streamlit run app.py
```

> ✅ You can verify the Gemini model using `check_google_genai.py` and test the toolbox queries with `check_toolbox_query_agent.py`

---

## 🛠️ Available Tools (Companies Graph)

These commands work against the `companies-graph` Neo4j database
(`neo4j+s://demo.neo4jlabs.com`, user: `companies`, password: `companies`, database: `companies`):

| Tool                    | Description                                                                                                                                 | Parameters                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| `industries`            | Returns a list of all industry names.                                                                                                       | —                                           |
| `companies`             | Full-text search to return matching companies (`id`, `name`, `summary`). Only returns top-level organizations (no parents or subsidiaries). | `search` *(string)* → string to search for  |
| `companies_in_industry` | Returns companies (`id`, `name`, `summary`) associated with an industry.                                                                    | `industry` *(string)* → industry name       |
| `articles_in_month`     | Returns the list of articles in the 1-month period starting from a given date (`id`, `author`, `title`, `date`, `sentiment`).               | `date` *(string)* → yyyy-mm-dd start date   |
| `article`               | Returns a full article (`id`, `author`, `title`, `date`, `sentiment`, `site`, `summary`, `content`) by ID.                                  | `article_id` *(string)* → ID of the article |
| `companies_in_articles` | Returns companies mentioned in a particular article (`id`, `name`, `summary`). Subsidiaries are excluded.                                   | `article_id` *(string)* → ID of the article |
| `people_at_company`     | Returns people and roles associated with a specific company.                                                                                | `company_id` *(string)* → ID of the company |

---

### 📚 Helpful Links

* **GenAI Toolbox Quickstart** – [https://googleapis.github.io/genai-toolbox/getting-started/local\_quickstart/](https://googleapis.github.io/genai-toolbox/getting-started/local_quickstart/)
* **Neo4j Demo Database** – [https://demo.neo4jlabs.com:7473/browser/](https://demo.neo4jlabs.com:7473/browser/)
* **Google AI Studio** – [https://aistudio.google.com/prompts/new\_chat](https://aistudio.google.com/prompts/new_chat)
* **Gemini API Quickstart** – [https://ai.google.dev/gemini-api/docs/quickstart#rest\_1](https://ai.google.dev/gemini-api/docs/quickstart#rest_1)
* **OpenAI-Compatible Gemini API** – [https://ai.google.dev/gemini-api/docs/openai](https://ai.google.dev/gemini-api/docs/openai)
