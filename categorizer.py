import re
from typing import Dict, List

# Transaction categorization rules
CATEGORY_KEYWORDS = {
    'Food & Dining': [
        'restaurant', 'cafe', 'food', 'dining', 'pizza', 'burger', 'starbucks',
        'mcdonalds', 'subway', 'grocery', 'supermarket', 'bakery', 'bar',
        'coffee', 'lunch', 'dinner', 'breakfast', 'snack', 'doordash',
        'uber eats', 'grubhub', 'delivery', 'takeout', 'kitchen', 'deli',
        'taco bell', 'kfc', 'dominos', 'chipotle', 'panera', 'whole foods',
        'trader joes', 'safeway', 'kroger', 'target', 'walmart', 'costco'
    ],
    'Transportation': [
        'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'subway',
        'parking', 'toll', 'car', 'vehicle', 'auto', 'maintenance',
        'repair', 'insurance', 'registration', 'license', 'metro',
        'gasoline', 'petrol', 'oil change', 'tire', 'brake', 'battery',
        'mechanic', 'garage', 'tow', 'rental', 'hertz', 'avis', 'enterprise'
    ],
    'Shopping': [
        'amazon', 'walmart', 'target', 'costco', 'mall', 'store', 'shop',
        'retail', 'clothing', 'shoes', 'electronics', 'home', 'garden',
        'toys', 'books', 'music', 'movies', 'games', 'sports', 'beauty',
        'best buy', 'apple', 'nike', 'adidas', 'macys', 'nordstrom',
        'home depot', 'lowes', 'ikea', 'bed bath beyond', 'sephora'
    ],
    'Entertainment': [
        'movie', 'cinema', 'theater', 'concert', 'show', 'ticket', 'event',
        'game', 'sport', 'netflix', 'spotify', 'youtube', 'subscription',
        'entertainment', 'fun', 'party', 'club', 'bar', 'recreation',
        'amusement', 'theme park', 'zoo', 'museum', 'bowling', 'golf',
        'disney', 'hulu', 'amazon prime', 'apple music', 'xbox', 'playstation'
    ],
    'Utilities': [
        'electric', 'electricity', 'water', 'gas', 'internet', 'phone',
        'cable', 'utility', 'bill', 'service', 'power', 'heating',
        'cooling', 'trash', 'sewage', 'wifi', 'broadband', 'cellular',
        'verizon', 'att', 'tmobile', 'sprint', 'comcast', 'xfinity',
        'charter', 'spectrum', 'directv', 'dish'
    ],
    'Healthcare': [
        'hospital', 'doctor', 'medical', 'health', 'pharmacy', 'medicine',
        'dental', 'vision', 'insurance', 'clinic', 'urgent', 'care',
        'prescription', 'drug', 'therapy', 'treatment', 'checkup',
        'cvs', 'walgreens', 'rite aid', 'dentist', 'orthodontist',
        'ophthalmologist', 'dermatologist', 'cardiologist', 'pediatrician'
    ],
    'Education': [
        'school', 'university', 'college', 'tuition', 'education', 'course',
        'class', 'training', 'seminar', 'workshop', 'certification',
        'books', 'supplies', 'student', 'learning', 'academic',
        'textbook', 'online course', 'udemy', 'coursera', 'khan academy',
        'library', 'study', 'exam', 'test', 'degree'
    ],
    'Travel': [
        'hotel', 'flight', 'airline', 'airport', 'vacation', 'trip',
        'travel', 'booking', 'airbnb', 'rental', 'cruise', 'tour',
        'resort', 'accommodation', 'luggage', 'passport', 'visa',
        'expedia', 'booking.com', 'priceline', 'kayak', 'southwest',
        'delta', 'american airlines', 'united', 'jetblue', 'marriott',
        'hilton', 'hyatt', 'holiday inn'
    ],
    'Income': [
        'salary', 'wage', 'paycheck', 'bonus', 'commission', 'freelance',
        'consulting', 'dividend', 'interest', 'refund', 'cashback',
        'reward', 'gift', 'prize', 'winning', 'deposit', 'payment',
        'payroll', 'employment', 'work', 'job', 'contract', 'gig',
        'tip', 'gratuity', 'royalty', 'pension', 'social security'
    ],
    'Banking & Finance': [
        'bank', 'atm', 'fee', 'charge', 'interest', 'loan', 'credit',
        'debit', 'transfer', 'withdrawal', 'deposit', 'overdraft',
        'statement', 'account', 'finance', 'investment', 'stock', 'bond',
        'mutual fund', 'etf', 'ira', '401k', 'savings', 'checking',
        'mortgage', 'refinance', 'equity', 'portfolio', 'broker',
        'wells fargo', 'chase', 'bank of america', 'citibank', 'fidelity',
        'schwab', 'vanguard', 'etrade', 'robinhood', 'td ameritrade'
    ],
    'Home & Garden': [
        'rent', 'mortgage', 'home', 'house', 'apartment', 'property',
        'furniture', 'appliance', 'hardware', 'improvement', 'repair',
        'maintenance', 'cleaning', 'garden', 'lawn', 'tools', 'supplies',
        'home depot', 'lowes', 'ikea', 'home improvement', 'plumbing',
        'electrical', 'painting', 'flooring', 'roofing', 'hvac',
        'landscaping', 'pest control', 'security', 'renovation'
    ],
    'Personal Care': [
        'salon', 'spa', 'haircut', 'beauty', 'cosmetics', 'skincare',
        'personal', 'hygiene', 'grooming', 'massage', 'wellness',
        'fitness', 'gym', 'health', 'self-care', 'style', 'manicure',
        'pedicure', 'facial', 'eyebrow', 'waxing', 'barber',
        'planet fitness', 'la fitness', 'equinox', '24 hour fitness',
        'sephora', 'ulta', 'sally beauty'
    ],
    'Gifts & Donations': [
        'gift', 'present', 'donation', 'charity', 'contribution', 'tip',
        'gratuity', 'helping', 'support', 'fundraiser', 'cause',
        'nonprofit', 'church', 'temple', 'religious', 'giving',
        'birthday', 'anniversary', 'wedding', 'holiday', 'christmas',
        'valentine', 'mother day', 'father day', 'graduation'
    ],
    'Business': [
        'office', 'supply', 'equipment', 'software', 'license', 'service',
        'professional', 'consultant', 'meeting', 'conference', 'business',
        'work', 'expense', 'client', 'vendor', 'contract', 'invoice',
        'staples', 'office depot', 'fedex', 'ups', 'usps', 'shipping',
        'legal', 'accounting', 'marketing', 'advertising', 'website'
    ],
    'Taxes': [
        'tax', 'irs', 'refund', 'payment', 'quarterly', 'annual',
        'filing', 'preparation', 'accountant', 'government', 'federal',
        'state', 'local', 'property', 'sales', 'income', 'deduction',
        'w2', '1099', 'turbotax', 'hr block', 'jackson hewitt'
    ],
    'Insurance': [
        'insurance', 'premium', 'policy', 'coverage', 'claim', 'deductible',
        'auto insurance', 'car insurance', 'health insurance', 'life insurance',
        'home insurance', 'renters insurance', 'disability insurance',
        'allstate', 'state farm', 'geico', 'progressive', 'usaa',
        'farmers', 'nationwide', 'liberty mutual', 'aetna', 'blue cross',
        'cigna', 'humana', 'kaiser'
    ],
    'Subscriptions': [
        'subscription', 'monthly', 'annual', 'membership', 'recurring',
        'netflix', 'spotify', 'apple music', 'amazon prime', 'hulu',
        'disney plus', 'youtube premium', 'microsoft office', 'adobe',
        'dropbox', 'icloud', 'google drive', 'gym membership',
        'magazine', 'newspaper', 'streaming', 'software', 'saas'
    ]
}

def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on its description.
    
    Args:
        description: Transaction description string
        
    Returns:
        Category name as string
    """
    if not description:
        return 'Other'
    
    # Convert to lowercase for matching
    desc_lower = description.lower().strip()
    
    # Check each category for keyword matches
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in desc_lower:
                # Give higher weight to exact matches
                if keyword == desc_lower:
                    score += 10
                # Give medium weight to word boundary matches
                elif re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower):
                    score += 5
                # Give lower weight to partial matches
                else:
                    score += 1
        
        if score > 0:
            category_scores[category] = score
    
    # Return the category with the highest score
    if category_scores:
        return max(category_scores, key=category_scores.get)
    
    # Try to detect patterns for common transaction types
    if any(word in desc_lower for word in ['deposit', 'transfer in', 'payment received', 'paycheck', 'salary']):
        return 'Income'
    elif any(word in desc_lower for word in ['withdrawal', 'transfer out', 'payment to']):
        return 'Banking & Finance'
    elif any(word in desc_lower for word in ['fee', 'charge', 'penalty', 'overdraft']):
        return 'Banking & Finance'
    elif re.search(r'\d{4}\s*\d{4}\s*\d{4}\s*\d{4}', desc_lower):
        return 'Banking & Finance'  # Looks like a credit card number
    elif re.search(r'check\s*#?\s*\d+', desc_lower):
        return 'Banking & Finance'  # Check number
    elif 'atm' in desc_lower:
        return 'Banking & Finance'
    elif any(word in desc_lower for word in ['online', 'web', 'digital']):
        return 'Shopping'
    
    return 'Other'

def get_category_suggestions(description: str) -> List[str]:
    """
    Get a list of suggested categories for a transaction description.
    
    Args:
        description: Transaction description string
        
    Returns:
        List of suggested category names, sorted by relevance
    """
    if not description:
        return ['Other']
    
    desc_lower = description.lower().strip()
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in desc_lower:
                if keyword == desc_lower:
                    score += 10
                elif re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower):
                    score += 5
                else:
                    score += 1
        
        if score > 0:
            category_scores[category] = score
    
    # Sort by score and return top suggestions
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    suggestions = [cat for cat, score in sorted_categories[:5]]
    
    if not suggestions:
        suggestions = ['Other']
    
    return suggestions

def add_custom_category_rule(category: str, keywords: List[str]) -> None:
    """
    Add a custom category rule.
    
    Args:
        category: Category name
        keywords: List of keywords to match
    """
    if category not in CATEGORY_KEYWORDS:
        CATEGORY_KEYWORDS[category] = []
    
    CATEGORY_KEYWORDS[category].extend(keywords)

def get_all_categories() -> List[str]:
    """
    Get all available categories.
    
    Returns:
        List of category names
    """
    return list(CATEGORY_KEYWORDS.keys()) + ['Other']

def analyze_categorization_accuracy(transactions: List[Dict]) -> Dict:
    """
    Analyze the accuracy of automatic categorization.
    
    Args:
        transactions: List of transaction dictionaries with 'description' and 'category' keys
        
    Returns:
        Dictionary with accuracy statistics
    """
    if not transactions:
        return {'accuracy': 0, 'total': 0, 'correct': 0}
    
    correct = 0
    total = len(transactions)
    
    for transaction in transactions:
        predicted_category = categorize_transaction(transaction['description'])
        actual_category = transaction.get('category', 'Other')
        
        if predicted_category == actual_category:
            correct += 1
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    return {
        'accuracy': accuracy,
        'total': total,
        'correct': correct,
        'incorrect': total - correct
    }

def get_category_statistics(transactions: List[Dict]) -> Dict:
    """
    Get statistics about category usage.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Dictionary with category statistics
    """
    if not transactions:
        return {}
    
    category_counts = {}
    category_amounts = {}
    
    for transaction in transactions:
        category = transaction.get('category', 'Other')
        amount = abs(transaction.get('amount', 0))
        
        category_counts[category] = category_counts.get(category, 0) + 1
        category_amounts[category] = category_amounts.get(category, 0) + amount
    
    return {
        'counts': category_counts,
        'amounts': category_amounts,
        'total_transactions': len(transactions),
        'total_amount': sum(category_amounts.values())
    }

def improve_categorization(feedback: List[Dict]) -> None:
    """
    Improve categorization based on user feedback.
    
    Args:
        feedback: List of dictionaries with 'description', 'predicted', 'actual' keys
    """
    # This could be used to train a machine learning model
    # For now, we'll use rule-based improvements
    
    for item in feedback:
        description = item.get('description', '')
        predicted = item.get('predicted', '')
        actual = item.get('actual', '')
        
        if predicted != actual and actual != 'Other':
            # Extract keywords from description for the correct category
            words = re.findall(r'\b\w+\b', description.lower())
            
            # Add significant words to the correct category
            if actual in CATEGORY_KEYWORDS:
                for word in words:
                    if len(word) > 3 and word not in CATEGORY_KEYWORDS[actual]:
                        CATEGORY_KEYWORDS[actual].append(word)
