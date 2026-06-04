"""Explanations, kept honest.

Attention weights are not treated as explanations (Jain & Wallace, 2019). Instead:

    - an interpretable-by-design model on human-readable features (recent trend,
      variability, time since last insulin) where the explanation is the model
    - post-hoc attribution (Integrated Gradients / SHAP) on the deep models, always
      paired with a faithfulness check so a wrong explanation is caught, not trusted

Each alert ships with a short, checkable "what drove this".
"""
