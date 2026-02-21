"""
Dynamic Feature Management System for MasterChief Platform

This module provides a dynamic feature loading and management system that allows
users to add, configure, and toggle features through a web interface.
"""

import os
import json
import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, render_template_string
import threading
import time
import subprocess
import requests
import zipfile
import io
import shutil


@dataclass
class FeatureConfig:
    """Configuration for a feature"""
    name: str
    display_name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = False
    dependencies: List[str] = None
    settings: Dict[str, Any] = None
    routes: List[Dict[str, Any]] = None
    scripts: List[str] = None
    ui_components: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.settings is None:
            self.settings = {}
        if self.routes is None:
            self.routes = []
        if self.scripts is None:
            self.scripts = []
        if self.ui_components is None:
            self.ui_components = []


class FeatureManager:
    """Manages dynamic features for the MasterChief platform"""

    def __init__(self, app: Flask, features_dir: str = "features"):
        print("FeatureManager.__init__ called")
        self.app = app
        self.features_dir = Path(__file__).parent / features_dir
        self.features_dir.mkdir(exist_ok=True)
        self.features: Dict[str, "FeatureHandler"] = {}
        self.feature_configs: Dict[str, FeatureConfig] = {}
        self._lock = threading.Lock()

        # Create subdirectories
        (self.features_dir / "configs").mkdir(exist_ok=True)
        (self.features_dir / "handlers").mkdir(exist_ok=True)
        (self.features_dir / "templates").mkdir(exist_ok=True)
        (self.features_dir / "static").mkdir(exist_ok=True)

        # Load existing features
        self._load_feature_configs()
        self._register_routes()

    def _register_routes(self):
        """Register feature management routes"""
        print("Registering feature routes...")

        @self.app.route("/api/features")
        def api_features():
            """Get all features"""
            return jsonify({
                "features": [asdict(handler.config) for handler in self.features.values()],
                "available": list(self.feature_configs.keys())
            })

        @self.app.route("/api/features/<feature_name>", methods=["GET"])
        def api_feature_detail(feature_name):
            """Get feature details"""
            if feature_name not in self.features and feature_name not in self.feature_configs:
                return jsonify({"error": "Feature not found"}), 404

            config = None
            if feature_name in self.features:
                config = self.features[feature_name].config
            else:
                config = self.feature_configs[feature_name]

            return jsonify(asdict(config))

        @self.app.route("/api/features/<feature_name>/toggle", methods=["POST"])
        def api_feature_toggle(feature_name):
            """Toggle feature on/off"""
            data = request.get_json() or {}
            enabled = data.get("enabled", False)

            try:
                if enabled:
                    self.enable_feature(feature_name)
                else:
                    self.disable_feature(feature_name)
                return jsonify({"success": True, "enabled": enabled})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def _load_feature_configs(self):
        """Load feature configurations from disk"""
        configs_dir = self.features_dir / "configs"
        for config_file in configs_dir.glob("*.json"):
            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)
                    config = FeatureConfig(**config_data)
                    self.feature_configs[config.name] = config
            except Exception as e:
                print(f"Error loading feature config {config_file}: {e}")

    def enable_feature(self, feature_name: str):
        """Enable a feature"""
        if feature_name not in self.feature_configs:
            raise ValueError(f"Feature {feature_name} not found")

        config = self.feature_configs[feature_name]
        if feature_name not in self.features:
            # Create feature handler
            handler = FeatureHandler(config, self.features_dir)
            self.features[feature_name] = handler

        config.enabled = True
        self._save_feature_config(config)

    def disable_feature(self, feature_name: str):
        """Disable a feature"""
        if feature_name in self.features:
            # Clean up feature
            del self.features[feature_name]

        if feature_name in self.feature_configs:
            config = self.feature_configs[feature_name]
            config.enabled = False
            self._save_feature_config(config)

    def _save_feature_config(self, config: FeatureConfig):
        """Save feature configuration to disk"""
        configs_dir = self.features_dir / "configs"
        config_file = configs_dir / f"{config.name}.json"
        with open(config_file, "w") as f:
            json.dump(asdict(config), f, indent=2)


class FeatureHandler:
    """Handles a loaded feature"""

    def __init__(self, config: FeatureConfig, features_dir: Path):
        self.config = config
        self.features_dir = features_dir
        self.instance = None

        # Load the feature if enabled
        if config.enabled:
            self._load_feature()

    def _load_feature(self):
        """Load the feature implementation"""
        # This is a placeholder - actual implementation would load Python modules
        pass


# Global feature manager instance
_feature_manager = None


def init_feature_manager(app: Flask) -> FeatureManager:
    """Initialize the global feature manager"""
    print("Initializing feature manager...")
    global _feature_manager
    _feature_manager = FeatureManager(app)
    return _feature_manager


def get_feature_manager() -> Optional[FeatureManager]:
    """Get the global feature manager instance"""
    return _feature_manager
