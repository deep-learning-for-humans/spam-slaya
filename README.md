# Spam Slaya

## Problem

In today's digital world, your email address is a key part of your identity. Yet, giving it out can feel like opening the floodgates to spam and unwanted clutter. Before you know it, your inbox is overflowing, leaving you overwhelmed and missing important messages. 

**Clean that up** rose out of this personal itch that our Gmail inboxes are bloated and the search for how to clean them up.

## Solution

Our solution is to have something that helps automate email cleaning service while prioritizing your privacy. Here is how it works:

1. **Smart Automation**: It runs quietly in the background, analyzing your emails with advanced language models. It intelligently determines which emails are worth keeping and which can be safely deleted.
2. **Privacy First**: We know how vital your personal information is. That’s why our solution is a local application that runs on your own device. No data is sent to the cloud, ensuring your inbox remains just that—yours!
3. **User-Friendly**: While we recommend some technical know-how for setup, once it’s running, anyone can enjoy a clutter-free inbox without any hassle.

To get started with this, we will need to generate credentials that will allow us to connect to a Google account because we use the Gmail API to fetch your emails. 

### Caveat with Google Credentials

Because of Google’s restrictions on who can get access to email inboxes (very rightfully so), we decided that we will never be a “verified” application. Verification by Google is a long drawn process that involves multiple hoops to jump through (and keep jumping through year after year). 

We have thoroughly detailed the steps that need to be followed in the link below that will allow you to generate your Google Credentials. For each credential you generate, up to 100 people can be added to it. We recommend that you use this only for very close friends and family.

### Generating Google Credentials

TODO

### The LLM

At this point, based on our testing, we have identified that the `qwen2.5:3b-instruct-q4_0` works with a high degree of confidence. In addition, to avoid *sending* your data to anyone, we have chosen to run this via a locally running Ollama server. By our calculations, this should take, on average, a time of 40s - 60s per inference.

We do understand that taxing our users to download a ~ 2GB model file is a lot to ask, but it is a small price to pay considering that our data is not being sent to a 3rd party service. 

# Note

We highly recommend that you read through the code, to make sure that you understand what we are doing with your data. We don’t send this information back to ourselves (there is no hosted instance anywhere). We wrote this, to solve OUR problem, and we hope that it helps solve yours too.

# TODO

- [X] Remove all existing POC code (bootstrap, etc) and keep only bare minimum OAuth flow
- [X] Plan out data & process
- [X] Introduce dependencies - SQLite, SQLAlchemy, Celery 
- [X] Get user ID from Gmail via oauth and store in DB
- [X] Store Open API Key in SQLite 
- [X] Create background job to get emails
- [X] Write status page
- [X] Wire in LLM logic (Rags)
- [X] Docker compose
- [X] Handle workers gracefully
- [ ] Normalize the environment variables with a prefix
- [X] Run flask in production mode inside docker (currently runs in dev)
- [X] Limit message processing to 500 at a time
- [ ] Documentation for "running the project"
- [ ] Add label to the emails deleted, so that one can filter these emails in trash
