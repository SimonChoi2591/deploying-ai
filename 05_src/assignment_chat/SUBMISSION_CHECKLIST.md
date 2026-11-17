# TechWise AI — Assignment 2 Submission Checklist

- [ ] `assignment-2` branch created from the course repository's expected base branch.
- [ ] All project files under `05_src/assignment_chat/`.
- [ ] Three services work in Gradio: books, semantic search, function calling.
- [ ] Restricted topics and prompt-disclosure requests refused.
- [ ] Recent conversation history retained; old history bounded.
- [ ] Persistent `knowledge_base/chroma_db/` copied from the local working environment and committed, **not just** `documents.json`.
- [ ] `python 05_src/assignment_chat/verify_submission.py` passes locally.
- [ ] `python -m unittest discover -s 05_src/assignment_chat/tests -v` passes.
- [ ] Live tests performed for Open Library, RAG, calculator, and direct/gateway OpenAI.
- [ ] No `.env`, `.secrets`, API keys, credentials, or personal data committed.
- [ ] Project files and database under 40 MB.
- [ ] `README.md` explains services, embeddings, limitations, and run steps.
- [ ] Repository public; pull request created from `assignment-2`.
- [ ] Pull request description follows UofT submission guide.
- [ ] PR URL opens successfully in a private browser window.
