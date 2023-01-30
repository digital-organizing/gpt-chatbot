# AI Chatbot

This Chatbot uses OpenAi to generate answers to questions. But it does not relay on the "knowledge" of GPT alone. Instead texts about certain topics can be stored in the database. For each question the most relevant texts are searched, using text embeddings and a vector database, and then used to write a response with GPT. This makes it possible to "train" GPT on specific topics and also have the source of the claims made in the generated answers.

## How it works

GPT is great for writing answers, that seem reasonably correct, but you can't be sure whether or not the answers are factualy correct. If prompted for sources, ChatGPT can make up it's own sources, that sound realistic, but don't actually exist. To get good answers that are also correct, GPT needs to be provided with the facts. With this help GPT can write nice answers that are actually correct. And you also have the sources that GPT used to write the answers to double check.

To find relevant answers we use Embeddings. In advance we generate an embedding for each text in the database. After receiving a question an embedding for it is generated and about 10 similar texts (depends on the length of the texts) are fetched from the database. These text snippets are combined with the question and sent to GPT to generate an answer. For this you need to specify a prompt template, that looks like this:
```
Answer the following question using the context provided below:

Question: {question}

Context: 
{context}

Answer:
```

You can provide more instructions in your prompt, like formality, length or language of the answer. But the longer your instructions, the less capacity for generating answers and adding context.

## How to train your own chatbot

First you need to get the application up and running, you can use docker and docker-compose to easily setup the databases and vector databases. Look at `docker-compose.yml` for an example. Customize to your needs.

To get started you need to collect your texts. Texts shouldn't be too long, but also not too short. A paragraph is a good length for text snippets. The longer the texts, the less texts can be inserted into the prompt. The shorter the text, the context might be less helpful to answer questions. You need to gather the texts as `jsonl` file, it should look like this:

```
{"text":"Some text that you collected....","page":1,"url":"https://example.com/page1.html"}
{"text":"Some other text that you collected....","page":1,"url":"https://example.com/page2.html"}
```

Import the text into the database:
```
python manage.py import_texts realm your_texts.jsonl
```

After you imported all your texts, you can generate the search index:

```
python manage.py index_realm realm
```
