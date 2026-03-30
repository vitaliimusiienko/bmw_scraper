# BMW Used Cars Scraper 🚗

An asynchronous web scraper built with the **Scrapy** framework to collect up-to-date data on used vehicles from the official [BMW UK](https://usedcars.bmw.co.uk/) website. 

The project extracts detailed car specifications (including hidden data rendered dynamically via JavaScript) and stores them in a local SQLite database.

## 🌟 Key Features

* **API Integration:** The spider interacts directly with BMW's internal API, handling CSRF tokens and cookies to efficiently fetch the vehicle list.
* **Bypassing Dynamic Rendering (JS):** Modern dealer websites often hide crucial data (color, interior, engine size) inside React/Next.js state scripts. This scraper locates and extracts the raw JSON object (`UVL.AD`) straight from the source HTML without relying on heavy browser automation tools like Selenium or Playwright.
* **Multi-stage Data Pipelines:**
  * `ValidationPipeline`: Acts as a strict filter, dropping items that are missing required fields (e.g., missing model name) to ensure data integrity.
  * `SQLitePipeline`: Saves the cleaned data into a local database (`bmw_cars.db`). Implements UPSERT logic (`INSERT OR IGNORE`) to efficiently prevent duplicate records.
* **Unit Testing:** The core logic is covered by unit tests using `pytest`. The tests verify the parsing algorithms and pipeline behavior using an in-memory database (`:memory:`), ensuring isolated and fast test execution without leaving temporary files on the disk.

## 🛠 Tech Stack

* **Python 3.10+**
* **Scrapy** (Asynchronous web scraping framework)
* **SQLite3** (Built-in relational database)
* **Pytest** (For unit testing and coverage reporting)

## 🗄 Database Structure

The data is saved into the `bmw_cars` table with the following schema:
* `registration` (Primary Key) — Vehicle license plate
* `model` — Series (e.g., BMW X7)
* `name` — Full derivative name (e.g., X7 xDrive40i M Sport)
* `mileage` — Odometer reading
* `registered` — Registration date
* `engine` — Engine capacity (in cc)
* `range` — Electric range (in miles, for EVs/PHEVs)
* `exterior` — Exterior body color
* `fuel` — Fuel type
* `transmission` — Gearbox type
* `upholstery` — Interior trim/upholstery
* `detail_url` — Direct URL to the vehicle's page

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd bmw_scraper
   ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # For Windows:
    .venv\Scripts\activate
    # For Mac/Linux:
    source .venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the spider:**    
    ```bash
    scrapy crawl bmw_spider
    ```

Upon successful execution, a bmw_cars.db file will be generated in the project root.

## 🧪 Running Tests
**To ensure the validation and database pipelines are working correctly, run the test suite:**
```bash
python -m pytest tests/ -v
```

## 👨‍💻 Author
[Vitalii Musiienko / vitaliimusiienko]