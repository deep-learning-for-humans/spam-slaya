# Spam Slaya

## TODO

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
