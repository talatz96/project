import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding
from datasets import Dataset
import os

# Load data from SQLite DB
conn = sqlite3.connect("../db/social_media.db")
df = pd.read_sql_query("SELECT title, label FROM reddit_labelled WHERE label IS NOT NULL", conn)
conn.close()

# Preprocessing
df = df.dropna(subset=["title", "label"])
df['title'] = df['title'].astype(str)
df['label'] = df['label'].astype(int)
df = df.rename(columns={"title": "text", "label": "label"})
print(f"Total rows: {len(df)}")
print(df['label'].unique())
print(df['label'].dtype)



# Controlled oversampling for 1:3 class ratio
cyberhate_df = df[df['label'] == 1]
non_cyberhate_df = df[df['label'] == 0]
oversampled_cyberhate_df = cyberhate_df.sample(n=477, replace=True, random_state=42)
balanced_df = pd.concat([non_cyberhate_df, oversampled_cyberhate_df]).sample(frac=1, random_state=42)

# Split into train/val/test
train_val_df, test_df = train_test_split(balanced_df, test_size=0.15, stratify=balanced_df['label'], random_state=42)
train_df, val_df = train_test_split(train_val_df, test_size=0.1765, stratify=train_val_df['label'], random_state=42)

# Load tokenizer and model
tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
model = RobertaForSequenceClassification.from_pretrained("roberta-base", num_labels=2)

# Tokenize datasets
def tokenize_function(example):
    return tokenizer(example["text"], truncation=True)

train_dataset = Dataset.from_pandas(train_df).map(tokenize_function, batched=True)
val_dataset   = Dataset.from_pandas(val_df).map(tokenize_function, batched=True)
test_dataset  = Dataset.from_pandas(test_df).map(tokenize_function, batched=True)

# Collator
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Training arguments
training_args = TrainingArguments(
    output_dir="./roberta-cyberhate",
    do_train=True,
    do_eval=True,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    save_total_limit=1,
    logging_dir="./logs",
    logging_steps=100,
    save_steps=500,
    eval_steps=500
)

# Custom metrics
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    preds = predictions.argmax(axis=-1)
    report = classification_report(labels, preds, output_dict=True)
    return {
        "accuracy": report["accuracy"],
        "precision_cyberhate": report["1"]["precision"],
        "recall_cyberhate": report["1"]["recall"],
        "f1_cyberhate": report["1"]["f1-score"]
    }

# Disable wandb
os.environ["WANDB_DISABLED"] = "true"

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

# Train model
trainer.train()

# Evaluate on test set
print("📊 Final test set evaluation:")
metrics = trainer.evaluate(test_dataset)
print(metrics)

# Save model and tokenizer for later use (e.g., Hugging Face upload)
model.save_pretrained("roberta_cyberhate_trained")
tokenizer.save_pretrained("roberta_cyberhate_trained")
