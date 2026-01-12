"""
LLM Generator - Training pipeline templates

Generates LLM training pipelines with best practices:
- Data collection and deduplication
- Data cleaning and normalization
- Training with checkpointing
- Learning rate scheduling
- Early stopping
- Validation on held-out data
- Hyperparameter logging

The presence is precision.
"""

from typing import Optional


class LLMGenerator:
    """Generates LLM training pipelines."""
    
    def generate_training_pipeline(
        self,
        model_name: str,
        data_source: str,
        framework: str = "pytorch"
    ) -> str:
        """Generate a complete LLM training pipeline."""
        if framework.lower() == "pytorch":
            return self._generate_pytorch_pipeline(model_name, data_source)
        elif framework.lower() == "tensorflow":
            return self._generate_tensorflow_pipeline(model_name, data_source)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _generate_pytorch_pipeline(
        self,
        model_name: str,
        data_source: str
    ) -> str:
        """Generate PyTorch training pipeline."""
        return f'''#!/usr/bin/env python3
"""
LLM Training Pipeline: {model_name}
Framework: PyTorch
Data Source: {data_source}
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)
from torch.utils.tensorboard import SummaryWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LLMDataset(Dataset):
    """Custom dataset for LLM training."""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 512):
        """Initialize dataset."""
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self._load_and_preprocess()
    
    def _load_and_preprocess(self) -> List[Dict]:
        """Load and preprocess data."""
        logger.info(f"Loading data from {{self.data_path}}")
        
        # Load raw data
        with open(self.data_path, 'r') as f:
            raw_data = [json.loads(line) for line in f]
        
        # Deduplicate
        logger.info("Deduplicating data...")
        seen = set()
        deduplicated = []
        for item in raw_data:
            text = item.get('text', '')
            if text not in seen:
                seen.add(text)
                deduplicated.append(item)
        
        logger.info(f"Deduplicated: {{len(raw_data)}} -> {{len(deduplicated)}} samples")
        
        # Clean and normalize
        logger.info("Cleaning and normalizing data...")
        cleaned = []
        for item in deduplicated:
            text = item.get('text', '').strip()
            if text:  # Filter empty
                cleaned.append({{'text': text}})
        
        logger.info(f"Cleaned: {{len(deduplicated)}} -> {{len(cleaned)}} samples")
        
        return cleaned
    
    def __len__(self):
        """Return dataset length."""
        return len(self.data)
    
    def __getitem__(self, idx):
        """Get item by index."""
        text = self.data[idx]['text']
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {{
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
        }}


class LLMTrainer:
    """LLM Training orchestrator."""
    
    def __init__(
        self,
        model_name: str = "{model_name}",
        output_dir: str = "./outputs",
        checkpoint_dir: str = "./checkpoints"
    ):
        """Initialize trainer."""
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.checkpoint_dir = Path(checkpoint_dir)
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {{self.device}}")
        
        # Initialize model and tokenizer
        logger.info(f"Loading model: {{self.model_name}}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        
        # Training state
        self.best_loss = float('inf')
        self.patience_counter = 0
        
        # TensorBoard
        self.writer = SummaryWriter(log_dir=str(self.output_dir / 'tensorboard'))
    
    def train(
        self,
        train_data_path: str,
        val_data_path: str,
        epochs: int = 3,
        batch_size: int = 8,
        learning_rate: float = 5e-5,
        warmup_steps: int = 500,
        early_stopping_patience: int = 3,
        gradient_accumulation_steps: int = 1,
    ):
        """Train the model."""
        logger.info("Starting training pipeline...")
        
        # Load datasets
        train_dataset = LLMDataset(train_data_path, self.tokenizer)
        val_dataset = LLMDataset(val_data_path, self.tokenizer)
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=4
        )
        
        # Optimizer and scheduler
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        # Training loop
        global_step = 0
        
        for epoch in range(epochs):
            logger.info(f"Epoch {{epoch + 1}}/{{epochs}}")
            
            # Training phase
            self.model.train()
            train_loss = 0
            
            for batch_idx, batch in enumerate(train_loader):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=input_ids
                )
                
                loss = outputs.loss / gradient_accumulation_steps
                loss.backward()
                
                # Gradient accumulation
                if (batch_idx + 1) % gradient_accumulation_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
                    global_step += 1
                
                train_loss += loss.item()
                
                # Log progress
                if batch_idx % 100 == 0:
                    logger.info(
                        f"Batch {{batch_idx}}/{{len(train_loader)}} - "
                        f"Loss: {{loss.item():.4f}}"
                    )
                
                # TensorBoard logging
                self.writer.add_scalar('train/loss', loss.item(), global_step)
                self.writer.add_scalar('train/lr', scheduler.get_last_lr()[0], global_step)
            
            avg_train_loss = train_loss / len(train_loader)
            logger.info(f"Average training loss: {{avg_train_loss:.4f}}")
            
            # Validation phase
            val_loss = self._validate(val_loader)
            logger.info(f"Validation loss: {{val_loss:.4f}}")
            
            # TensorBoard logging
            self.writer.add_scalar('val/loss', val_loss, epoch)
            
            # Checkpointing
            self._save_checkpoint(epoch, val_loss)
            
            # Early stopping
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.patience_counter = 0
                self._save_best_model()
            else:
                self.patience_counter += 1
                if self.patience_counter >= early_stopping_patience:
                    logger.info(f"Early stopping triggered after {{epoch + 1}} epochs")
                    break
        
        logger.info("Training completed!")
        self.writer.close()
    
    def _validate(self, val_loader):
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=input_ids
                )
                
                total_loss += outputs.loss.item()
        
        return total_loss / len(val_loader)
    
    def _save_checkpoint(self, epoch: int, loss: float):
        """Save training checkpoint."""
        checkpoint_path = self.checkpoint_dir / f"checkpoint_epoch_{{epoch}}.pt"
        
        torch.save({{
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'loss': loss,
        }}, checkpoint_path)
        
        logger.info(f"Checkpoint saved: {{checkpoint_path}}")
    
    def _save_best_model(self):
        """Save best model."""
        best_model_path = self.output_dir / "best_model"
        self.model.save_pretrained(best_model_path)
        self.tokenizer.save_pretrained(best_model_path)
        
        logger.info(f"Best model saved: {{best_model_path}}")


def main():
    """Main training function."""
    # Hyperparameters (can be loaded from config)
    config = {{
        'model_name': '{model_name}',
        'train_data': '{data_source}',
        'val_data': '{data_source.replace(".jsonl", "_val.jsonl")}',
        'epochs': 3,
        'batch_size': 8,
        'learning_rate': 5e-5,
        'warmup_steps': 500,
        'early_stopping_patience': 3,
    }}
    
    # Log hyperparameters
    logger.info("Hyperparameters:")
    for key, value in config.items():
        logger.info(f"  {{key}}: {{value}}")
    
    # Save hyperparameters
    with open('hyperparameters.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Initialize trainer
    trainer = LLMTrainer(
        model_name=config['model_name'],
        output_dir='./outputs',
        checkpoint_dir='./checkpoints'
    )
    
    # Train
    trainer.train(
        train_data_path=config['train_data'],
        val_data_path=config['val_data'],
        epochs=config['epochs'],
        batch_size=config['batch_size'],
        learning_rate=config['learning_rate'],
        warmup_steps=config['warmup_steps'],
        early_stopping_patience=config['early_stopping_patience'],
    )


if __name__ == "__main__":
    main()
'''
    
    def _generate_tensorflow_pipeline(
        self,
        model_name: str,
        data_source: str
    ) -> str:
        """Generate TensorFlow training pipeline."""
        return f'''#!/usr/bin/env python3
"""
LLM Training Pipeline: {model_name}
Framework: TensorFlow
Data Source: {data_source}
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

import tensorflow as tf
from transformers import TFAutoModelForCausalLM, AutoTokenizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def load_and_preprocess_data(data_path: str):
    """Load and preprocess training data."""
    logger.info(f"Loading data from {{data_path}}")
    
    with open(data_path, 'r') as f:
        data = [json.loads(line) for line in f]
    
    # Deduplicate
    seen = set()
    deduplicated = []
    for item in data:
        text = item.get('text', '')
        if text not in seen:
            seen.add(text)
            deduplicated.append(item)
    
    logger.info(f"Deduplicated: {{len(data)}} -> {{len(deduplicated)}} samples")
    
    return deduplicated


def create_dataset(data, tokenizer, max_length=512, batch_size=8):
    """Create TensorFlow dataset."""
    texts = [item['text'] for item in data]
    
    def generator():
        for text in texts:
            encoding = tokenizer(
                text,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_tensors='tf'
            )
            yield encoding['input_ids'][0], encoding['attention_mask'][0]
    
    dataset = tf.data.Dataset.from_generator(
        generator,
        output_signature=(
            tf.TensorSpec(shape=(max_length,), dtype=tf.int32),
            tf.TensorSpec(shape=(max_length,), dtype=tf.int32)
        )
    )
    
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)


def main():
    """Main training function."""
    logger.info("Starting TensorFlow training pipeline...")
    
    # Configuration
    config = {{
        'model_name': '{model_name}',
        'train_data': '{data_source}',
        'val_data': '{data_source.replace(".jsonl", "_val.jsonl")}',
        'epochs': 3,
        'batch_size': 8,
        'learning_rate': 5e-5,
    }}
    
    # Load model and tokenizer
    logger.info(f"Loading model: {{config['model_name']}}")
    tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
    model = TFAutoModelForCausalLM.from_pretrained(config['model_name'])
    
    # Load and prepare data
    train_data = load_and_preprocess_data(config['train_data'])
    val_data = load_and_preprocess_data(config['val_data'])
    
    train_dataset = create_dataset(train_data, tokenizer, batch_size=config['batch_size'])
    val_dataset = create_dataset(val_data, tokenizer, batch_size=config['batch_size'])
    
    # Compile model
    optimizer = tf.keras.optimizers.Adam(learning_rate=config['learning_rate'])
    model.compile(optimizer=optimizer)
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            'checkpoints/checkpoint_{{epoch}}.h5',
            save_weights_only=True
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True
        ),
        tf.keras.callbacks.TensorBoard(log_dir='./logs'),
    ]
    
    # Train
    logger.info("Starting training...")
    model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=config['epochs'],
        callbacks=callbacks
    )
    
    # Save final model
    model.save_pretrained('./outputs/final_model')
    tokenizer.save_pretrained('./outputs/final_model')
    
    logger.info("Training completed!")


if __name__ == "__main__":
    main()
'''


__all__ = ['LLMGenerator']
