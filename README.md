# Spam Slaya

## Problem

In today's digital world, your email address is a key part of your identity. Yet, giving it out can feel like opening the floodgates to spam and unwanted clutter. Before you know it, your inbox is overflowing, leaving you overwhelmed and missing important messages. 

**Spam Slaya** (yes, not _slayer_ but _slaya_) rose out of this personal itch that our Gmail inboxes are bloated and the search for how to clean them up.

## Solution

At the core, the solution looks something like 

```py
for email in inbox:
  result = ai.infer(email)
  if result.is_spam:
    queue_for_delete(email)
```

But this raises 2 important questions

1. Is each email in the inbox is sent to an AI for inference?
2. Why should I give **you** access to **my** inbox?

**Is each email in the inbox is sent to an AI for inference?**

The short answer is **yes**. 

The long answer is that it is sent to an AI but **not sent outside** your machine. The entire solution relies on Ollama at the core, to keep everything running locally. No data is sent to the cloud, ensuring your inbox remains just that — yours!

**Why should I give _you_ access to _my_ inbox?**

You don't need to. Google already makes this hard by requesting that anyone requesting for access to "sensitive data" (like reading the content of emails, deleting,  etc) needs to undergo a _verification_ process that is long and comprehensive (with good reason). 

For this reason, we require you to generate your own credentials to use the app. It takes a few minutes, but is worth it because you get an extra layer of confidence.

Additionally, any emails that we delete, we add a `Spam Slaya` label on them, so that it will make it easier to filter by this, to see which emails were deleted from the app. This will allow you to easily track down the deletes and act on them, should you need to.

---

Fundamentally, the core of the solution is this: 

- My Inbox
- My AI
- My Compute
- My Credentials

We get **no access** to anything from your end. 

A guarentee like this, requires some technical know-how for setup, but once it’s running, you and your friends & family can enjoy a clutter-free inbox without any hassle.

So let's get started.

### Generating Google Credentials

Because of Google’s restrictions on who can get access to email inboxes (very rightfully so), we decided that **we will never be a "verified" application**. 

We have thoroughly detailed the steps that need to be followed in the link below that will allow you to generate your Google Credentials. For each credential you generate, up to 100 people can be added to it. We recommend that you use this only for very close friends and family.


#### Process

> [!IMPORTANT]  
> This process does not need you to add a billing account

1. To start off, go to the [Google Cloud Console](https://console.cloud.google.com) and login with your gmail account 
2. Start by [create a project](https://console.cloud.google.com/projectcreate). Give it a meaningful name. This will be the place where you will have to generate the credentials to use this. I have chosen to name mine as "clean it up". Once it has created, select that project

<table>
  <tbody>
    <tr>
      <td>
        <img src="https://github.com/user-attachments/assets/166f6f41-7401-4589-897d-069fcc7e8a03" />
      </td>
      <td>
          <img src="https://github.com/user-attachments/assets/4551bc9e-ee09-4af6-94f1-44c393393cd1" />
      </td>
    </tr>
  </tbody>
</table>

3. You will be able to tell that the project is selected, if you see the name come up in the dashboard and on the dropdown on top

<table>
  <tbody>
    <tr>
      <td>
        <img src="https://github.com/user-attachments/assets/f98f4657-58d7-48dd-a971-e8cf03979068" />
      </td>
    </tr>
  </tbody>
</table>

4. At this stage, in the [API Library](https://console.cloud.google.com/apis/library), we can enable the APIs required.
5. The API we are interested in and need access to, is the Gmail API. You can access this via the [direct link too](https://console.cloud.google.com/apis/library/gmail.googleapis.com).
6. Click "Enable" to enable this API for the project. Once you enable it, it will take you to a API/Service details page which will show you usage of this API
7. Now we must generate credentials. To do so, click on the "Credentials" tab, or use [this link](https://console.cloud.google.com/apis/api/gmail.googleapis.com/credentials).
8. Before we generate the credentials, we must finish answering a few questions for OAuth as part of the OAuth consent screen. To start this, click the "Configure consent screen" button or use [this link](https://console.cloud.google.com/apis/credentials/consent).
    - Choose "External" for user type and hit "Create"
    - Give your app a name. I used "Clean it up". And give an email address, I used mine. Skip everything else on this page except the *Developer contact information* at the end, where again I gave my email.
    - Hit "Save and continue"
    - In the "Scopes" screen, Do the following by clicking "Add or remove scopes" button
      - Search for "Gmail API" in the filter box (set rows per page to **20** for quick searchability)
      - Select scope `https://mail.google.com/` that allows for *Read, compose, send and permanently delete all your email from Gmail*
      - Select scope `.../auth/gmail.readonly` that allows for *View your email messages and setting*s
      - Select scope `.../auth/gmail.labels` that allows for *See and edit your email labels*

<table>
  <tbody>
    <tr>
      <td>
        <img src="https://github.com/user-attachments/assets/11eeb4ee-dd68-427b-abfa-7197cf236a96" />
      </td>
    </tr>
  </tbody>
</table>

9. On the "Test users" page, is where you add your email and the email of the loved ones that you want to give access to this, to. You can give 100 people access. The idea is that this project will forever remain in "test mode" and never get out of it. Thus you being the administrator, can control who gets access to this app, simply by adding or removing them from this page. 
10. Once that is done, hit "Save and continue" and this will show you a summary. Hit "Back to dashboard". We are now ready to create the credentials. 
11. Go back to the ["Gmail API API/Service details page"](https://console.cloud.google.com/apis/api/gmail.googleapis.com/credentials) and hit the "create credentials" button and select "OAuth Client ID".
12. In the page that comes up, select "Web application" and name it. Under "Authorised redirect URIs" enter the redirect URI
    - If you are hosting this locally, it can be something like `http://localhost:8080/oauth2callback`
    - If you are hosting this for others to be used, the starting part of the URI will change but it has to end with `/oauth2callback`. We recommend using HTTPS (via caddy) to ease your deployment out.
13. Once that is done, hit "Create" and it will present you with a popup with your credentials
    - On this screen, you are presented with the credentials required to use the app.
    - Hit "Download JSON" and save this json to a place of your choice.

<table>
  <tbody>
    <tr>
      <td>
        <img src="https://github.com/user-attachments/assets/f97de02a-0bb4-4532-b264-8effa73016a6" />
      </td>
    </tr>
  </tbody>
</table>

    
**Keep it safe.**

<details>
  <summary>
    If you missed doing this, then click on the app and you can download the JSON from that page too.
  </summary>

  <table>
    <tbody>
      <tr>
        <td>
          <img src="https://github.com/user-attachments/assets/b14c0a08-0585-4a44-b946-07ff79cbae78" />
        </td>
      </tr>
    </tbody>
  </table>

</details>

# Running the project

## Recommended way (docker)

- Install docker. We required version 2 and up.
- Generate the google credentials and download your `client_secret.json`
  - We are sorry about this, again.
- Clone the project (with git or https)
- Drop the `client_secret.json` inside the cloned folder
- Check the `docker-compose.yml` file and customize the variables in `environment` as per your needs
  - There are some defaults here, and these are the defaults we have used.
- Run `docker compose up` to start all the services 
- Visit `http://localhost:8080` to start using the app

## For development

- For development you need 3 things installed
  1. Python
  2. Ollama
  3. Redis
- Run redis 
- Run Ollama
- Create a virtual env
- Run `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and set the required variables
- Run `python worker.py`
- Run `python run.py`

# Dry run

There is a method to dry run the entire application and we highly recommend you
run it in this mode first. That way you get a "feel" for the entire operation
and then you can run it without the dry run. 

To dry run the application, set the `SPAM_SLAYA_DRY_RUN` environment variable to
`TRUE` and emails will be processed as per usual, but no deletes will happen

# Demo

Below is a full run of the application. Please note that the initial 4 minutes and 11 seconds are spent to download the LLM. It is intentionally kept to show the **full** end to end usage of the application.

https://github.com/user-attachments/assets/8c05ced6-ca26-4b7d-aca3-fb173299d0f8

_Note: This is a little outdated, will update it soon. The fundamental flow remains the same however_

# The LLM

At this point, based on our testing, we have identified that the `qwen2.5:3b-instruct-q4_0` works with a high degree of confidence. In addition, to avoid *sending* your data to anyone, we have chosen to run this via a locally running Ollama server. By our calculations, this should take, on average, a time of 40s - 60s per inference.

We do understand that taxing our users to download a ~ 2GB model file is a lot to ask, but it is a small price to pay considering that our data is not being sent to a 3rd party service. 

This can be customized by setting the `SPAM_SLAYA_OLLAMA_MODEL` variable in the `docker-compose.yml` file.

# Note

- We highly recommend that you read through the code, to make sure that you understand what we are doing with your data. We don’t send this information back to ourselves (there is no hosted instance anywhere). We wrote this, to solve OUR problem, and we hope that it helps solve yours too.
- The first time, we have to download the LLM. This will take some time to get (the file is about 1.7GB so it will take some time depending on your internet connection)

# TODO

- [ ] Setup demo.spamslaya.com
- [ ] Test with replicate for FF setup
- [ ] Slay OTP emails that are more than 1 week old
  - [ ] Populate now - email date somewhere to do OTP operations on
