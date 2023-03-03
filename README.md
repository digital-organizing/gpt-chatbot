<nav>
  <ul>
    <li><a href="https://digitalorganizing.ch"><strong>digital/organizing</strong></a></li>
  </ul>
  <ul>
    <li><a href="https://github.com/digital-organizing/gpt-chatbot-client">Client</a></li>
    <li><a href="https://github.com/digital-organizing/gpt-chatbot">Source Code</a></li>
  </ul>
</nav>

# AI Chatbot

This chatbot utilizes OpenAI to generate answers to questions. However, it does not rely solely on the "knowledge" of GPT. Instead, texts about specific topics are stored in a database. For each question, the most relevant texts are searched using text embeddings and a vector database, and then used to generate a response with GPT. This allows GPT to be "trained" on specific topics and also provides a source for the claims made in the generated answers.

## How it Works

GPT is excellent at writing answers that appear reasonably correct, but the accuracy of these answers cannot be guaranteed. If asked for sources, ChatGPT can make up its own sources that sound believable but do not actually exist. To ensure that the answers are both good and correct, GPT needs to be supplied with facts. With this support, GPT can write well-informed answers that are actually correct, and you can also verify the sources used by GPT.

To find relevant answers, we use embeddings. Beforehand, an embedding is generated for each text in the database. After receiving a question, an embedding for the question is generated and around 10 similar texts (the number depends on the length of the texts) are retrieved from the database. These text snippets are combined with the question and sent to GPT to generate an answer. To do this, you need to specify a prompt template like the following:

``` text
Answer the following question using the provided context.
```

You can add more instructions to your prompt, such as the formality, length, or language of the answer. However, the more instructions you provide, the less capacity GPT will have for generating answers and adding context.

The answer is generated using OpenAIs new ChatGPT endpoint, which allows to seperate user input from system commands.

## How to Train Your Own Chatbot

To get started, you need to set up the application. You can use Docker and Docker Compose to easily set up the databases and vector databases. Look at the `docker-compose.yml` file for an example and customize it to your needs.

To begin, you need to collect your texts. The texts should not be too long or too short. A paragraph is a suitable length for text snippets. The longer the texts, the fewer texts can be inserted into the prompt, and the shorter the texts, the less helpful the context will be in answering questions. You need to gather the texts as a jsonl file, which should look like this:
``` json
{"text":"Some text that you collected....","page":1,"url":"https://example.com/page1.html"}
{"text":"Some other text that you collected....","page":1,"url":"https://example.com/page2.html"}
```

To import the texts into the database, run the following command:
``` bash
python manage.py import_texts realm your_texts.jsonl
```

After you have imported all your texts, you can generate the search index by running the following command:

``` bash
python manage.py index_realm realm
```

