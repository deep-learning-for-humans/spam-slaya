# Clean that Up 

## Notes

- Storing access token, refresh token etc is a big security hassle. We will not
  store anything and ask people to authenticate everytime.
- Once the open API key is entered, we will store that along with the google
  given user ID. We will not store the email of the customer also.
- We can use celery to run the background tasks. Considering that this will be
  the core of the application, it makes sense to make this a little robust.
    - We will use this over https://github.com/agronholm/apscheduler because we
      have already used this
- We will use SQLite as the DB to store whatever data we wish to have
- The first time processing is our USP. As a result, we must do this right. The
  first background job will be time consuming but it is what will give the users
  the most storage savings. So we need to do this right
- Repeat processing depends on if there is an API that allows us to get emails
  since a particular time. That way we can only process those emails for storage
  benefits instead of processing the entire lot again
    - Of course we can implement this ourselves by keeping a list of message
      IDs that we have already processed (this can come as next development)

## Questions

- Once a background job is scheduled, the page that the user is redirected to,
  needs no authentication. This greatly simplifies our flow because even if the
  OAuth token has expired, we will not need to login again or do anything of
  that kind. Is this OK? 

## Flow

- User lands on site
- User clicks on login with google button and finishes the oauth dance
- Once dance is over, we check if that user has an OAuth Key registered
  previously
  - We will use the google returned ID (not email) for storing and checking
    this.
  - If not, we ask for it and store it.
- We will show the user last run information. This will contain a list of:
  - When they last used the app
  - How many emails were deleted in that run
- If there were no last runs, we will show a button to schedule a first run.
  This needs to have some disclaimer about how much time it will take
    - Running this on our mailboxes ought to give us a good understanding of
      the amount of time it will take and we should extrapolate from that
- If there were last runs, from the same page, the user can schedule another
  run,
- Once a run is queued, the user will be redirected to another page that is
  unique to that run. This page will have the status of the operation and the
  elapsed time.
    - This page will refresh every minute automatically
    - We should show information about how many emails have been processed and
      how many are remaining
- Once the background task completes, the page will show that information. To
  keep things simple, there will be no email sent at this time 

## TODO

- [ ] Remove all existing POC code (bootstrap, etc) and keep only bare minimum OAuth flow
- [ ] Introduce dependencies - SQLite, Celery 
- [ ] Get user ID from Gmail via oauth and store in DB
- [ ] Store Open API Key in SQLite 
- [ ] Create background job to get emails
- [ ] Write status page
- [ ] Wire in LLM logic (Rags)