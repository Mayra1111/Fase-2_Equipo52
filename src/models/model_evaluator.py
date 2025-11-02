"""
Model evaluation module
Handles evaluation, comparison, and visualization of models
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix
)

from ..utils.config import FIGURES_DIR
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """
    Evaluates and compares multiple models
    """
    
    def __init__(
        self,
        models: Dict[str, Any],
        predictions: Dict[str, np.ndarray],
        y_test: pd.Series,
        class_names: List[str],
        output_dir: Path = FIGURES_DIR
    ):
        """
        Initialize ModelEvaluator
        
        Args:
            models: Dictionary of trained models
            predictions: Dictionary of predictions
            y_test: Test labels
            class_names: List of class names
            output_dir: Directory to save figures
        """
        self.models = models
        self.predictions = predictions
        self.y_test = y_test
        self.class_names = class_names
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("ModelEvaluator initialized")
    
    def create_metrics_dataframe(self) -> pd.DataFrame:
        """
        Create comparative metrics dataframe
        
        Returns:
            DataFrame with metrics for all models
        """
        logger.info("Creating metrics comparison dataframe...")
        
        metrics_data = []
        
        for name, pred in self.predictions.items():
            metrics_data.append({
                'Modelo': name,
                'Accuracy': accuracy_score(self.y_test, pred),
                'Precision': precision_score(self.y_test, pred, average='weighted'),
                'Recall': recall_score(self.y_test, pred, average='weighted'),
                'F1-score': f1_score(self.y_test, pred, average='weighted')
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        logger.info(f"Metrics dataframe created with {len(metrics_df)} models")
        
        return metrics_df
    
    def plot_metrics_comparison(
        self,
        metrics_df: pd.DataFrame,
        filename: str = "07_metrics_comparison"
    ):
        """
        Plot comparative bar chart of metrics
        
        Args:
            metrics_df: DataFrame with metrics
            filename: Output filename
        """
        logger.info("Plotting metrics comparison...")
        
        plt.figure(figsize=(12, 7))
        metrics_df.set_index('Modelo').plot(
            kind='bar',
            ax=plt.gca(),
            colormap='viridis'
        )
        plt.title('Comparación de métricas de rendimiento', fontsize=16, fontweight='bold')
        plt.ylabel('Valor', fontsize=12)
        plt.ylim(0, 1)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend(loc='lower right')
        plt.tight_layout()
        
        filepath = self.output_dir / f"{filename}.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        logger.info(f"Metrics comparison saved: {filepath}")
        plt.close()
    
    def plot_confusion_matrices(
        self,
        filename: str = "08_confusion_matrices"
    ):
        """
        Plot confusion matrices for all models
        
        Args:
            filename: Output filename
        """
        logger.info("Plotting confusion matrices...")
        
        n_models = len(self.predictions)
        fig, axes = plt.subplots(n_models, 1, figsize=(10, 6 * n_models))
        
        if n_models == 1:
            axes = [axes]
        
        colors = ['Blues', 'Greens', 'Reds', 'Purples', 'Oranges']
        
        for idx, (name, pred) in enumerate(self.predictions.items()):
            cm = confusion_matrix(self.y_test, pred)
            
            sns.heatmap(
                cm,
                annot=True,
                fmt='d',
                cmap=colors[idx % len(colors)],
                ax=axes[idx],
                xticklabels=self.class_names,
                yticklabels=self.class_names
            )
            axes[idx].set_title(f'Matriz de confusión - {name}', fontsize=14, fontweight='bold')
            axes[idx].set_xlabel('Predicho', fontsize=12)
            axes[idx].set_ylabel('Real', fontsize=12)
        
        plt.tight_layout()
        
        filepath = self.output_dir / f"{filename}.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        logger.info(f"Confusion matrices saved: {filepath}")
        plt.close()
    
    def evaluate_overfitting(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> pd.DataFrame:
        """
        Evaluate overfitting/underfitting for all models
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            
        Returns:
            DataFrame with overfitting analysis
        """
        logger.info("Evaluating overfitting/underfitting...")
        
        results = []
        
        for name, model in self.models.items():
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            gap = train_score - test_score
            
            # Determine status
            if gap > 0.1:
                status = "Overfitting"
            elif gap < -0.05:
                status = "Underfitting"
            else:
                status = "Good fit"
            
            results.append({
                'Modelo': name,
                'Train Score': train_score,
                'Test Score': test_score,
                'Gap': gap,
                'Status': status
            })
            
            logger.info(f"{name}: Train={train_score:.3f}, Test={test_score:.3f}, Gap={gap:.3f} ({status})")
        
        return pd.DataFrame(results)
    
    def plot_overfitting_analysis(
        self,
        overfitting_df: pd.DataFrame,
        filename: str = "09_overfitting_analysis"
    ):
        """
        Plot overfitting analysis
        
        Args:
            overfitting_df: DataFrame with overfitting metrics
            filename: Output filename
        """
        logger.info("Plotting overfitting analysis...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Train vs Test scores
        x = np.arange(len(overfitting_df))
        width = 0.35
        
        ax1.bar(x - width/2, overfitting_df['Train Score'], width, label='Train', alpha=0.8)
        ax1.bar(x + width/2, overfitting_df['Test Score'], width, label='Test', alpha=0.8)
        ax1.set_xlabel('Modelo', fontsize=12)
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Train vs Test Scores', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(overfitting_df['Modelo'], rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Plot 2: Gap visualization
        colors = ['red' if gap > 0.1 else 'orange' if gap < -0.05 else 'green' 
                  for gap in overfitting_df['Gap']]
        
        ax2.barh(overfitting_df['Modelo'], overfitting_df['Gap'], color=colors, alpha=0.7)
        ax2.set_xlabel('Gap (Train - Test)', fontsize=12)
        ax2.set_title('Overfitting Gap Analysis', fontsize=14, fontweight='bold')
        ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
        ax2.axvline(x=0.1, color='red', linestyle='--', alpha=0.5, label='Overfitting threshold')
        ax2.axvline(x=-0.05, color='orange', linestyle='--', alpha=0.5, label='Underfitting threshold')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / f"{filename}.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        logger.info(f"Overfitting analysis saved: {filepath}")
        plt.close()
    
    def generate_all_plots(
        self,
        metrics_df: pd.DataFrame,
        overfitting_df: pd.DataFrame
    ):
        """
        Generate all evaluation plots
        
        Args:
            metrics_df: Metrics comparison dataframe
            overfitting_df: Overfitting analysis dataframe
        """
        logger.info("="*70)
        logger.info("GENERATING ALL EVALUATION VISUALIZATIONS")
        logger.info("="*70)
        
        self.plot_metrics_comparison(metrics_df)
        self.plot_confusion_matrices()
        self.plot_overfitting_analysis(overfitting_df)
        
        logger.info("="*70)
        logger.info("ALL EVALUATION VISUALIZATIONS GENERATED")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*70)
