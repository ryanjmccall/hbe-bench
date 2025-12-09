import time
import random
import os
import json
import glob

# The Knowledge Base
topics = {}

topic_emojis = {
    "Hopf Optical Architecture": "🔬",
    "Physics & Solitons": "🌊",
    "Hopf Sphere Encoding": "🌐",
    "Optical Topology": "🍩",
    "Topology Basics": "⭕",
    "AlGaAs Material Science": "💎",
    "Lattice Architecture": "🕸️",
    "Advanced Geometry": "🌀",
    "The Time Engine": "⏳",
    "Hopf Index & Qudits": "🔢"
}

def load_topics(docs_dir="docs"):
    """Loads topics from JSON files in the docs directory."""
    global topics
    topics = {}
    
    # Find all JSON files in the docs directory
    # We look for files that look like topic files (have deck_name and cards)
    # n*.json files seem to be the pattern, but we also created specific topic files.
    # Let's load all .json files and check if they have the required structure.
    
    json_files = glob.glob(os.path.join(docs_dir, "*.json"))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if "deck_name" in data and "cards" in data:
                topics[data["deck_name"]] = data["cards"]
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear()
    print("🥋 WELCOME TO THE DOJO")
    print("   Internalizing the Kernel Symbols...")
    print("---------------------------------------")
    time.sleep(1)

def select_topic():
    print("\n[THE DECK PHASE]")
    print("Select a learning topic:")
    topic_names = list(topics.keys())
    for i, name in enumerate(topic_names):
        emoji = topic_emojis.get(name, "📘")
        print(f"{i+1}. {emoji} {name}")
    
    while True:
        try:
            choice = int(input(f"\n>> Choose (1-{len(topic_names)}): "))
            if 1 <= choice <= len(topic_names):
                return topic_names[choice-1]
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

def play_level_1(item):
    print(f"\n[LEVEL 1: WARM-UP]")
    # New format: item['concept']
    print(f"Term: {item.get('concept', item.get('term', 'Unknown'))}")
    
    # New format: item['levels']['1_recall']['question'] / ['answer']
    # Fallback to old format if needed, but we migrated everything.
    
    level_data = item.get('levels', {}).get('1_recall', {})
    question = level_data.get('question', f"Define {item.get('concept', 'this term')}.")
    answer = level_data.get('answer', item.get('definition', 'No definition found.'))
    
    print(f"Question: {question}")
    input(">> Press Enter to reveal answer...")
    print(f"[TRUTH]: {answer}")
    
    rating = input("\nDid you know this? (y/n): ").lower()
    if rating == 'y':
        print("Correct.")
        return True
    else:
        print("Incorrect.")
        return False

def play_level_2(item):
    print(f"\n[LEVEL 2: APPLICATION]")
    
    level_data = item.get('levels', {}).get('2_application', {})
    question = level_data.get('question', item.get('level2_q', 'No question.'))
    answer = level_data.get('answer', item.get('level2_a', ''))
    
    print(f"Challenge: {question}")
    
    user_ans = input(">> Your Answer: ").strip()
    
    # Simple normalization for checking
    if answer.lower() in user_ans.lower():
        print("✅ Correct! Optimization/Fix applied.")
        return True
    else:
        print(f"Incorrect. Expected: {answer}")
        return False

def play_level_3(item):
    print(f"\n[LEVEL 3: BOSS MODE]")
    
    level_data = item.get('levels', {}).get('3_synthesis', {})
    question = level_data.get('question', item.get('level3_q', 'No question.'))
    insight = level_data.get('insight', item.get('level3_a', 'No insight.'))
    # Note: New format uses 'insight' in level 3, old used 'level3_a' which was effectively the insight/answer.
    # Actually checking n1.json, level 3 has 'question', 'answer', 'insight'.
    # The old code printed level3_a as "Insight".
    # Let's use 'answer' + 'insight' or just 'insight' depending on what we want to show.
    # Old code: print(f"Synthesis: {item['level3_q']}") ... print(f"💡 Insight: {item['level3_a']}")
    # New format has answer AND insight. Let's show answer then insight.
    
    answer = level_data.get('answer', '')
    
    print(f"Synthesis: {question}")
    input(">> Press Enter to reveal insight...")
    print(f"[ANSWER]: {answer}")
    print(f"💡 Insight: {insight}")
    return True

def celebrate():
    print("\n" + "*"*40)
    print("🎉 GOOD JOB! YOU COMPLETED A ROUND! 🎉")
    print("*"*40)
    time.sleep(1)

def start_dojo():
    # Load topics first
    load_topics()
    
    if not topics:
        print("No topics found in docs/ directory.")
        return

    print_header()
    
    while True:
        topic_name = select_topic()
        print(f"\nLoading Deck: {topic_name}...")
        time.sleep(1)
        
        deck = topics[topic_name]
        random.shuffle(deck)
        
        # score = 0
        # max_score = len(deck) * 3 
        
        for item in deck:
            print("\n" + "="*40)
            # Level 1
            if play_level_1(item):
                # Level 2
                time.sleep(0.5)
                if play_level_2(item):
                    # Level 3
                    time.sleep(0.5)
                    play_level_3(item)
            
            time.sleep(1)
        
        celebrate()
        
        cont = input("\n⚔️  Up for another round? (y/n): ").lower()
        if cont != 'y':
            print("Exiting Dojo. Rest well, warrior.")
            break
        clear()

if __name__ == "__main__":
    start_dojo()