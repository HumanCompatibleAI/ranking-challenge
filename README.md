# Prosocial Ranking Challenge

<p align="center"><!-- markdownlint-disable MD033 -->

![Prosocial Ranking Challenge](/docs/img/prc-logo.png?raw=true)

</p>

The Prosocial Ranking Challenge is designed to inspire, fund, and test the best algorithms to improve well-being, polarization, and factual knowledge for social media users. We will use our browser extension to re-order the feeds of paid U.S. participants on Facebook, Reddit, and X (Twitter) for four months, and measure changes in attitudes and behavior.

[More about the project here](https://humancompatible.ai/news/2024/01/18/the-prosocial-ranking-challenge-60000-in-prizes-for-better-social-media-algorithms/)

How do we identify pro- and anti-social content? That's where you come in! We are soliciting ranking algorithms to test, with $60,000 in prize money to be split between ten finalists (as selected by our panel of experts).

---

## 📅 Submission timeline and requirements

### First-round deadline: April 1, 2024

Submissions will take place in two rounds: prototype and production. See the [contest announcement](https://humancompatible.ai/news/2024/01/18/the-prosocial-ranking-challenge-60000-in-prizes-for-better-social-media-algorithms/).

Each submission will include documentation describing how the algorithm works, what outcome(s) it is expected to change, and why it is significant to test, plus a prototype implementation (running as a live API endpoint that you host).

#### First-round submission requirements

For your initial submission, you will need:

- A description of how the algorithm works, what outcome(s) it is expected to change, and why it is significant to test
- A prototype implementation. We do not need your code at this stage.
- A description of how the prototype was built, the language used, and its dependencies.
- A URL for live endpoint that hosts your algorithm, using the API specified below.

You may submit code written in any programming language or combination of languages, but we will supply example code in Python.

At this stage, it is acceptable for you to use external services, hosted models, etc.

### Finalist submissions: May 15, 2024

This time your ranker will need to be delivered in a Docker container, along with complete source code and build instructions. It will need to meet certain performance and security requirements.

At this point your code must be self-contained. Submissions that rely on external services will be disqualified.

Five winners will be announced June 1, 2024.

#### Finalist submission requirements

If you are selected as a finalist, you will need to provide:

- An example Docker container that runs your code, including a repeatable process for building it from source.
- A list of your external dependencies, including versions.
- Your code, so that we can perform a security audit on it.

We will rebuild your container using the audited code before running it in production. We may request your assistance during this process.

### Experiment: Jun - Oct 2024

We will test the winning rankers with real users across three different platforms for five months.

---

## 📨 Submitting an entry

There's a [submission form](https://forms.gle/tcRvtoFyhGeFyZup7).

---

## 🛠 Building a ranker

### Request/response format

Your ranker should accept a list of social media posts and comments, each with a corresponding ID, in JSON format:

```jsonc
{
    // Abbreviated for clarity, see api reference
    "items": [
        {
            "id": "de83fc78-d648-444e-b20d-853bf05e4f0e",
            "title": "this is the post title, available only on reddit",
            "text": "this is a social media post",
            "type": "post",
            "enagements": {
                "upvote": 34,
                "downvote": 27
            }
        },
        {
            "id": "a4c08177-8db2-4507-acc1-1298220be98d",
            "text": "this is a comment, by the author of the post",
            "type": "comment",
            "enagements": {
                "upvote": 3,
                "downvote": 5
            }
        }
    ]
}
```

Your ranker should return an ordered list of IDs. You can also remove items by removing an ID, or add items by inserting a new ID that you generate. To insert posts, we will also need you to supply the URL for the post.

```jsonc
{
    "ranked_ids": [
        "de83fc78-d648-444e-b20d-853bf05e4f0e",
        "571775f3-2564-4cf5-b01c-f4cb6bab461b"
    ],
    "new_items": [
        {
            "id": "571775f3-2564-4cf5-b01c-f4cb6bab461b",
            "url": "https://reddit.com/r/PRCExample/comments/1f33ead/example_to_insert",
        }
    ]
}
```

Additional details can be found in [`docs/api_reference.md`](/docs/api_reference.md)

---

## 🏭 Available infrastructure

Winning classifiers will be run during the experiment in an environment that can provide the following infrastructure (let us know which you'll need). Note that this applies to second-round submissions only. For first round submissions, you must host the ranker and can use whatever infrastructure you like, but it must be imeplementable on our [background process architecture](https://rankingchallenge.substack.com/p/background-processes-databases-scrapers) to be eligible to win.

### Endpoint

We will host your classifier endpoint. GPU is available if needed.

### Database

We will provide a database of historical post metadata for your users, updated as often as is practical, into which you can also write whatever data you want to store. This will probably be Redis.

### Workers

We will provide for three types of worker (GPU equipped, if needed):

- Background: no internet connectivity, but has read/write access to the database.
- Scraper: has internet connectivity, and write-only access to the database.
- Scorer: one or more processes that take posts in parallel and return a JSON output for each one

See [this post](https://rankingchallenge.substack.com/p/background-processes-databases-scrapers) for an explanation of the architecture. If you want to run any of these processes you must provide them inside the same submitted Docker container that holds your ranker process.

### Latency: 500ms

There is no latency requirement for initial submissions.

Finalists must finish returning their result using a standardized test set on our infrastructure within 500ms, for 95% of requests.

We will test this vigorously. Latency can have an enormous impact on overall outcomes, and to properly control for it all study arms must be delayed to match the performance of the slowest ranker.

If your classifier is too slow, we will let you know as quickly as possible, to give you time to improve your submission before the deadline.

---

## 🔐 Security model

As this experiment handles a considerable amount of Personal Identifiable Information (PII) to which your code will have unfettered access, we must take steps to prevent data exfiltration. These will include, among other things:

- Classifiers and offline workers will be executed in a sandbox and prevented from making outgoing network connections.
- Classifier outputs will be validated.
- Direct identifiers of study participants will be hashed wherever practical.
- You will not personally have access to any user-level data about the participants in your study arm. Only aggregate data will be made available during the study. De-identified data may be made available after the study period, if it can be sufficiently de-identified.
- Our team will audit your code.

If your team needs a greater level of access to user data, that may be possible if you are working within an instution that has its own IRB and can independently review your contributions. Talk to us and we'll see if we can find a way.

---

## Example code

A simple Python example that uses nltk to rank items can be found in [examples/basic](/examples/basic)

In the coming weeks, we will add sample rankers that

We will also provide a containerization example for finalist submissions.

---

## Contacting us

- [Subscribe for Updates!](https://rankingchallenge.substack.com/)
- [Join our Discord!](https://discord.gg/JRmuHSj8XK)

- Technical questions: Ian Baker <raindrift@berkeley.edu>
- All other enquiries: Jonathan Stray <jonathanstray@berkeley.edu>
