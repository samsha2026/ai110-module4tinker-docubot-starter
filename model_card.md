# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> DocuBot helps developers stop digging through folders when they just need a quick answer. It reads your local docs and tries to surface the right information and when it uses an LLM it makes sure the model only talks about what the docs actually say.

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> A question typed by the user, markdown files sitting in the docs folder, and a Gemini API key if you want LLM features enabled.

**What outputs does DocuBot produce?**

> Either the raw text of the most relevant docs, or a clean written answer from Gemini. If nothing useful was found, it says so instead of guessing.

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> Every document gets broken down into individual words and those words get mapped to the file they came from. 
> When a question comes in, the system checks which files contain the most query words and ranks them. 
> The top three get returned.

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

> Simplicity was the priority. The system is easy to follow and debug but it has no real understanding of language. Matching the word "token" in a setup guide scores the same as finding it in the auth documentation which is not always helpful.

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> Naive LLM mode: Gemini gets the question and nothing else so it answers from whatever it already knows.
> Retrieval only mode: No LLM at all, just the raw text of whatever files matched.
> RAG mode: The top matching files go to Gemini first and it can only use those to answer.

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> The prompt tells Gemini to stick strictly to the snippets it was given, not to make up any function names or endpoints, to mention which files it pulled from, and to say it does not know rather than fill in the gaps with guesses.

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|

| Where is the auth token generated? | Harmful | Helpful | Helpful | Naive LLM gave a generic answer, RAG correctly cited AUTH.md |
| How do I connect to the database? | Harmful | Helpful | Helpful | Naive LLM invented steps, RAG pulled the correct setup info |
| Which endpoint lists all users? | Harmful | Helpful | Helpful | Naive LLM guessed a route, RAG pointed to GET /api/users |
| How does a client refresh an access token? | Harmful | Helpful | Helpful | Naive LLM described a generic flow, RAG used the actual docs |


**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

> Naive LLM is most dangerous when it sounds the most polished, using fluent sentences with specific sounding details that were never actually in the docs.
> Retrieval only earns trust because you can see exactly where the answer came from even if you have to find it yourself in a wall of text.
> RAG hits the sweet spot when the answer exists in the docs and you just want it explained clearly without hunting through raw files.

---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> Failure case 1: Asked whether the docs mention payment processing, naive LLM described a Stripe integration in confident detail.
> None of that exists anywhere in the project.
> It should have simply said it had no information on that topic rather than inventing something that sounded believable.

> Failure case 2: When asked where the auth token is generated, retrieval also returned SETUP.md because the word "token" appeared there in a different context.
> The right file came back too but the extra noise made the output harder to read.
> The system should have been smarter about ranking by relevance rather than just word count.

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> When the query does not match any files in the index at all.
> When the files that do come back are clearly talking about something adjacent but never actually answer the question.


**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> If retrieval comes back empty the system skips the LLM entirely and returns a refusal right away.
> The RAG prompt also tells Gemini directly that it is better to admit uncertainty than to fill silence with a guess.

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. The system matches words but not meaning so related terms like "auth" and "authentication" are treated as completely different
2. Whole documents get returned instead of just the relevant paragraph which makes answers harder to read
3. There is no memory between questions so every query starts completely fresh

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. Switch to embedding based search so the system understands meaning not just exact words
2. Break documents into smaller chunks before indexing so retrieved results are more focused
3. Add a score threshold so low confidence matches trigger a refusal instead of a noisy answer

---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> Developers who trust DocuBot without double checking could wire up authentication wrong or use the wrong environment variable names.
> They could also skip setup steps entirely without realizing the docs had more detail.

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- Use RAG mode whenever possible and treat naive LLM answers as a starting point not a final answer
- If the response does not mention a specific file be extra careful about trusting it

---
