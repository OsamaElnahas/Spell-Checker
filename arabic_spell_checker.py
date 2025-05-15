import tkinter as tk
from tkinter import messagebox, ttk
from difflib import get_close_matches
import arabic_reshaper
from bidi.algorithm import get_display
import re

# Load dictionary from external file
def load_dictionary(path):
    with open(path, encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

# Normalize Arabic text for better matching
def normalize_arabic(text):
    text = re.sub(r'[\u064B-\u0652]', '', text)
    text = re.sub(r'[ى]', 'ي', text)
    text = re.sub(r'ـ', '', text)
    return text

# Correct a word using close matches and return multiple suggestions
def correct_word(word, dictionary):
    normalized = normalize_arabic(word)
    if normalized in dictionary:
        return []
    matches = get_close_matches(normalized, dictionary, n=3, cutoff=0.6)
    return matches

# Spell check a full sentence with suggestions
def check_spelling(text, dictionary):
    words = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    corrected_words = []
    corrections = {}
    suggestions_dict = {}

    for i, word in enumerate(words):
        if re.match(r'[\u0600-\u06FF]', word):
            normalized = normalize_arabic(word)
            if normalized not in dictionary:
                sug = correct_word(word, dictionary)
                if sug:
                    corrected_words.append(sug[0])
                    suggestions_dict[i] = sug
                    corrections[i] = f'"{word}" → "{sug[0]}"'
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)

    corrected_text = ' '.join(corrected_words)
    return corrected_text, corrections, suggestions_dict

# Run spell check and show suggestions in the main window
def run_spell_check():
    text = input_text.get("1.0", "end-1c").strip()
    if not text:
        messagebox.showwarning("تحذير", "الرجاء إدخال نص")
        return
    
    corrected_text, corrections, suggestions_dict = check_spelling(text, dictionary)
    
    output_text.delete("1.0", "end")
    output_text.insert("1.0", corrected_text)
    
    corrections_label.config(text=f"عدد التصحيحات: {len(corrections)}")
    
    for widget in suggestions_frame.winfo_children():
        widget.destroy()

    if suggestions_dict:
        selected_vars = {}  
        
        tk.Label(suggestions_frame, text="الاقتراحات:", font=("Arial", 14)).pack()
        for idx, sug_list in suggestions_dict.items():
            if sug_list:
                original_word = text.split()[idx] if idx < len(text.split()) else sug_list[0]
                tk.Label(suggestions_frame, text=f"الكلمة: {original_word}", font=("Arial", 12), bg="#f5f5f5", fg="#333").pack(anchor="w", pady=2)
                
                var = tk.StringVar(value=sug_list[0])
                radio_frame = tk.Frame(suggestions_frame, bg="#f5f5f5")
                radio_frame.pack(anchor="w", pady=2)
                for sug in sug_list:
                    sug_display = get_display(arabic_reshaper.reshape(sug))
                    tk.Radiobutton(radio_frame, text=sug_display, variable=var, value=sug, font=("Arial", 12), bg="#f5f5f5", fg="#555", selectcolor="#e0e0e0", anchor="w", padx=15, pady=5).pack(side=tk.LEFT)
                
                selected_vars[idx] = var  

        # زر تطبيق واحد لكل الاقتراحات
        def apply_all_corrections():
            new_text = corrected_text.split()
            for idx, var in selected_vars.items():
                new_text[idx] = var.get()
            final_text = " ".join(new_text)
            output_text.delete("1.0", "end")
            output_text.insert("1.0", final_text)
            for widget in suggestions_frame.winfo_children():
                widget.destroy()

        tk.Button(suggestions_frame, text="تطبيق الكل", command=apply_all_corrections, font=("Arial", 12), bg="#1E90FF", fg="white", bd=0, padx=15, pady=8, relief="flat").pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("Spell Checker")
root.geometry("800x700")
root.configure(bg="#E6E9EF")

main_frame = tk.Frame(root, bg="#E6E9EF")
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

input_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=2, relief="flat")
input_frame.pack(fill="x", pady=(0, 10))

label_input = tk.Label(input_frame, text="أدخل النص هنا:", bg="#FFFFFF", font=("Arial", 14, "bold"), fg="#333")
label_input.pack(anchor="w", pady=(10, 5))

input_text = tk.Text(input_frame, height=5, width=70, font=("Arial", 12), wrap=tk.WORD, bd=1, relief="solid", bg="#F9F9F9")
input_text.pack(pady=(0, 10), padx=10, fill="x")

button_frame = tk.Frame(main_frame, bg="#E6E9EF")
button_frame.pack(fill="x", pady=5)

check_button = tk.Button(button_frame, text="أختبر النص", font=("Arial", 12), bg="#1E90FF", fg="white", bd=0, padx=15, pady=5, relief="flat", command=run_spell_check)
check_button.pack(side=tk.RIGHT, padx=5)

corrections_label = tk.Label(button_frame, text="عدد التصحيحات: 0", bg="#E6E9EF", font=("Arial", 12), fg="#555")
corrections_label.pack(side=tk.RIGHT, padx=10)

output_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=2, relief="flat")
output_frame.pack(fill="x", pady=10)

label_output = tk.Label(output_frame, text="النص الصحيح:", bg="#FFFFFF", font=("Arial", 14, "bold"), fg="#333")
label_output.pack(anchor="w", pady=(10, 5))

output_text = tk.Text(output_frame, height=5, width=70, font=("Arial", 12), wrap=tk.WORD, bd=1, relief="solid", bg="#F9F9F9")
output_text.pack(pady=(0, 10), padx=10, fill="x")

suggestions_frame = tk.Frame(main_frame, bg="#f5f5f5", bd=2, relief="flat")
suggestions_frame.pack(fill="both", expand=True, pady=10)

try:
    dictionary = load_dictionary("list.txt")
    if not dictionary:
        messagebox.showerror("خطأ", "القاموس فاضي أو لم يتم تحميله")
except:
    dictionary = []
    messagebox.showerror("خطأ", "فشل تحميل القاموس الافتراضي")

root.mainloop()