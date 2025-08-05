import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_runway_events():
    """
    Scrape event links from Runway Playa Vista events page
    """
    url = "https://www.runwayplayavista.com/events2"
    
    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the request
        print(f"Fetching events from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all event links using the provided CSS selector
        event_links = soup.select('div.eventlist.eventlist--upcoming > article.eventlist-event > a')
        
        events = []
        for link in event_links:
            href = link.get('href')
            if href:
                # Get event title from the link text or title attribute
                title = link.get_text(strip=True) or link.get('title', 'No title')
                
                event_info = {
                    'title': title,
                    'url': 'https://www.runwayplayavista.com/' + href,
                    'scraped_at': datetime.now().isoformat()
                }
                events.append(event_info)
                print(f"Found event: {title} - {href}")
        
        print(f"\nTotal events found: {len(events)}")
        
        return events
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the webpage: {e}")
        return []

def scrape_event_details(event_url):
    """
    Scrape detailed information from an individual event page
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(event_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract event details using the provided selectors
        details = {}
        
        # Title
        title_elem = soup.select_one('h1.eventitem-title')
        details['title'] = title_elem.get_text(strip=True) if title_elem else 'No title found'
        
        # Date
        date_elem = soup.select_one('time.event-date')
        if date_elem:
            # Extract just the date part (remove day of week)
            full_date_text = date_elem.get_text(strip=True)
            # Split by comma and take the part after the first comma (removes day)
            date_parts = full_date_text.split(', ', 1)
            if len(date_parts) > 1:
                details['date'] = date_parts[1]  # "August 6, 2025"
            else:
                details['date'] = full_date_text  # Fallback to full text if no comma
            details['date_datetime'] = date_elem.get('datetime', '')
        else:
            details['date'] = 'No date found'
            details['date_datetime'] = ''
        
        # Start time
        start_time_elem = soup.select_one('time.event-time-localized-start')
        details['start_time'] = start_time_elem.get_text(strip=True) if start_time_elem else 'No start time found'
        
        # End time
        end_time_elem = soup.select_one('time.event-time-localized-end')
        details['end_time'] = end_time_elem.get_text(strip=True) if end_time_elem else 'No end time found'
        
        # Book link
        book_link_elem = soup.select_one('a.sqs-block-button-element--medium.sqs-button-element--primary.sqs-block-button-element')
        if book_link_elem:
            details['book_link'] = book_link_elem.get('href', '')
            details['book_link_text'] = book_link_elem.get_text(strip=True)
        else:
            details['book_link'] = ''
            details['book_link_text'] = ''
        
        # Description
        desc_elem = soup.select_one('div.sqs-block.html-block.sqs-block-html')
        if desc_elem:
            # Get text with proper spacing
            description_text = desc_elem.get_text(separator=' ', strip=True)
            # Clean up multiple spaces
            import re
            description_text = re.sub(r'\s+', ' ', description_text)
            details['description'] = description_text
        else:
            details['description'] = 'No description found'
        
        return details
        
    except Exception as e:
        print(f"Error scraping event details from {event_url}: {e}")
        return {
            'title': '',
            'date': '',
            'start_time': '',
            'end_time': '',
            'book_link': '',
            'description': f'Error: {str(e)}'
        }

def scrape_all_event_details(events):
    """
    Scrape detailed information for all events
    """
    detailed_events = []
    
    for i, event in enumerate(events, 1):
        print(f"Scraping details for event {i}/{len(events)}: {event['title']}")
        
        # Get detailed information
        details = scrape_event_details(event['url'])
        
        # Combine basic and detailed information
        detailed_event = {
            'url': event['url'],
            'scraped_at': event['scraped_at'],
            **details
        }
        
        detailed_events.append(detailed_event)
        
        # Small delay to be respectful to the server
        import time
        time.sleep(1)
    
    return detailed_events

if __name__ == "__main__":
    # First get the list of events
    events = scrape_runway_events()
    
    if events:
        print(f"\nScraping detailed information for {len(events)} events...")
        
        # Then get detailed information for each event
        detailed_events = scrape_all_event_details(events)
        
        # Save detailed events to JSON
        with open('runway_events_detailed.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_events, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed events saved to runway_events_detailed.json")
        
    else:
        print("No events found to scrape details for.")
