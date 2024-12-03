# Atlas Accounting Web App

## Running Atlas Accounting Locally
Please navigate (`cd [name of repo root]`) to the root directory of the repository before following the below instructions.
### With Containerization
Ensure that you have [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and open
```bash
docker compose up -d --build
```
* Builds and run the application inside the container. 
* Access the app via [**http://localhost:5000**](http://localhost:5000) 

### Without Containerization
Ensure that you have a recent version of Python installed (we tested with 3.12.7)
```bash
pip install -r requirements.txt
```
* Installs all dependencies required to run the application

```bash
python main.py
```
* Starts the application from the main.py file (which contains the main method)
* Access the app via [**http://localhost:5000**](http://localhost:5000)

## Using a Python Venv (for Alembic and Package management)
```bash
pip install virtualenv
```
* Installs the virtual environment package for self contained project management.

### Venv on Windows
```bash
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
```
* Ensures that the powershell script associated with the python venv can be ran
* `-Scope Process` limits the execution policy change to the current working terminal

```bash
python -m virtualenv Atlas
```
* Ensure you have navigated to the repo folder 'Atlas-Accounting'

```bash
.\Atlas\Scripts\activate
```
* Activates the virtual environment for use

### Venv on Mac/Linux
```bash
virtualenv Atlas
```
* Ensure you have navigated to the repo folder 'Atlas-Accounting'
* NOTE: it may be something slightly different. I am on Windows so I don't have something to test with.

```bash
. Atlas/bin/activate
```
* Activates the virtual environment for use
* Use when you are about to begin working on the system.

```bash
deactivate
```
* Deactivates the virtual environment
* Use when you are done working on the system.

## Working with Alembic

```bash
alembic revision -m "[Insert Name for Revision]"
```
* This will create a manual revision in which you can migrate the database for what is required.
* `--autogenerate` does not currently function as the metadata object does reflect the database, but not in the expected way by Alembic.
* Once the revision file is created, edit the revision for what you need added, removed, or revised.

```bash
alembic upgrade x
```
* `x`: the revision to upgrade to 
    * In most cases, this will always be `head`
* This will apply the changes from the revision you just created to the database

```bash
alembic downgrade -x
```
* `-x`: the number of revisions you need the database to go backwards
    * If you wanted to go back one revision, use `-1`
* This will downgrade the database to a previous revision