\# University Info Bot



> A Telegram bot for fetching details, application deadlines, and faculty lists for top US computer science universities.

>

> \\\*\\\*Live Demo:\\\*\\\* \\\[@University\\\_infobot](https://t.me/University\\\_infobot)



This project is a collection of Python scripts that scrape data from various sources (like US News and CSRankings) to build a comprehensive database of computer science programs. This data is then made available through an interactive Telegram bot.



\## 🚀 Features



\* \*\*Comprehensive# University Info Bot



> A Telegram bot for fetching details, application deadlines, and faculty lists for top US computer science universities.

>

> \\\*\\\*Live Demo:\\\*\\\* \\\[@University\\\_infobot](https://t.me/University\\\_infobot)



This project is a collection of Python scripts that scrape data from various sources (like US News and CSRankings) to build a comprehensive database of computer science programs. This data is then made available through an interactive Telegram bot.



\## 🚀 Features



\* \*\*Comprehensive Data:\*\* Scrapes university rankings, student statistics, and official websites from US News.

\* \*\*Faculty Lists:\*\* Extracts professor names, specializations, and homepages from CSRankings.

\* \*\*Deadline Search:\*\* Automatically searches Google for graduate program application deadlines.

\* \*\*Data Merging:\*\* Intelligently combines all scraped data into a single `final\\\_university\\\_database.csv` file.

\* \*\*Telegram Interface:\*\* Provides all information in a clean, paginated, and searchable format via a Telegram bot.



\## 🛠️ Installation \& Setup



\### 1. Clone the Repository



```bash

git clone \\\[https://github.com/sepehrrr4/university-bot]

cd \\\[university-bot]

```



\### 2. Create a Virtual Environment



It is highly recommended to use a virtual environment.



```bash

\\# On Windows

python -m venv venv

venv\\\\Scripts\\\\activate



\\# On macOS/Linux

python3 -m venv venv

source venv/bin/activate

```



\### 3. Install Dependencies



This project's requirements are listed in `requirements.txt`.



```bash

pip install -r requirements.txt

```



\### 4. WebDriver Setup



The scrapers use `undetected-chromedriver` and `webdriver-manager`, which will automatically download and manage the correct `chromedriver` for your system.



\*\*Your only prerequisite is to have Google Chrome installed.\*\*



\### 5. Set Up Environment Variables



The bot requires a Telegram token. Copy the example file and edit it.



```bash

\\# On Windows

copy .env.example .env



\\# On macOS/Linux

cp .env.example .env

```



Now, edit the `.env` file and add your Telegram bot token, which you can get from \[BotFather](https://t.me/BotFather).



```

TELEGRAM\\\_TOKEN="YOUR\\\_TELEGRAM\\\_BOT\\\_TOKEN\\\_HERE"

```



\## 🏃‍♂️ How to Run



There are two main steps to run this project:



\### 1. Run the Full Data Pipeline



This step runs all the scrapers and builds the final database. This script will run all other scraping scripts in the correct order.



> \\\*\\\*Note:\\\*\\\* This process can take a significant amount of time, as it scrapes many websites.



```bash

python update\\\_data.py

```

This will execute `usnews\\\_scraper.py`, `deadline\\\_scraper.py`, `web\\\_scraper.py`, and finally `merge\\\_data.py`, resulting in the `final\\\_university\\\_database.csv` file.



\### 2. Run the Telegram Bot



Once the `final\\\_university\\\_database.csv` file is successfully created, you can start the bot:



```bash

python telegram\\\_bot.py

```



The bot will load the CSV into memory and be ready to accept commands.



\## 📁 Project Structure



\* `usnews\\\_scraper.py`: Scrapes general university data and rankings from US News.

\* `web\\\_scraper.py`: Scrapes faculty (professor) lists from CSRankings.

\* `deadline\\\_scraper.py`: Scrapes application deadline information using Google search.

\* `identify\\\_failures.py`: A utility script to separate successful from failed deadline scrapes, creating a `retry\\\_list.csv`.

\* `merge\\\_data.py`: Merges data from all sources (`usnews\\\_\\\*.csv`, `successful\\\_deadlines.csv`, `all\\\_professors.csv`) into the final database.

\* `update\\\_data.py`: The main pipeline script that runs all scrapers in the correct order.

\* `telegram\\\_bot.py`: The main application logic for the Telegram bot interface.

\* `config.py`: Stores CSS selectors and configuration constants for `usnews\\\_scraper.py`.

\* `requirements.txt`: A list of all necessary Python libraries.

\* `.gitignore`: Ensures that sensitive files (like `.env`) and data files (like `\\\*.csv`) are not committed to Git. Data:\*\* Scrapes university rankings, student statistics, and official websites from US News.

\* \*\*Faculty Lists:\*\* Extracts professor names, specializations, and homepages from CSRankings.

\* \*\*Deadline Search:\*\* Automatically searches Google for graduate program application deadlines.

\* \*\*Data Merging:\*\* Intelligently combines all scraped data into a single `final\\\_university\\\_database.csv` file.

\* \*\*Telegram Interface:\*\* Provides all information in a clean, paginated, and searchable format via a Telegram bot.



\## 🛠️ Installation \& Setup



\### 1. Clone the Repository



```bash

git clone \\\[URL-TO-YOUR-REPO]

cd \\\[REPO-NAME]

```



\### 2. Create a Virtual Environment



It is highly recommended to use a virtual environment.



```bash

\\# On Windows

python -m venv venv

venv\\\\Scripts\\\\activate



\\# On macOS/Linux

python3 -m venv venv

source venv/bin/activate

```



\### 3. Install Dependencies



This project's requirements are listed in `requirements.txt`.



```bash

pip install -r requirements.txt

```



\### 4. WebDriver Setup



The scrapers use `undetected-chromedriver` and `webdriver-manager`, which will automatically download and manage the correct `chromedriver` for your system.



\*\*Your only prerequisite is to have Google Chrome installed.\*\*



\### 5. Set Up Environment Variables



The bot requires a Telegram token. Copy the example file and edit it.



```bash

\\# On Windows

copy .env.example .env



\\# On macOS/Linux

cp .env.example .env

```



Now, edit the `.env` file and add your Telegram bot token, which you can get from \[BotFather](https://t.me/BotFather).



```

TELEGRAM\\\_TOKEN="YOUR\\\_TELEGRAM\\\_BOT\\\_TOKEN\\\_HERE"

```



\## 🏃‍♂️ How to Run



There are two main steps to run this project:



\### 1. Run the Full Data Pipeline



This step runs all the scrapers and builds the final database. This script will run all other scraping scripts in the correct order.



> \\\*\\\*Note:\\\*\\\* This process can take a significant amount of time, as it scrapes many websites.



```bash

python update\\\_data.py

```

This will execute `usnews\\\_scraper.py`, `deadline\\\_scraper.py`, `web\\\_scraper.py`, and finally `merge\\\_data.py`, resulting in the `final\\\_university\\\_database.csv` file.



\### 2. Run the Telegram Bot



Once the `final\\\_university\\\_database.csv` file is successfully created, you can start the bot:



```bash

python telegram\\\_bot.py

```



The bot will load the CSV into memory and be ready to accept commands.



\## 📁 Project Structure



\* `usnews\\\_scraper.py`: Scrapes general university data and rankings from US News.

\* `web\\\_scraper.py`: Scrapes faculty (professor) lists from CSRankings.

\* `deadline\\\_scraper.py`: Scrapes application deadline information using Google search.

\* `identify\\\_failures.py`: A utility script to separate successful from failed deadline scrapes, creating a `retry\\\_list.csv`.

\* `merge\\\_data.py`: Merges data from all sources (`usnews\\\_\\\*.csv`, `successful\\\_deadlines.csv`, `all\\\_professors.csv`) into the final database.

\* `update\\\_data.py`: The main pipeline script that runs all scrapers in the correct order.

\* `telegram\\\_bot.py`: The main application logic for the Telegram bot interface.

\* `config.py`: Stores CSS selectors and configuration constants for `usnews\\\_scraper.py`.

\* `requirements.txt`: A list of all necessary Python libraries.

\* `.gitignore`: Ensures that sensitive files (like `.env`) and data files (like `\\\*.csv`) are not committed to Git.

