# wikipedia-to-html
This Python script allows you to scrape Wikipedia content and save it along with images locally.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python 3
- Required Python packages: `beautifulsoup4`, `requests`, `tqdm`, `alive-progress`

You can install the required packages using the following command:

`pip install beautifulsoup4 requests tqdm alive-progress`


# How to use

* Clone the repository:

  ```python
  git clone https://github.com/your-username/html-wiki-exporter.git
  cd html-wiki-exporter
  ```

* Run the script:

  ```python
  python wiki-to-html.py
  ```
1. Follow the prompts to provide input. The script will prompt you for the following:
    1. Whether you want to include images (type yes or no).
    2. Enter Wikipedia page names one per line. Press Enter on an empty line to finish.

2. The script will create a directory named **WikiExport** (or use the existing one if available) and store the exported HTML files along with images inside individual folders for each Wikipedia page.

# Script Overview
* The script uses the Wikipedia Parsing API to fetch content in HTML format.
* It extracts images from infoboxes, galleries, and standard MediaWiki syntax.
* Optionally, it downloads images and updates HTML files with local paths.
* The script saves each Wikipedia page's content in an HTML file along with images in a separate folder.

# Note
* Image downloading is optional and can be disabled by entering **'no'** when prompted.
* The script uses an API call to fetch Wikipedia content, so avoid making too many requests in a short time to prevent IP blocking.

❗Feel free to modify and enhance the script based on your requirements.


```python
Replace 'your-username' in the clone URL with your GitHub username. Customize the script name ('wiki-to-html.py') and directory name ('WikiExport') as needed for your project.
```
# Author
+ Author: Gurwinder Singh
+ Version: 1.0
+ Contact Author: For any issues or inquiries, please get in touch with the author on Upwork: [Author's Upwork Profile](https://upwork.com/freelancers/~0162de9053b9e180f4)
