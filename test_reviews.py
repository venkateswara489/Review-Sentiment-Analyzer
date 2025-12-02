from preprocessing import clean_text, get_aspect_sentiment, assign_three_way_label
import os

# Test reviews
reviews = [
    "The battery life is amazing! I used it for two full days without charging.",
    "Great performance, very smooth and fast. Worth every rupee.",
    "The product arrived earlier than expected and the packaging was perfect.",
    "Camera quality is crisp and clear, exactly what I wanted.",
    "Excellent build quality, feels premium in hand.",
    "Battery drains too fast, barely lasts 4 hours.",
    "Performance is very slow and the device hangs frequently.",
    "Shipping was delayed by a week, very disappointing experience.",
    "The product stopped working within three days of use.",
    "Packaging was damaged and the item had scratches.",
    "The product works fine, but nothing extraordinary.",
    "Battery life is okay, performance is average for the price.",
    "Delivery was on time, but the seller didn’t respond to my queries.",
    "Sound quality is decent, but build quality could be better.",
    "Not bad, but I expected more features based on the description.",
    "Good display quality, but battery life definitely needs improvement.",
    "Fast delivery and good packaging, but the product heats up quickly.",
    "Performance is solid, though the camera struggles in low light.",
    "Lightweight and stylish, but storage is very limited.",
    "Excellent battery and camera, but the speaker volume is too low.",
    "Good camera but overpriced. Sound quality could be better.",
]

with open('results.txt', 'w', encoding='utf-8') as f:
    f.write(f"{'Review':<80} | {'Label':<10} | {'Aspects'}\\n")
    f.write("-" * 150 + "\\n")

    aspect_list = ['battery', 'screen', 'delivery', 'price', 'quality', 'performance', 'camera', 'sound', 'storage']

    for review in reviews:
        label = assign_three_way_label(review, aspect_list)
        aspects = get_aspect_sentiment(review, aspect_list)
        
        # Format aspects
        aspect_str = ", ".join([f"{k}: {v}" for k, v in aspects.items() if v != 'Not Mentioned'])
        
        f.write(f"{review:<80} | {label:<10} | {aspect_str}\\n")
