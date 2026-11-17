# TechWise AI — Assignment 2

**TechWise AI** is a conversational technical assistant for AI, programming, and engineering topics. It uses Gradio for the UI, the OpenAI Responses API for natural-language answers, and three independent services: Open Library book discovery, persistent ChromaDB semantic search, and an engineering calculator with actual OpenAI function calling.

## Setup and run

Place this folder at `05_src/assignment_chat` in the existing UofT `deploying-ai` repository. The course's `05_src/utils/clients.py`, `05_src/.env`, and `05_src/.secrets` must already exist; **they are not included in this submission**. `config.py` loads both configuration files before importing `get_client()`. The course client supports direct OpenAI access or the gateway selected with `USE_GATEWAY`. Gateway operation requires Responses API support, including function calls for Service 3.

Do not install extra packages for grading. The expected course environment already includes `openai`, `gradio`, `python-dotenv`, and `chromadb`. Check with the instructor if any are unavailable.

From the repository root:

```powershell
python 05_src/assignment_chat/app.py
```

The app deliberately omits the Gradio `ChatInterface(type=...)` argument for compatibility with older course versions. The default model is `gpt-4.1-mini` unless `OPENAI_MODEL` is set. Optional `MAX_HISTORY_TURNS=8` and `MAX_HISTORY_CHARS=12000` can be set in the existing `05_src/.env`.

## Architecture and service routing

`app.py` accepts a Gradio message and session history, applies input guardrails, and routes the request. Explicit calculation intent goes to the function-calling calculator, explicit knowledge-base intent goes to ChromaDB, and book-search intent goes to Open Library. Other requests use general OpenAI chat. A final output guardrail checks all responses. Mixed-intent messages follow the precedence calculator → knowledge base → books → general chat.

### Service 1 — Open Library API

`services/book_service.py` queries the public `https://openlibrary.org/search.json` API via Python standard-library HTTP functions. The result is transformed into conversational text by the LLM, using the returned titles, authors, publication years, and URLs as evidence. If the model is unavailable, a deterministic readable summary is shown instead of raw JSON. No API key is required for Open Library. Search results are not verified quality rankings.

**Try:** `Find books about machine learning for beginners`.

### Service 2 — ChromaDB semantic search / RAG

`services/rag_service.py` uses `chromadb.PersistentClient` at `knowledge_base/chroma_db/` and collection `techwise_knowledge_v1`. The source corpus, `knowledge_base/documents.json`, contains 15 concise passages about AI, Python, RAG, and software engineering. Retrieved passages are passed to the LLM, which is instructed to answer from those sources and cite their titles. When the LLM is unavailable, the source passages can be displayed directly.

**Embedding process:** `services/semantic_embedding.py` contains a fixed **15-dimensional deterministic concept encoder**. It maps technical terms and curated synonyms to concept dimensions, boosts source-document concept labels, and L2-normalizes the vectors. Both documents and user questions use the same encoder; cosine distance is used for retrieval. This is a simplified **domain-specific semantic approximation**, **not** a pretrained neural embedding model. It recognizes a limited vocabulary and can miss paraphrases. The source JSON and encoder are included for reproducibility.

**Persistence/submission:** The code initializes the collection from the JSON only if it is empty. **Graders should not be required to generate embeddings.** On your local course computer, run a knowledge-base question once, close the app, and commit the generated `knowledge_base/chroma_db/` folder, including `chroma.sqlite3` and any index subfolders, after checking it is under 40 MB. The ZIP supplied here does not include your existing local database because that file is on your computer, not available in this workspace. The code has a bootstrap fallback, but the submitted Git branch should contain the populated index. ChromaDB's internal SQLite files are part of ChromaDB persistence; the application does not use the SQLite library directly.

**Try:** `According to the knowledge base, what is RAG?`.

### Service 3 — OpenAI function-calling calculator

`services/calculator_service.py` declares five function schemas: `calculate_power`, `calculate_voltage`, `calculate_current`, `calculate_resistance`, and `convert_units`. The LLM chooses a tool and its arguments; Python validates numeric inputs and executes a whitelisted calculation; the result is sent back as `function_call_output` for a natural-language answer. Division by zero, non-finite numbers, and incompatible unit conversions are rejected. Basic DC equations are supported; AC power factor and three-phase analysis are out of scope.

**Try:** `Calculate power at 12V and 2.5A` and `Convert 2500 mA to A`.

## Personality, guardrails and memory

The server-side `prompts.py` defines a patient, professional, technically precise assistant. `guardrails.py` checks inputs and outputs for the assignment's restricted topics (cats/dogs, horoscopes/zodiac, Taylor Swift), and common attempts to reveal or modify the system prompt. User messages cannot edit the server-side instructions. These regex and instruction-based safeguards are **not foolproof**: they may reject benign phrases or miss indirect, obfuscated, or multilingual attacks.

`memory.py` accepts both older Gradio history pairs and message dictionaries. It retains at most eight recent exchanges and 12,000 characters of history, dropping older messages. Blocked history messages are filtered. Memory is only for the current chat session, not saved into ChromaDB. Character count approximates, but does not equal, token usage. There is no long-term memory or summary of dropped turns.

## Tests

Run offline tests from the repository root:

```powershell
python -m unittest discover -s 05_src/assignment_chat/tests -v
```

Phase 6 includes mocked routing tests for all three services and general chat, so tests do not require paid API calls. Run local submission checks after copying your persistent database:

```powershell
python 05_src/assignment_chat/verify_submission.py
```

**Live manual tests required:** Verify a real Open Library response, RAG retrieval after restart, actual OpenAI function calling, follow-up memory, prompt protection, and restricted-topic refusals. Automated mocks do not establish gateway compatibility or live service availability.

## Repository and submission

Keep the project under `05_src/assignment_chat`. Create the branch `assignment-2`, commit the project and populated ChromaDB index (but never credentials), push the branch, and open a pull request to the repository's expected base branch. Ensure the repository is public and verify the PR in a private browser window. See `SUBMISSION_CHECKLIST.md` and the course's [Assignment Submission Guide](https://github.com/UofT-DSI/onboarding/blob/main/onboarding_documents/submissions.md).

## Known limitations

Small curated knowledge corpus, deterministic concept embeddings, intent-based routing, session-only memory, regex guardrails, and dependence on course gateway support for Responses API function calling. This project is a course demonstration, not a production-grade assistant.
