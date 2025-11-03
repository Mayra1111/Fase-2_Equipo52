"""
EDA Visualization Module
Generates professional visualizations for exploratory data analysis
All plots are saved as PNG files in the reports/figures directory
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import warnings

from ..utils.config import FIGURES_DIR
from ..utils.logger import get_logger

warnings.filterwarnings('ignore')
logger = get_logger(__name__)


class EDAVisualizer:
    """
    Class to generate and save EDA visualizations
    """
    
    def __init__(self, output_dir: Path = FIGURES_DIR):
        """
        Initialize EDA Visualizer
        
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_theme(style="whitegrid")
        plt.style.use('default')
        
        logger.info(f"EDA Visualizer initialized. Output dir: {self.output_dir}")
    
    def _save_figure(self, filename: str, dpi: int = 300):
        """
        Save current figure to file
        
        Args:
            filename: Name of the file (without extension)
            dpi: Resolution in dots per inch
        """
        filepath = self.output_dir / f"{filename}.png"
        plt.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')
        logger.info(f"✓ Figure saved: {filepath}")
        plt.close()
    
    def plot_dataset_overview(self, df: pd.DataFrame, filename: str = "01_dataset_overview"):
        """
        Generate overview visualizations of the dataset
        
        Args:
            df: Input DataFrame
            filename: Name for the output file
        """
        logger.info("Generating dataset overview visualization...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Información General del Dataset', fontsize=16, fontweight='bold')
        
        # 1. Data types distribution
        dtype_counts = df.dtypes.value_counts()
        axes[0, 0].pie(
            dtype_counts.values,
            labels=dtype_counts.index,
            autopct='%1.1f%%',
            colors=sns.color_palette("coolwarm", len(dtype_counts))
        )
        axes[0, 0].set_title('Distribución de Tipos de Datos')
        
        # 2. Missing values
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_data[missing_data > 0].plot(kind='bar', ax=axes[0, 1], color='coral')
            axes[0, 1].set_title('Valores Nulos por Columna')
            axes[0, 1].tick_params(axis='x', rotation=45)
        else:
            axes[0, 1].text(
                0.5, 0.5, 'No hay valores nulos',
                ha='center', va='center',
                transform=axes[0, 1].transAxes,
                fontsize=14
            )
            axes[0, 1].set_title('Valores Nulos por Columna')
        
        # 3. Unique values per column
        unique_counts = [df[col].nunique() for col in df.columns]
        axes[1, 0].bar(range(len(df.columns)), unique_counts, color='skyblue')
        axes[1, 0].set_title('Valores Únicos por Columna')
        axes[1, 0].set_xlabel('Columnas')
        axes[1, 0].set_ylabel('Valores Únicos')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Memory usage per column
        memory_usage = df.memory_usage(deep=True, index=False) / 1024**2  # MB
        axes[1, 1].bar(range(len(df.columns)), memory_usage, color='lightgreen')
        axes[1, 1].set_title('Uso de Memoria por Columna (MB)')
        axes[1, 1].set_xlabel('Columnas')
        axes[1, 1].set_ylabel('Memoria (MB)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        self._save_figure(filename)
        
        # Log summary statistics
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Total missing values: {missing_data.sum()}")
        logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    def plot_numeric_distributions(
        self,
        df: pd.DataFrame,
        numeric_cols: Optional[List[str]] = None,
        filename: str = "02_numeric_distributions"
    ):
        """
        Generate distribution plots for numeric variables
        
        Args:
            df: Input DataFrame
            numeric_cols: List of numeric columns to plot (auto-detect if None)
            filename: Name for the output file
        """
        logger.info("Generating numeric distributions visualization...")
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            logger.warning("No numeric columns found")
            return
        
        n_cols = 3
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6 * n_rows))
        fig.suptitle('Distribución de Variables Numéricas', fontsize=16, fontweight='bold')
        
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, col in enumerate(numeric_cols):
            row = i // n_cols
            col_idx = i % n_cols
            
            # Histogram with KDE
            sns.histplot(
                df[col].dropna(),
                kde=True,
                ax=axes[row, col_idx],
                color=sns.color_palette("coolwarm", 1)[0],
                alpha=0.7
            )
            axes[row, col_idx].set_title(f'{col}', fontweight='bold')
            axes[row, col_idx].set_xlabel(col)
            axes[row, col_idx].set_ylabel('Frecuencia')
            
            # Add statistics
            mean_val = df[col].mean()
            median_val = df[col].median()
            
            axes[row, col_idx].axvline(
                mean_val, color='red', linestyle='--',
                alpha=0.8, label=f'Media: {mean_val:.2f}'
            )
            axes[row, col_idx].axvline(
                median_val, color='green', linestyle='--',
                alpha=0.8, label=f'Mediana: {median_val:.2f}'
            )
            axes[row, col_idx].legend(fontsize=8)
        
        # Hide empty subplots
        for i in range(len(numeric_cols), n_rows * n_cols):
            row = i // n_cols
            col_idx = i % n_cols
            axes[row, col_idx].set_visible(False)
        
        plt.tight_layout()
        self._save_figure(filename)
        
        logger.info(f"Generated distributions for {len(numeric_cols)} numeric variables")
    
    def plot_numeric_boxplots(
        self,
        df: pd.DataFrame,
        numeric_cols: Optional[List[str]] = None,
        filename: str = "03_numeric_boxplots"
    ):
        """
        Generate boxplots for outlier detection
        
        Args:
            df: Input DataFrame
            numeric_cols: List of numeric columns to plot (auto-detect if None)
            filename: Name for the output file
        """
        logger.info("Generating boxplots for outlier detection...")
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) == 0:
            logger.warning("No numeric columns found")
            return
        
        n_cols = 4
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
        fig.suptitle('Box Plots - Detección de Outliers', fontsize=16, fontweight='bold')
        
        if len(numeric_cols) == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        
        axes_flat = axes.flatten() if n_rows > 1 or len(numeric_cols) > 1 else [axes]
        
        for i, col in enumerate(numeric_cols):
            # Box plot
            box_plot = axes_flat[i].boxplot(
                df[col].dropna(),
                patch_artist=True,
                boxprops=dict(facecolor=sns.color_palette("coolwarm", 1)[0], alpha=0.7),
                medianprops=dict(color='red', linewidth=2),
                whiskerprops=dict(color='black', linewidth=1.5),
                capprops=dict(color='black', linewidth=1.5)
            )
            
            axes_flat[i].set_title(f'{col}', fontweight='bold')
            axes_flat[i].set_ylabel(col)
            
            # Calculate outliers
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            outlier_percentage = len(outliers) / len(df) * 100
            
            # Add statistics
            stats_text = f'Outliers: {len(outliers)}\n({outlier_percentage:.1f}%)'
            axes_flat[i].text(
                0.02, 0.98, stats_text,
                transform=axes_flat[i].transAxes,
                verticalalignment='top',
                fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            )
        
        # Hide empty subplots
        for i in range(len(numeric_cols), len(axes_flat)):
            axes_flat[i].set_visible(False)
        
        plt.tight_layout()
        self._save_figure(filename)
        
        logger.info(f"Generated boxplots for {len(numeric_cols)} numeric variables")
    
    def plot_categorical_distributions(
        self,
        df: pd.DataFrame,
        categorical_cols: Optional[List[str]] = None,
        filename: str = "04_categorical_distributions"
    ):
        """
        Generate distribution plots for categorical variables
        
        Args:
            df: Input DataFrame
            categorical_cols: List of categorical columns (auto-detect if None)
            filename: Name for the output file
        """
        logger.info("Generating categorical distributions visualization...")
        
        if categorical_cols is None:
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if len(categorical_cols) == 0:
            logger.warning("No categorical columns found")
            return
        
        n_cols = 2
        n_rows = (len(categorical_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 8 * n_rows))
        fig.suptitle('Distribución de Variables Categóricas', fontsize=16, fontweight='bold')
        
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, col in enumerate(categorical_cols):
            row = i // n_cols
            col_idx = i % n_cols
            
            value_counts = df[col].value_counts()
            
            # Horizontal bar chart (better for many categories)
            if len(value_counts) > 8:
                top_values = value_counts.head(8)
                bars = axes[row, col_idx].barh(
                    range(len(top_values)),
                    top_values.values,
                    color=sns.color_palette("viridis", len(top_values))
                )
                axes[row, col_idx].set_yticks(range(len(top_values)))
                axes[row, col_idx].set_yticklabels(top_values.index, fontsize=10)
                axes[row, col_idx].set_title(f'{col} (Top 8)', fontweight='bold', fontsize=12)
            else:
                bars = axes[row, col_idx].barh(
                    range(len(value_counts)),
                    value_counts.values,
                    color=sns.color_palette("viridis", len(value_counts))
                )
                axes[row, col_idx].set_yticks(range(len(value_counts)))
                axes[row, col_idx].set_yticklabels(value_counts.index, fontsize=10)
                axes[row, col_idx].set_title(f'{col}', fontweight='bold', fontsize=12)
            
            axes[row, col_idx].set_xlabel('Frecuencia', fontsize=10)
            
            # Add values on bars
            for j, bar in enumerate(bars):
                width = bar.get_width()
                percentage = (width / len(df)) * 100
                axes[row, col_idx].text(
                    width + width * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    f'{int(width)} ({percentage:.1f}%)',
                    ha='left', va='center',
                    fontsize=8, fontweight='bold'
                )
        
        # Hide empty subplots
        for i in range(len(categorical_cols), n_rows * n_cols):
            row = i // n_cols
            col_idx = i % n_cols
            axes[row, col_idx].set_visible(False)
        
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(top=0.93)
        self._save_figure(filename)
        
        logger.info(f"Generated distributions for {len(categorical_cols)} categorical variables")
    
    def plot_target_distribution(
        self,
        df: pd.DataFrame,
        target_col: str = 'NObeyesdad',
        filename: str = "05_target_distribution"
    ):
        """
        Generate special visualization for target variable
        
        Args:
            df: Input DataFrame
            target_col: Name of the target column
            filename: Name for the output file
        """
        logger.info(f"Generating target distribution for {target_col}...")
        
        if target_col not in df.columns:
            logger.warning(f"Target column '{target_col}' not found")
            return
        
        target_counts = df[target_col].value_counts()
        target_percentages = df[target_col].value_counts(normalize=True) * 100
        
        plt.figure(figsize=(12, 6))
        
        # Horizontal bar chart with coolwarm colors
        colors = sns.color_palette("coolwarm", len(target_counts))
        bars = plt.barh(
            range(len(target_counts)),
            target_counts.values,
            color=colors,
            edgecolor='white',
            linewidth=1.5,
            alpha=0.8
        )
        
        plt.title(
            f'Distribución de la Variable Objetivo ({target_col})',
            fontsize=14, fontweight='bold'
        )
        plt.xlabel('Número de Personas', fontsize=12)
        plt.ylabel('Categoría de Obesidad', fontsize=12)
        plt.yticks(range(len(target_counts)), target_counts.index)
        
        # Add values on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            percentage = target_percentages.iloc[i]
            plt.text(
                width + width * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f'{int(width)} ({percentage:.1f}%)',
                ha='left', va='center',
                fontweight='bold', fontsize=10
            )
        
        plt.grid(axis='x', alpha=0.3, linestyle='--')
        plt.tight_layout()
        self._save_figure(filename)
        
        # Log balance information
        balance_ratio = target_counts.max() / target_counts.min()
        logger.info(f"Target variable balance ratio: {balance_ratio:.2f}")
        logger.info(f"Majority class: {target_counts.index[0]} ({target_percentages.iloc[0]:.1f}%)")
        logger.info(f"Minority class: {target_counts.index[-1]} ({target_percentages.iloc[-1]:.1f}%)")
    
    def plot_correlation_matrix(
        self,
        df: pd.DataFrame,
        numeric_cols: Optional[List[str]] = None,
        filename: str = "06_correlation_matrix"
    ):
        """
        Generate correlation matrix heatmap
        
        Args:
            df: Input DataFrame
            numeric_cols: List of numeric columns (auto-detect if None)
            filename: Name for the output file
        """
        logger.info("Generating correlation matrix...")
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            logger.warning("Need at least 2 numeric columns for correlation")
            return
        
        correlation_matrix = df[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        # Heatmap
        sns.heatmap(
            correlation_matrix,
            mask=mask,
            annot=True,
            cmap='RdYlBu_r',
            center=0,
            square=True,
            linewidths=1,
            fmt='.2f',
            cbar_kws={"shrink": .8},
            annot_kws={'fontsize': 10, 'fontweight': 'bold'}
        )
        
        plt.title(
            'Matriz de Correlación - Variables Numéricas',
            fontsize=16, fontweight='bold', pad=20
        )
        plt.tight_layout()
        self._save_figure(filename)
        
        # Log strong correlations
        logger.info("Strong correlations (|r| > 0.5):")
        for i in range(len(correlation_matrix.columns)):
            for j in range(i + 1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.5:
                    col1 = correlation_matrix.columns[i]
                    col2 = correlation_matrix.columns[j]
                    logger.info(f"  {col1} ↔ {col2}: {corr_val:.3f}")
    
    def generate_all_plots(self, df: pd.DataFrame):
        """
        Generate all EDA visualizations at once
        
        Args:
            df: Input DataFrame
        """
        logger.info("="*70)
        logger.info("GENERATING ALL EDA VISUALIZATIONS")
        logger.info("="*70)
        
        # 1. Dataset overview
        self.plot_dataset_overview(df)
        
        # 2. Numeric distributions
        self.plot_numeric_distributions(df)
        
        # 3. Numeric boxplots
        self.plot_numeric_boxplots(df)
        
        # 4. Categorical distributions
        self.plot_categorical_distributions(df)
        
        # 5. Target distribution
        if 'NObeyesdad' in df.columns:
            self.plot_target_distribution(df)
        
        # 6. Correlation matrix
        self.plot_correlation_matrix(df)
        
        logger.info("="*70)
        logger.info("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*70)


def generate_eda_visualizations(df: pd.DataFrame, output_dir: Optional[Path] = None):
    """
    Convenience function to generate all EDA visualizations
    
    Args:
        df: Input DataFrame
        output_dir: Directory to save figures (default: FIGURES_DIR from config)
    
    Returns:
        EDAVisualizer instance
    """
    visualizer = EDAVisualizer(output_dir=output_dir or FIGURES_DIR)
    visualizer.generate_all_plots(df)
    return visualizer
