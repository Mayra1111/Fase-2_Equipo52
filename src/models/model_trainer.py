"""
Model training module for the Obesity ML Project
Implements training for multiple classifiers with MLflow tracking
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
import mlflow
import mlflow.sklearn

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """
    Class to train and evaluate multiple ML models
    """
    
    def __init__(
        self,
        preprocessor,
        target_names: list,
        random_state: int = 42
    ):
        """
        Initialize ModelTrainer
        
        Args:
            preprocessor: Fitted preprocessor (ColumnTransformer)
            target_names: List of target class names
            random_state: Random seed for reproducibility
        """
        self.preprocessor = preprocessor
        self.target_names = target_names
        self.random_state = random_state
        self.models = {}
        self.predictions = {}
        self.metrics = {}
        
        logger.info("ModelTrainer initialized")
    
    def train_random_forest(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        n_estimators: int = 200,
        max_depth: int = 10,
        class_weight: str = 'balanced'
    ) -> Tuple[Any, np.ndarray]:
        """
        Train RandomForest classifier
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            class_weight: Class weight strategy
            
        Returns:
            Trained pipeline and predictions
        """
        logger.info("Training RandomForest classifier...")
        
        from sklearn.pipeline import Pipeline
        
        rf_pipe = Pipeline([
            ('pre', self.preprocessor),
            ('clf', RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=self.random_state,
                class_weight=class_weight
            ))
        ])
        
        with mlflow.start_run(run_name="RandomForest_Baseline"):
            mlflow.log_param("model_type", "RandomForest")
            mlflow.log_params(rf_pipe.named_steps['clf'].get_params())
            mlflow.log_param("smote_applied", False)
            
            rf_pipe.fit(X_train, y_train)
            pred_rf = rf_pipe.predict(X_test)
            
            # Log metrics
            metrics = self._calculate_metrics(y_test, pred_rf, "rf")
            self._log_metrics(metrics, y_train, y_test, rf_pipe, X_train, X_test)
            
            # Log model
            mlflow.sklearn.log_model(
                rf_pipe,
                "random_forest_model",
                signature=mlflow.models.infer_signature(X_test, pred_rf)
            )
            
            logger.info(f"RandomForest - Accuracy: {metrics['test_accuracy']:.4f}")
            print(classification_report(y_test, pred_rf, target_names=self.target_names))
        
        self.models['RandomForest'] = rf_pipe
        self.predictions['RandomForest'] = pred_rf
        self.metrics['RandomForest'] = metrics
        
        return rf_pipe, pred_rf
    
    def train_xgboost_smote(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        param_dist: Optional[Dict] = None,
        n_iter: int = 20,
        cv_splits: int = 5
    ) -> Tuple[Any, np.ndarray]:
        """
        Train XGBoost with SMOTE and hyperparameter tuning
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            param_dist: Parameter distribution for RandomizedSearchCV
            n_iter: Number of iterations for random search
            cv_splits: Number of cross-validation splits
            
        Returns:
            Best pipeline and predictions
        """
        logger.info("Training XGBoost with SMOTE and hyperparameter tuning...")
        
        if param_dist is None:
            param_dist = {
                'clf__n_estimators': [100, 200, 400],
                'clf__max_depth': [3, 5, 7],
                'clf__learning_rate': [0.01, 0.05, 0.1],
                'clf__subsample': [0.6, 0.8, 1.0],
                'clf__colsample_bytree': [0.6, 0.8, 1.0],
                'smote__k_neighbors': [1]
            }
        
        xgb_pipe = ImbPipeline([
            ('pre', self.preprocessor),
            ('smote', SMOTE(random_state=self.random_state)),
            ('clf', XGBClassifier(
                objective='multi:softprob',
                eval_metric='mlogloss',
                random_state=self.random_state
            ))
        ])
        
        cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=self.random_state)
        
        search = RandomizedSearchCV(
            xgb_pipe,
            param_dist,
            n_iter=n_iter,
            scoring='accuracy',
            n_jobs=-1,
            cv=cv,
            random_state=self.random_state,
            verbose=2
        )
        
        search.fit(X_train, y_train)
        best_xgb = search.best_estimator_
        pred_xgb = best_xgb.predict(X_test)
        
        logger.info(f"Best params: {search.best_params_}")
        
        with mlflow.start_run(run_name="XGBoost_SMOTE_Tuning"):
            mlflow.log_param("model_type", "XGBoost_SMOTE")
            mlflow.log_params(search.best_params_)
            
            # Log metrics
            metrics = self._calculate_metrics(y_test, pred_xgb, "xgb_smote")
            self._log_metrics(metrics, y_train, y_test, best_xgb, X_train, X_test)
            
            # Log model
            mlflow.sklearn.log_model(
                best_xgb,
                "xgboost_smote_model",
                signature=mlflow.models.infer_signature(X_test, pred_xgb)
            )
            
            logger.info(f"XGBoost (SMOTE) - Accuracy: {metrics['test_accuracy']:.4f}")
            print(classification_report(y_test, pred_xgb, target_names=self.target_names))
        
        self.models['XGBoost_SMOTE'] = best_xgb
        self.predictions['XGBoost_SMOTE'] = pred_xgb
        self.metrics['XGBoost_SMOTE'] = metrics
        
        return best_xgb, pred_xgb
    
    def train_xgboost_simple(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        n_estimators: int = 200,
        max_depth: int = 5,
        learning_rate: float = 0.1
    ) -> Tuple[Any, np.ndarray]:
        """
        Train simple XGBoost without SMOTE
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            n_estimators: Number of trees
            max_depth: Maximum depth
            learning_rate: Learning rate
            
        Returns:
            Trained pipeline and predictions
        """
        logger.info("Training XGBoost (simple, no SMOTE)...")
        
        from sklearn.pipeline import Pipeline
        
        xgb_simple_pipe = Pipeline([
            ('pre', self.preprocessor),
            ('clf', XGBClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                objective='multi:softprob',
                eval_metric='mlogloss',
                random_state=self.random_state
            ))
        ])
        
        with mlflow.start_run(run_name="XGBoost_Simple"):
            mlflow.log_param("model_type", "XGBoost_Simple")
            mlflow.log_params(xgb_simple_pipe.named_steps['clf'].get_params())
            mlflow.log_param("smote_applied", False)
            
            xgb_simple_pipe.fit(X_train, y_train)
            pred_xgb_simple = xgb_simple_pipe.predict(X_test)
            
            # Log metrics
            metrics = self._calculate_metrics(y_test, pred_xgb_simple, "xgb_simple")
            self._log_metrics(metrics, y_train, y_test, xgb_simple_pipe, X_train, X_test)
            
            # Log model
            mlflow.sklearn.log_model(
                xgb_simple_pipe,
                "xgboost_simple_model",
                signature=mlflow.models.infer_signature(X_test, pred_xgb_simple)
            )
            
            logger.info(f"XGBoost (Simple) - Accuracy: {metrics['test_accuracy']:.4f}")
            print(classification_report(y_test, pred_xgb_simple, target_names=self.target_names))
        
        self.models['XGBoost_Simple'] = xgb_simple_pipe
        self.predictions['XGBoost_Simple'] = pred_xgb_simple
        self.metrics['XGBoost_Simple'] = metrics
        
        return xgb_simple_pipe, pred_xgb_simple
    
    def train_knn(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        n_neighbors: int = 5
    ) -> Tuple[Any, np.ndarray]:
        """
        Train K-Nearest Neighbors classifier
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            n_neighbors: Number of neighbors
            
        Returns:
            Trained pipeline and predictions
        """
        logger.info("Training KNN classifier...")
        
        from sklearn.pipeline import Pipeline
        
        knn_pipe = Pipeline([
            ('pre', self.preprocessor),
            ('clf', KNeighborsClassifier(n_neighbors=n_neighbors))
        ])
        
        with mlflow.start_run(run_name="KNN"):
            mlflow.log_param("model_type", "KNN")
            mlflow.log_params(knn_pipe.named_steps['clf'].get_params())
            mlflow.log_param("smote_applied", False)
            
            knn_pipe.fit(X_train, y_train)
            pred_knn = knn_pipe.predict(X_test)
            
            # Log metrics
            metrics = self._calculate_metrics(y_test, pred_knn, "knn")
            self._log_metrics(metrics, y_train, y_test, knn_pipe, X_train, X_test)
            
            # Log model
            mlflow.sklearn.log_model(
                knn_pipe,
                "knn_model",
                signature=mlflow.models.infer_signature(X_test, pred_knn)
            )
            
            logger.info(f"KNN - Accuracy: {metrics['test_accuracy']:.4f}")
            print(classification_report(y_test, pred_knn, target_names=self.target_names))
        
        self.models['KNN'] = knn_pipe
        self.predictions['KNN'] = pred_knn
        self.metrics['KNN'] = metrics
        
        return knn_pipe, pred_knn
    
    def train_svm(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        kernel: str = 'linear',
        C: float = 1.0
    ) -> Tuple[Any, np.ndarray]:
        """
        Train Support Vector Machine classifier
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            kernel: Kernel type
            C: Regularization parameter
            
        Returns:
            Trained pipeline and predictions
        """
        logger.info("Training SVM classifier...")
        
        from sklearn.pipeline import Pipeline
        
        svm_pipe = Pipeline([
            ('pre', self.preprocessor),
            ('clf', SVC(kernel=kernel, C=C, random_state=self.random_state))
        ])
        
        with mlflow.start_run(run_name="SVM_Linear"):
            mlflow.log_param("model_type", "SVM_Linear")
            mlflow.log_params(svm_pipe.named_steps['clf'].get_params())
            mlflow.log_param("smote_applied", False)
            
            svm_pipe.fit(X_train, y_train)
            pred_svm = svm_pipe.predict(X_test)
            
            # Log metrics
            metrics = self._calculate_metrics(y_test, pred_svm, "svm")
            self._log_metrics(metrics, y_train, y_test, svm_pipe, X_train, X_test)
            
            # Log model
            mlflow.sklearn.log_model(
                svm_pipe,
                "svm_model",
                signature=mlflow.models.infer_signature(X_test, pred_svm)
            )
            
            logger.info(f"SVM - Accuracy: {metrics['test_accuracy']:.4f}")
            print(classification_report(y_test, pred_svm, target_names=self.target_names))
        
        self.models['SVM_Linear'] = svm_pipe
        self.predictions['SVM_Linear'] = pred_svm
        self.metrics['SVM_Linear'] = metrics
        
        return svm_pipe, pred_svm
    
    def _calculate_metrics(
        self,
        y_test: pd.Series,
        y_pred: np.ndarray,
        prefix: str
    ) -> Dict[str, float]:
        """
        Calculate all metrics for a model
        
        Args:
            y_test: True labels
            y_pred: Predicted labels
            prefix: Metric prefix
            
        Returns:
            Dictionary with all metrics
        """
        report = classification_report(
            y_test,
            y_pred,
            target_names=self.target_names,
            output_dict=True
        )
        
        return {
            'test_accuracy': accuracy_score(y_test, y_pred),
            f'{prefix}_precision_weighted': report['weighted avg']['precision'],
            f'{prefix}_recall_weighted': report['weighted avg']['recall'],
            f'{prefix}_f1_weighted': report['weighted avg']['f1-score']
        }
    
    def _log_metrics(
        self,
        metrics: Dict[str, float],
        y_train: pd.Series,
        y_test: pd.Series,
        model,
        X_train: pd.DataFrame,
        X_test: pd.DataFrame
    ):
        """
        Log all metrics to MLflow
        
        Args:
            metrics: Dictionary with metrics
            y_train: Training labels
            y_test: Test labels
            model: Trained model
            X_train: Training features
            X_test: Test features
        """
        # Log test metrics
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
        
        # Log overfitting/underfitting metrics
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        gap = train_score - test_score
        
        mlflow.log_metric("train_score", train_score)
        mlflow.log_metric("test_score_ov_uf", test_score)
        mlflow.log_metric("gap_overfitting", gap)
    
    def get_best_model(self) -> Tuple[str, Any, float]:
        """
        Get the best model based on accuracy
        
        Returns:
            Model name, model object, and accuracy
        """
        best_name = max(
            self.metrics.keys(),
            key=lambda x: self.metrics[x]['test_accuracy']
        )
        best_model = self.models[best_name]
        best_acc = self.metrics[best_name]['test_accuracy']
        
        logger.info(f"Best model: {best_name} with accuracy: {best_acc:.4f}")
        
        return best_name, best_model, best_acc
    
    def get_metrics_dataframe(self) -> pd.DataFrame:
        """
        Get comparison dataframe of all models
        
        Returns:
            DataFrame with metrics comparison
        """
        data = []
        for name, pred in self.predictions.items():
            # Get y_test from the first prediction (all use same test set)
            # This is a simplification - in production, store y_test as instance variable
            data.append({
                'Modelo': name,
                'Accuracy': self.metrics[name]['test_accuracy']
            })
        
        return pd.DataFrame(data)
