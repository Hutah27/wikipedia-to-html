from bs4 import BeautifulSoup
import os
import requests
import json
from urllib.parse import urljoin, urlparse
from alive_progress import alive_bar 
from tqdm import tqdm
import sys

def fetch_wikipedia_content(page_title, language='en'):
    # Set the URL for the Wikipedia Parsing API
    url = f'https://{language}.wikipedia.org/w/api.php'
    
    # Parameters for the API request
    params = {
        'action': 'parse',
        'format': 'json',
        'page': page_title,
        'prop': 'text',
    }

    # Make the API request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        data = json.loads(response.text)

        # Extract the main text content from the parsed data
        if 'parse' in data and 'text' in data['parse']:
            return data['parse']['text']['*']

    return None

def extract_images_from_infobox(content):
    soup = BeautifulSoup(content, 'html.parser')
    infobox = soup.find('table', class_='infobox')
    images = []

    if infobox:
        image_tags = infobox.find_all('img')
        images.extend(tag['src'] for tag in image_tags)

    return images

def extract_images_from_gallery(content):
    soup = BeautifulSoup(content, 'html.parser')
    gallery = soup.find('div', class_='gallery')
    images = []

    if gallery:
        image_tags = gallery.find_all('img')
        images.extend(tag['src'] for tag in image_tags)

    return images

def extract_images_from_wiki_syntax(content):
    soup = BeautifulSoup(content, 'html.parser')
    images = []

    # Find images using the standard MediaWiki syntax
    wiki_syntax_tags = soup.find_all('img', {'src': True})
    images.extend(tag['src'] for tag in wiki_syntax_tags)

    return images

def download_images_and_update_html(html_content, page_title, output_directory='images', include_images=True):
    soup = BeautifulSoup(html_content, 'html.parser')

    if include_images:
        infobox_images = extract_images_from_infobox(html_content)
        gallery_images = extract_images_from_gallery(html_content)
        wiki_syntax_images = extract_images_from_wiki_syntax(html_content)

        images = infobox_images + gallery_images + wiki_syntax_images

        if images:
            page_directory = os.path.join(output_directory, page_title)
            os.makedirs(page_directory, exist_ok=True)

            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

            with tqdm(total=len(images), desc=f"Processing images for {page_title}", unit="image", unit_scale=True) as img_bar:
                for image_url in images:
                    download_image(image_url, page_directory)
                    img_bar.update(1)

            sys.stdout = original_stdout

            for img_tag in soup.find_all('img'):
                img_src = img_tag.get('src', '')
                img_filename = os.path.basename(urlparse(img_src).path)

                img_filename = "".join(c if c.isalnum() or c in {'_', '.'} else '_' for c in img_filename)

                img_tag['src'] = os.path.join(page_directory, img_filename)

                if 'srcset' in img_tag.attrs:
                    img_tag['srcset'] = img_tag['src']

def download_image(image_url, output_directory='images'):
    # Extract the image file name from the URL
    image_filename = os.path.basename(urlparse(image_url).path)

    # Download the image to the 'images' folder
    download_path = os.path.join(output_directory, image_filename)

    # Fix invalid URLs
    image_url = urljoin('https://en.wikipedia.org', image_url)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        with requests.get(image_url, stream=True, headers=headers) as response:
            response.raise_for_status()
            with open(download_path, 'wb') as image_file:
                for chunk in response.iter_content(chunk_size=8192):
                    image_file.write(chunk)
        return download_path
    except requests.exceptions.RequestException as e:
        return None

def save_to_file(page_title, content, output_directory='Wikipedia export', include_images=True, print_message=True):
    page_title_cleaned = ''.join(c if c.isalnum() or c in ['_', '-'] else '_' for c in page_title)
    filename = f'{page_title_cleaned}.html'

    print(f"Debug: page_title_cleaned: {page_title_cleaned}")
    print(f"Debug: filename: {filename}")

    page_directory = os.path.join(output_directory, page_title_cleaned)
    os.makedirs(page_directory, exist_ok=True)  # Create the directory if it doesn't exist

    if include_images:
        download_images_and_update_html(content, page_title_cleaned, output_directory=page_directory)

    with open(os.path.join(page_directory, filename), 'w', encoding='utf-8') as file:
        if include_images:
            file.write(content)
        else:
            # Remove all img tags
            soup = BeautifulSoup(content, 'html.parser')
            for img_tag in soup.find_all('img'):
                img_tag.extract()  # Remove the img tag
            file.write(str(soup))

    if include_images:
        infobox_images = extract_images_from_infobox(content)
        gallery_images = extract_images_from_gallery(content)
        wiki_syntax_images = extract_images_from_wiki_syntax(content)

        images = infobox_images + gallery_images + wiki_syntax_images

        if images:
            page_directory = os.path.join(output_directory, page_title)
            os.makedirs(page_directory, exist_ok=True)

            filename_mapping = {}
            for image_url in images:
                new_filename = download_image(image_url, page_directory)

                if new_filename:
                    original_filename = os.path.basename(urlparse(image_url).path)
                    cleaned_filename = ''.join(c for c in original_filename if c.isalnum() or c in ['.', '_', '-'])
                    new_filename_cleaned = os.path.join(page_directory, cleaned_filename)

                    counter = 1
                    while os.path.exists(new_filename_cleaned):
                        new_filename_cleaned = os.path.join(page_directory, f"{cleaned_filename}_{counter}")
                        counter += 1

                    os.rename(new_filename, new_filename_cleaned)
                    filename_mapping[original_filename] = new_filename_cleaned

            soup = BeautifulSoup(content, 'html.parser')
            for img_tag in soup.find_all('img'):
                if include_images:  # Add this condition
                    img_src = img_tag.get('src', '')
                    img_filename = os.path.basename(urlparse(img_src).path)

                    new_filename = filename_mapping.get(img_filename)
                    if new_filename:
                        img_tag['src'] = os.path.relpath(new_filename, page_directory)

                    if 'srcset' in img_tag.attrs:
                        img_tag['srcset'] = img_tag['src']

            with open(os.path.join(page_directory, filename), 'w', encoding='utf-8') as file:
                file.write(str(soup))
            if print_message:
                print(f"Content saved to {filename}")
        else:
            print(f"No images found for '{page_title}'.")
    else:
        if print_message:
            print(f"Content saved to {filename}")


if __name__ == "__main__":
    include_images_input = input("Do you want to include images? (yes/no): ").lower()
    include_images = include_images_input == 'yes'

    print("Enter Wikipedia page names one per line. Press Enter on an empty line to finish.")
    page_titles = []
    while True:
        page_title = input("Enter page name: ")
        if not page_title:
            break
        page_titles.append(page_title.strip())

    with tqdm(total=len(page_titles), desc="Processing Pages", unit="page") as bar:
        for page_title in page_titles:
            article_content = fetch_wikipedia_content(page_title)

            if article_content:
                save_to_file(page_title, article_content, include_images=include_images, print_message=False)
            else:
                print(f"Page '{page_title}' does not exist on Wikipedia or the content could not be retrieved.")

            bar.update(1)

    # Thank the user and credit the author
print("\nThank you for using the Wikipedia to HTML exporter.") 
print("Author: Gurwinder Singh")  
print("Version: 1.0")  
print("For any issues, please contact on Upwork: freelancers/~0162de9053b9e180f4")
