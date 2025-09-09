import json
import re

def process_ai_output(ai_output):
    """
    Takes the output of the AI as input and creates a mapping of identifiers to descriptions and categories.
    
    Args:
        ai_output: The raw output from the AI (could be JSON string or dict, or plain text)
        
    Returns:
        dict: A dictionary with identifiers as keys and AI descriptions/categories as values
    """
    # Handle case where AI returns plain text (no leads found)
    if isinstance(ai_output, str):
        # Check if it's actually JSON wrapped in markdown
        json_match = re.search(r'```json\s*(\{.*\})\s*```', ai_output, re.DOTALL)
        if json_match:
            # Extract the JSON from the markdown code block
            json_str = json_match.group(1)
            try:
                ai_data = json.loads(json_str)
            except json.JSONDecodeError:
                print("Error parsing AI output as JSON")
                return {}
        elif ai_output.strip().startswith('{'):
            # Regular JSON string
            try:
                ai_data = json.loads(ai_output)
            except json.JSONDecodeError:
                print("Error parsing AI output as JSON")
                return {}
        else:
            # Plain text message (no leads found)
            print("No leads found by AI:", ai_output)
            return {}
    else:
        # Assume it's already a dict
        ai_data = ai_output
    
    # Handle case where AI returns an empty dict or invalid structure
    if not isinstance(ai_data, dict):
        print("AI output is not a valid dictionary")
        return {}
    
    url_description_map = {}
    
    # Process post leads
    post_leads = ai_data.get('post_leads', [])
    if post_leads:
        for lead in post_leads:
            if 'id' in lead and 'description' in lead:
                # For posts, we'll store the post ID and description
                # The full URL will be constructed later when we have subreddit info
                url_key = lead['id']  # Use the actual post ID without prefix
                url_description_map[url_key] = {
                    'description': lead['description'],
                    'category': lead.get('category', 'neutral')
                }
    
    # Process comment leads
    comment_leads = ai_data.get('comment_leads', [])
    if comment_leads:
        for lead in comment_leads:
            if 'id' in lead and 'description' in lead:
                # For comments, we'll store the comment ID and description
                # The full URL will be constructed later when we have subreddit and post info
                url_key = lead['id']  # Use the actual comment ID without prefix
                url_description_map[url_key] = {
                    'description': lead['description'],
                    'category': lead.get('category', 'neutral')
                }
    
    return url_description_map

# For testing purposes
if __name__ == "__main__":
    # Test case 1: Normal JSON output
    test_output1 = {
        "post_leads": [
            {
                "id": "111",
                "description": "User is explicitly looking to hire a YouTube editor and mentions needing good pacing, a direct match for the service.",
                "category": "hot"
            }
        ],
        "comment_leads": [
            {
                "id": "888",
                "description": "User expresses a clear pain point (editing takes too long) and a desire to delegate, making them an ideal lead.",
                "category": "cold"
            }
        ]
    }
    
    result1 = process_ai_output(test_output1)
    print("Test 1 result:", result1)
    
    # Test case 2: Empty leads
    test_output2 = {
        "post_leads": [],
        "comment_leads": []
    }
    
    result2 = process_ai_output(test_output2)
    print("Test 2 result:", result2)
    
    # Test case 3: Plain text output (no leads found)
    test_output3 = "Based on your query for video editing, I couldn't find any direct leads in this batch. You might have better luck scanning more specific subreddits like r/youtubers, r/CreatorServices, or r/forhire where creators often look for editing help."
    
    result3 = process_ai_output(test_output3)
    print("Test 3 result:", result3)
    
    # Test case 4: JSON wrapped in markdown
    test_output4 = '''```json
{
  "post_leads": [
    {
      "id": "1nak9eg",
      "description": "User is explicitly hiring a designer for a new D2C brand to create social media creatives, a direct match for graphic design services.",
      "category": "hot"
    }
  ],
  "comment_leads": []
}
```'''
    
    result4 = process_ai_output(test_output4)
    print("Test 4 result:", result4)
    
    # Test case 5: Cold leads example
    test_output5 = {
        "post_leads": [
            {
                "id": "123",
                "description": "User mentions looking for inventory management SaaS, which is a direct but cold lead for inventory management software.",
                "category": "hot"
            }
        ],
        "comment_leads": [
            {
                "id": "456",
                "description": "User spends significant time on inventory tracking, indicating a need for automation - a cold lead.",
                "category": "cold"
            }
        ]
    }
    
    result5 = process_ai_output(test_output5)
    print("Test 5 result (cold leads):", result5)