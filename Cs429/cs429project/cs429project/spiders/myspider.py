import scrapy
import requests
from ..url import url_list, domain_list
from urllib.parse import urlparse
from ..items import Cs429ProjectItem # type: ignore

class MySpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = domain_list
    start_urls = url_list
    
    custom_settings = {
        'DEPTH_LIMIT': 5,  # Max Depth
        'CLOSESPIDER_PAGECOUNT': 100,  # Max Pages
        # Add other settings like concurrent crawling and distributed crawling as required
    }


    def parse_item(self, response):
        # Define how to scrape and parse data from each page here
        # For this example, let's scrape article titles
        
        l1= ""
        # Extract URL
        url = response.url
        domain = get_domain(url)
        if 'screenrant.com' in domain:
            return self.screenrant(response)
        elif 'rottentomatoes.com' in domain:
            return self.rottomatoes(response)
         
        
            
            



    def rottomatoes(self, response):
        url = response.url
        items = Cs429ProjectItem()
        review_title = response.css('div.reviews-container h2[data-qa="reviews-title"]::text').get()
        # Get the list of names
        names = response.css('div.reviewer-name-and-publication a.display-name::text').getall()

        # Remove leading and trailing whitespace from each name, and join them with a comma
        formatted_names = ', '.join(name.strip() for name in names)

        # Print the formatted names
        #print(formatted_names)

        review = response.css('div.review-text-container p.review-text::text').getall()
        reviews = ' '.join(review)
        ogscores = response.css('div.review-text-container p.original-score-and-url::text').getall()
        # Get the list of original scores and URLs
        
        # Filter out empty strings and remove leading and trailing whitespace
        
        ogscores_cleaned = [text.strip().replace('|', '').replace('\n', ' ').strip() for text in ogscores if text.strip()]
        cleaned_ogscores = ' '.join(ogscores_cleaned)
        fin_text = reviews + cleaned_ogscores
        items['url'] = url
        items['review'] = fin_text
        items['title'] = review_title
        yield items
                
    def screenrant(self, response):
        url = response.url
        items = Cs429ProjectItem()
        headline = response.xpath('//header[@class="article_heading "]//h1[@class="heading_title"]/text()').get()
        #headline_excerpt = response.xpath('//header[@class="article_heading "]//p[@class="heading_excerpt"]/text()').get()
        author = response.xpath('//div[@class="w-author"]/a[@class="meta_txt author"]/text()').get()
        # Extract the <ul> element
        summary = response.xpath('//div[@class="custom_block-content"]/ul')

# Extract the text content from the <ul> element
        ul_text = summary.xpath('.//text()').getall()

# Remove any leading or trailing whitespace from each text item
        summary_cleaned = [text.strip() for text in ul_text if text.strip()]

# Join the cleaned text items into a single string
        summary_output = ' '.join(summary_cleaned)

        review = response.xpath('//p/text()').getall()
        reviews  = ' '.join(review)
        director_texts = response.css('div.w-display-card-info span::text').getall()
       # cleaned_director_texts = [text.strip() for text in director_texts if text.strip()]
        cleaned_director_texts = [text.strip().replace("\n", "").replace("\t", "") for text in director_texts]
        cleaned_director_text = ' '.join(cleaned_director_texts)
       # final_text = author + headline + summary_output + reviews + cleaned_director_text
        final_text = ''
        if author:
            final_text += author
        if headline:
            final_text += headline
        if summary_output:
            final_text += summary_output
        if reviews:
            final_text += reviews
        if cleaned_director_text:
            final_text += cleaned_director_text

        items['url'] = url
        items['review'] = final_text
        items['title'] = headline
        yield items

    def start_requests(self):
        # Start requests with custom callbacks
        for url in self.start_urls:
            domain = get_domain(url)
            if 'screenrant.com' in domain:
                yield scrapy.Request(url, callback=self.screenrant)
            elif 'rottentomatoes.com' in domain:
                yield scrapy.Request(url, callback=self.rottomatoes)

def get_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

#    # def test(self, response):

#         # Fetching the webpage
#         url = "https://screenrant.com/challengers-review/"
#         items = Cs429ProjectItem()
#         response = requests.get(url)
#         tree = html.fromstring(response.content)

#         # Extracting text nodes
#         text_nodes = tree.xpath('//body//text()')

#         # Cleaning and formatting the text
#         cleaned_text_nodes = [re.sub(r'\{.*?\}|\(.*?\)|\[.*?\]', '', text.strip()) for text in text_nodes]
#         formatted_text = ' '.join(filter(None, cleaned_text_nodes))

#         # Removing newline characters
#         formatted_text = formatted_text.replace('\n', '')

#         # Removing tab characters
#         formatted_text = formatted_text.replace('\t', '')

#         # Printing the formatted text
#         items['text'] = formatted_text
#         yield items
        








