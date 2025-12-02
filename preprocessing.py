import re
import string

def clean_text(text):
    """
    Cleans the input text by converting to lowercase, removing punctuation,
    and removing extra whitespace.
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_aspect_sentiment(text, aspects):
    """
    Analyzes sentiment for specific aspects within the text.
    Returns a dictionary of aspect -> sentiment score/label.
    Improved version that looks at context window around aspect.
    """
    # Don't clean for aspect detection - need to preserve sentence structure
    text_lower = text.lower()
    results = {}
    DEBUG_ASPECT = False
    
    # Aspect synonyms - map related terms to main aspects
    aspect_synonyms = {
        'battery': ['battery', 'charge', 'charging', 'power', 'drain', 'drains', 'draining'],
        'screen': ['screen', 'display', 'monitor'],
        'delivery': ['delivery', 'shipping', 'ship', 'shipped', 'arrived', 'packaging', 'packaged', 'packaged well'],
        'price': ['price', 'cost', 'expensive', 'cheap', 'value', 'pricing'],
        'quality': ['quality', 'build', 'material', 'durability', 'lightweight', 'stylish', 'sleek', 'compact', 'product', 'item', 'device'],
        'performance': ['performance', 'speed', 'slow', 'lag', 'heat', 'hot', 'heating', 'overheat', 'overheating', 'fast', 'smooth', 'hangs', 'working', 'works'],
        'camera': ['camera', 'photo', 'picture', 'image'],
        'sound': ['sound', 'audio', 'speaker', 'speakers', 'volume', 'music', 'headphone'],
        'storage': ['storage', 'space', 'memory', 'sd-card', 'sdcard']
    }

    
    # Expanded positive/negative words
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'love', 'fast', 'best', 'nice', 'perfect',
        'awesome', 'fantastic', 'wonderful', 'outstanding', 'superb', 'brilliant', 'incredible',
        'stunning', 'beautiful', 'impressive', 'solid', 'strong', 'vibrant', 'clear', 'sharp',
        'reliable', 'durable', 'smooth', 'responsive', 'efficient', 'helpful', 'friendly', 'stylish', 'lightweight', 'sleek', 'compact',
        'on time', 'earlier', 'crisp', 'commendable'
    }
    
    negative_words = {
        'bad', 'terrible', 'poor', 'slow', 'worst', 'hate', 'broken', 'useless', 'disappointed',
        'disappointing', 'awful', 'horrible', 'pathetic', 'mediocre', 'inferior', 'defective',
        'faulty', 'damaged', 'inadequate', 'subpar', 'unacceptable', 'frustrating', 'annoying',
        'sluggish', 'lag', 'lagging', 'rude', 'unhelpful', 'overpriced', 'expensive', 'struggle', 'struggles', 'struggling', 'low', 'heat', 'heats', 'heating', 'hot', 'overheat', 'limited',
        'drain', 'drains', 'draining', 'delayed', 'late', 'scratches', 'scratched', 'hangs', 'stopped', 'dead', 'died'
    }

    # Additional negative phrases to capture multi-word constructs
    negative_phrases = {
        'needs improvement', 'needs to improve', 'needs improving', 'too low', 'low volume',
        'low light', 'struggles in low light', 'camera struggles',
        'limited storage', 'storage limited', 'heats up', 'heats', 'heating', 'overheat', 'overheating',
        'gets hot', 'gets hot quickly', 'hot quickly', 'warms up quickly', 'could be better', 'could be improved', 'could be lower', 'not good', 'not great',
        'stopped working', 'not working', 'drains fast', 'drains too fast', 'drains quickly', 'barely lasts', 'didn’t respond', 'did not respond'
    }

    # Phrase-aspect priority: if a phrase appears, give sentiment to that aspect and suppress others
    phrase_aspect_priority = {
        'sound quality': 'sound',
        'camera quality': 'camera',
        'display quality': 'screen',
        'screen quality': 'screen',
        'battery life': 'battery',
        'storage capacity': 'storage',
        'limited storage': 'storage',
        'speaker volume': 'sound',
        'low volume': 'sound',
        'fast delivery': 'delivery',
        'fast shipping': 'delivery',
        'build quality': 'quality'
    }
    
    # Neutral words - indicate middle-ground or average sentiment
    neutral_words = {
        'okay', 'ok', 'fine', 'decent', 'average', 'fair', 'moderate', 'acceptable', 
        'standard', 'normal', 'usual', 'ordinary', 'reasonable', 'sufficient', 'adequate',
        'alright', 'passable', 'satisfactory', 'tolerable'
    }
    
    # Intensifiers
    intensifiers = {'very', 'extremely', 'absolutely', 'really', 'incredibly', 'totally', 'completely', 'way too', 'definitely'}

    
    for aspect in aspects:
        aspect_score = 0
        count = 0
        
        # Get all synonyms for this aspect
        aspect_terms = aspect_synonyms.get(aspect, [aspect])
        
        # Find all occurrences of any aspect term
        words = text_lower.split()
        
        for i, word in enumerate(words):
            # Check if this word or nearby word contains any aspect term
            word_matches = False
            for term in aspect_terms:
                if term in word or (i > 0 and term in words[i-1]) or (i < len(words)-1 and term in words[i+1]):
                    word_matches = True
                    break
            
            if word_matches:
                # Try to detect clause/sentence around the aspect to reduce cross-aspect contamination
                clause = None
                # Split text into clauses using common conjunctions and punctuation
                # Split on commas, semicolons, colons, periods, question marks, exclamation, and key conjunctions
                split_tokens = re.split(r"\b(?:but|though|however|although|yet)\b|[\.,;:!?]", text_lower)
                for c in split_tokens:
                    if any(term in c for term in aspect_terms):
                        clause = c.strip()
                        break
                if clause:
                    context_words = clause.split()
                else:
                    # Fallback to word window
                    start = max(0, i - 5)
                    end = min(len(words), i + 6)
                    context_words = words[start:end]
                
                # Count sentiment words in context window
                pos_count = 0
                neg_count = 0
                neu_count = 0
                phrase_neg = False
                
                # Build a context string for phrase detection and determine preferred aspect
                context_string = ' '.join(context_words)
                clause_preferred_aspect = None
                for phrase, aspc in phrase_aspect_priority.items():
                    if phrase in context_string:
                        clause_preferred_aspect = aspc
                        break
                # Check negative phrases in this context window
                for neg_phrase in negative_phrases:
                    if neg_phrase in context_string:
                        phrase_neg = True
                        break

                # If this clause prefers a different aspect than the one we're checking, skip
                if clause_preferred_aspect and clause_preferred_aspect != aspect:
                    # Skip detection for this aspect in this clause (it belongs to the preferred aspect)
                    count += 0
                    continue

                for j, ctx_word in enumerate(context_words):
                    # Remove punctuation for comparison
                    clean_word = ctx_word.strip('.,!?;:')
                    
                    # Check for intensifiers before sentiment words
                    multiplier = 1
                    if j > 0 and context_words[j-1].strip('.,!?;:') in intensifiers:
                        multiplier = 2
                    
                    if clean_word in positive_words:
                        pos_count += multiplier
                    elif clean_word in negative_words:
                        neg_count += multiplier
                    elif clean_word in neutral_words:
                        neu_count += 1

                    # Negation handling: if 'not' or 'no' directly precedes a positive word
                    if clean_word in ('not', 'no') and j < len(context_words) - 1:
                        next_word = context_words[j+1].strip('.,!?;:')
                        if next_word in positive_words:
                            # Flip the sentiment of next_word
                            neg_count += 1
                            pos_count = max(0, pos_count - 1)
                
                # If we detected a negative phrase in context, treat this as negative occurrence
                if phrase_neg:
                    neg_count += 2

                if DEBUG_ASPECT and (aspect == 'performance' or phrase_neg):
                    print(f"DEBUG: aspect={aspect}, clause='{context_string}', pos={pos_count}, neg={neg_count}, neu={neu_count}, phrase_neg={phrase_neg}")

                # Determine sentiment for this occurrence
                # If neutral words are present and dominant, it's neutral
                if neu_count > 0 and pos_count == neg_count:
                    # Explicitly neutral
                    pass  # Score stays at 0
                elif pos_count > neg_count:
                    aspect_score += 1
                elif neg_count > pos_count:
                    aspect_score -= 1
                
                count += 1
        
        # Determine final sentiment
        if count > 0:
            if aspect_score > 0:
                results[aspect] = "Positive"
            elif aspect_score < 0:
                results[aspect] = "Negative"
            else:
                results[aspect] = "Neutral"
        else:
            results[aspect] = "Not Mentioned"
            
    return results


def detect_sarcasm_and_features(text, aspects=None):
    """
    Detects sarcasm-like patterns and extracts simple features that help classify
    a review into Positive/Neutral/Negative. Returns a dict with
    positive_count, negative_count, neutral_count, sarcasm_flag, contrast_flag.
    """
    # Basic features from aspect sentiment
    if aspects is None:
        aspects = ['battery', 'screen', 'delivery', 'price', 'quality', 'performance', 'camera', 'sound', 'storage']

    aspect_sentiments = get_aspect_sentiment(text, aspects)
    pos_count = sum(1 for v in aspect_sentiments.values() if v == 'Positive')
    neg_count = sum(1 for v in aspect_sentiments.values() if v == 'Negative')
    neu_count = sum(1 for v in aspect_sentiments.values() if v == 'Neutral')

    # Sarcasm heuristics - look for common sarcasm markers
    s = text.lower()
    sarcasm_phrases = [
        'which is great', 'which is awesome', 'i love how', 'i love', 'love how', 'i thanks',
        'doubles as', 'hand warmer', 'teaches patience', 'forces me', 'i always enjoy', 'i appreciate',
        'i appreciate how', 'if you like', 'if you enjoy', 'it doubles as', 'so fast that', 'best thing about',
        'finally, a', 'thanks for sending', 'my favorite', 'would recommend with caveats', 'sarcasm'
    ]
    sarcasm_flag = False
    for phrase in sarcasm_phrases:
        if phrase in s:
            sarcasm_flag = True
            break

    # Also treat unmatched positive + a negative aspect phrase as sarcasm (e.g., 'Amazing battery—dies instantly')
    if pos_count > 0 and neg_count > 0:
        # Mixed positive and negative mentions; if stylistic clues present, treat as sarcasm / mixed
        sarcasm_flag = True

    # Contrast flag if 'but' / 'though' appear (indicates mixed sentiment)
    contrast_flag = bool(re.search(r"\b(but|though|however|although|yet)\b", s))

    return {
        'pos_count': pos_count,
        'neg_count': neg_count,
        'neu_count': neu_count,
        'sarcasm': sarcasm_flag,
        'contrast': contrast_flag,
        'aspect_sentiments': aspect_sentiments
    }


def assign_three_way_label(text, aspects=None):
    """
    Assign a label for the review: 'Positive', 'Negative', or 'Neutral'
    using the heuristics: aspect-level counts + sarcasm detection.
    """
    features = detect_sarcasm_and_features(text, aspects)
    pos = features['pos_count']
    neg = features['neg_count']
    sar = features['sarcasm']
    contrast = features['contrast']

    # Basic rules
    if pos > 0 and neg == 0:
        # If sarcasm/contrast suggests flipping, treat as Neutral
        if sar and contrast:
            return 'Neutral'
        return 'Positive'
    if neg > 0 and pos == 0:
        if sar and contrast:
            return 'Neutral'
        return 'Negative'
    # Mixed aspects or sarcasm -> Neutral
    if pos > 0 and neg > 0:
        return 'Neutral'

    # Fallback to neutral if nothing mentioned
    return 'Neutral'
