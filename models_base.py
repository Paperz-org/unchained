from django.db import models
from typing import List, Type

class MainAppModelMeta(models.base.ModelBase):
    """Metaclass that automatically sets app_label to '_unchained_main_app' for all models"""
    # Class variable to track all models created with this metaclass
    models_registry: List[Type] = []
    
    def __new__(mcs, name, bases, attrs):
        # Set app_label in Meta if not already set
        if 'Meta' not in attrs:
            attrs['Meta'] = type('Meta', (), {'app_label': '_unchained_main_app'})
        elif not hasattr(attrs['Meta'], 'app_label'):
            setattr(attrs['Meta'], 'app_label', '_unchained_main_app')
        
        # Create the model class
        model_class = super().__new__(mcs, name, bases, attrs)
        
        # Don't register abstract models
        is_abstract = getattr(model_class._meta, 'abstract', False)
        if not is_abstract:
            # Add to registry
            mcs.models_registry.append(model_class)
            print(f"Registered model {model_class.__name__} in MainAppModelMeta.models_registry")
        
        return model_class

class MainModel(models.Model, metaclass=MainAppModelMeta):
    """
    Base model class that automatically sets app_label to '_unchained_main_app'
    All models should inherit from this class instead of models.Model
    """
    class Meta:
        abstract = True  # This ensures this base class won't create its own table 