# Clean that Up 

## Notes

- Storing access token, refresh token etc is a big security hassle. We will not store anything and ask people to
  authenticate everytime.
- Once the open API key is entered, we will store that along with the google given user ID. We will not store the email
  of the customer also.
- We can use celery to run the background tasks. Considering that this will be the core of the application, it makes
  sense to make this a little robust. There also seems to be https://github.com/agronholm/apscheduler but this is not
  something that I have worked with, hence going the known devil route

## Questions

- During first run, how many emails will we process? As of this writing, I (shrayas) have 76,582 emails and I think the
  window size of getting emails is 500 at a time. That means that this is a total of 153 pages of information. Where
  will we store this? How will this process happen?

## Flow

- User lands on site
- User clicks on login with google button and finishes the oauth dance
- Once dance is over, we check if that user has an OAuth Key registered previously
  - We will use the google returned ID (not email) for storing and checking this.
  - If not, we ask for it and store it.
- We will show the user last run information. This will contain a list of:
  - When they last used the app
  - How many emails were deleted in that run
- From here, the user can schedule another run, which will queue a job and give them a unique page that they can visit
  to get a status of the job
  - The same will be updated in the last run information table also
- Once the background task completes, the page will show that information. To keep things simple, there will be no email
  sent at this time (can reconsider this)
