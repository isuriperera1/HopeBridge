# -*- coding: utf-8 -*-
"""Bert_Emotion_Model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11zEIdkNj2CqAjlOXJlWTBDUORLN6sSHp
"""

!pip install datasets

import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer
from datasets import load_dataset
from collections import Counter

model = TFAutoModel.from_pretrained("bert-base-uncased")

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

inputs = tokenizer(['Hello', 'How are you'], padding=True, truncation=True, return_tensors='tf')
inputs

output = model(inputs)
output

emotions = load_dataset('SetFit/emotion')

emotions

print("Sample Entries from the Training Dataset:")
print(emotions['train'][:5])

train_labels = emotions['train']['label']
label_counts = Counter(train_labels)

print("\nLabel Distribution in Training Data:")
for label, count in label_counts.items():
    print(f"Label {label}: {count}")

def tokenize(batch): return tokenizer(batch['text'], padding=True, truncation=True, max_length=128)

emotions_encoded = emotions.map(tokenize, batched=True, batch_size=None)

emotions_encoded

emotions_encoded.set_format('tf', columns=['input_ids', 'attention_mask', 'token_type_ids', 'label'])


BATCH_SIZE = 64

def order(inp):
    data = list(inp.values())
    return {
        'input_ids': data[1],
        'attention_mask': data[2],
        'token_type_ids': data[3]
    }, data[0]

# converting train split of `emotions_encoded` to tensorflow format
train_dataset = tf.data.Dataset.from_tensor_slices(emotions_encoded['train'][:])
# set batch_size and shuffle
train_dataset = train_dataset.batch(BATCH_SIZE).shuffle(1000)
# map the `order` function
train_dataset = train_dataset.map(order, num_parallel_calls=tf.data.AUTOTUNE)

# doing the same for test set
test_dataset = tf.data.Dataset.from_tensor_slices(emotions_encoded['test'][:])
test_dataset = test_dataset.batch(BATCH_SIZE)
test_dataset = test_dataset.map(order, num_parallel_calls=tf.data.AUTOTUNE)

inp, out = next(iter(train_dataset))
print(inp, '\n\n', out)

from collections import Counter
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

# Get class distribution
labels = emotions_encoded['train']['label']
# Convert the labels to a NumPy array to make it hashable
labels = np.array(labels)
class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(labels), y=labels)
class_weights_dict = {i: weight for i, weight in enumerate(class_weights)}

print("Class Weights:", class_weights_dict)

class BERTForClassification(tf.keras.Model):
    def __init__(self, bert_model, num_classes):
        super().__init__()
        self.bert = bert_model
        self.fc = tf.keras.layers.Dense(num_classes, activation='softmax')

    def call(self, inputs):
        x = self.bert(inputs)[1]
        return self.fc(x)

    def get_config(self):
        config = super().get_config()
        config.update({
            "num_classes": self.fc.units,  # Store number of output classes
        })
        return config

    @classmethod
    def from_config(cls, config):
        from transformers import TFBertModel  # Import BERT model
        bert_model = TFBertModel.from_pretrained("bert-base-uncased")  # Load base model again
        return cls(bert_model, config["num_classes"])

classifier = BERTForClassification(model, num_classes=6)

classifier.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

history = classifier.fit(
    train_dataset,
    epochs=3,
    class_weight=class_weights_dict  # Apply computed class weights
)

classifier.evaluate(test_dataset)

def test_emotions_with_label_text(texts, classifier, tokenizer):
    """
    Predicts the emotion of input texts and maps them to emotion labels directly.

    Args:
        texts (list): List of text strings to classify.
        classifier: Trained BERT classifier model.
        tokenizer: Tokenizer used during training.

    Returns:
        None. Prints out the text and its predicted emotion.
    """
    # Define explicit label mapping based on dataset index
    label_mapping = {
        0: "sadness",
        1: "joy",
        2: "love",
        3: "anger",
        4: "fear",
        5: "surprise"
    }

    # Tokenize the input text
    inputs = tokenizer(
        texts, padding=True, truncation=True, max_length=128, return_tensors="tf"
    )

    # Get predictions
    # The classifier outputs probabilities, not logits directly.
    probs = classifier(inputs)
    # We don't need to apply softmax again as it's already applied in the model.
    # probs = tf.nn.softmax(logits, axis=1)
    predictions = tf.argmax(probs, axis=1).numpy()  # Convert probabilities to predicted label indices

    # Map predictions to emotion labels
    predicted_emotions = [label_mapping[pred] for pred in predictions]

    # Print results
    print("\nPredicted Emotions:")
    for text, emotion in zip(texts, predicted_emotions):
        print(f"Text: '{text}' => Predicted Emotion: {emotion}")


# Example texts to classify
test_texts = [
    "I feel so empty inside.",
    "Damn shes a great girl to love",
    "I can't take this pain anymore.",
    "I don't want to be here anymore.",
    "Why does everything hurt so much?",
    "I feel so alone in this world.",
    "I just want to end my life",
    "I can't escape my thoughts.",
    "I am getting more creative now. I love what I do",
    "todays game was awesome. what a great dayyyy",
    "I am so happy about my life, what a joyful day ",
    "I love going out with him ",
    "I literally hate my life. I cant do this anymore",
    "I’m surrounded by people who care about me.",
    "I'm feeling hopeless about the future.",
    "I want to kill that person. I cant do this anymore"
]

# Call the function with the test texts
test_emotions_with_label_text(test_texts, classifier, tokenizer)

import tensorflow as tf
import shutil
from google.colab import files

# Define save paths
model_save_path = "bert_emotion_model"
tokenizer_save_path = "tokenizer"

# Save the model
classifier.save(model_save_path)

# Save the tokenizer
tokenizer.save_pretrained(tokenizer_save_path)

# Zip the model and tokenizer for download
shutil.make_archive(model_save_path, 'zip', model_save_path)
shutil.make_archive(tokenizer_save_path, 'zip', tokenizer_save_path)

# Download model and tokenizer
files.download(model_save_path + ".zip")
files.download(tokenizer_save_path + ".zip")