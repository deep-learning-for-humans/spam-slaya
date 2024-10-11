# Spam Slaya

## Problem

In today's digital world, your email address is a key part of your identity. Yet, giving it out can feel like opening the floodgates to spam and unwanted clutter. Before you know it, your inbox is overflowing, leaving you overwhelmed and missing important messages. 

**Spam Slaya** (yes, not _slayer_ but _slaya_) rose out of this personal itch that our Gmail inboxes are bloated and the search for how to clean them up.

## Solution

Our solution is to have something that helps automate email cleaning service while prioritizing your privacy. Here is how it works:

1. **Smart Automation**: It runs quietly in the background, analyzing your emails with advanced language models. It intelligently determines which emails are worth keeping and which can be safely deleted.
2. **Privacy First**: We know how vital your personal information is. That’s why our solution is a local application that runs on your own device. No data is sent to the cloud, ensuring your inbox remains just that—yours!
3. **User-Friendly**: While we recommend some technical know-how for setup, once it’s running, anyone can enjoy a clutter-free inbox without any hassle.

To get started with this, we will need to generate credentials that will allow us to connect to a Google account because we use the Gmail API to fetch your emails. 

### Caveat with Google Credentials

Because of Google’s restrictions on who can get access to email inboxes (very rightfully so), we decided that we will never be a "verified" application. Verification by Google is a long drawn process that involves multiple hoops to jump through (and keep jumping through year after year). 

We have thoroughly detailed the steps that need to be followed in the link below that will allow you to generate your Google Credentials. For each credential you generate, up to 100 people can be added to it. We recommend that you use this only for very close friends and family.

### Generating Google Credentials

#### Problem

Because the problem statement of trying to clear out our inboxes is such a privacy sensitive one, it would be a rather time taking process for a side project to go through the crazy hoops of getting "verified" so that we can offer this as a service. 

The middle ground would be to make this as simple as we can, to run this project locally or for your loved ones. 

This starts with having to get your own OAuth2 credentials (sorry).

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

4. At this stage, go to the [API Library](https://console.cloud.google.com/apis/library). This is where we will enable the APIs required.
5. The API we are interested in and need access to, is the Gmail API. You can access this via the [direct link too](https://console.cloud.google.com/apis/library/gmail.googleapis.com).
6. Click "Enable" to enable this API for the project. Once you enable it, it will take you to a API/Service details page which will show you usage of this API
7. Now we must generate credentials. To do so, click on the "Credentials" tab, or use [this link](https://console.cloud.google.com/apis/api/gmail.googleapis.com/credentials).
8. Before we generate the credentials, we must finish answering a few questions for OAuth as part of the OAuth consent screen. To start this, click the "Configure consent screen" button or use [this link](https://console.cloud.google.com/apis/credentials/consent).
    - Choose "External" for user type and hit "Create"
    - Give your app a name. I used "Clean it up". And give an email address, I used mine. Skip everything else on this page except the *Developer contact information* at the end, where again I gave my email.
    - Hit "Save and continue"
    - In the "Scopes" screen, Do the following by clicking "Add or remove scopes" button
      - Search for "Gmail API" in the filter box
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

- Install docker. We required version 2 and up.
- Generate the google credentials and download your `client_secret.json`
  - We are sorry about this, again.
- Clone the project (with git or https)
- Check the `docker-compose.yml` file and customize the variables in `environment` as per your needs
  - There are some defaults here, and these are the defaults we have used.
- Run `docker compose up` to start all the services 
- Visit `http://localhost:8080` to start using the app

**Dry run**

There is a method to dry run the entire application and we highly recommend you
run it in this mode first. That way you get a "feel" for the entire operation
and then you can run it without the dry run. 

To dry run the application, set the `SPAM_SLAYA_DRY_RUN` environment variable to
`TRUE` and emails will be processed as per usual, but no deletes will happen

## The LLM

At this point, based on our testing, we have identified that the `qwen2.5:3b-instruct-q4_0` works with a high degree of confidence. In addition, to avoid *sending* your data to anyone, we have chosen to run this via a locally running Ollama server. By our calculations, this should take, on average, a time of 40s - 60s per inference.

We do understand that taxing our users to download a ~ 2GB model file is a lot to ask, but it is a small price to pay considering that our data is not being sent to a 3rd party service. 

# Note

- We highly recommend that you read through the code, to make sure that you understand what we are doing with your data. We don’t send this information back to ourselves (there is no hosted instance anywhere). We wrote this, to solve OUR problem, and we hope that it helps solve yours too.
- The first time, we have to download the LLM. This will take some time to get (the file is about 1.7GB so it will take some time depending on your internet connection)

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
- [X] Run flask in production mode inside docker (currently runs in dev)
- [X] Limit message processing to 500 at a time
- [X] Move to `deep learning for humans`
- [X] Change name
- [X] Normalize the environment variables with a prefix
- [ ] Documentation for "running the project"
- [ ] Add label to the emails deleted, so that one can filter these emails in trash
- [ ] Remove `client_secret.json` and purge it from git. Rotate creds
