import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from transformers import (
    SwinForImageClassification, 
    Swinv2ForImageClassification, 
    ConvNextForImageClassification, 
    ResNetForImageClassification, 
    DeiTForImageClassification,
    ViTForImageClassification,
)
import timm  # for additional model support
import torchvision.models as models  # for torchvision resnet models

class DualInputModel(nn.Module):
    def __init__(self, model_name="microsoft/swin-tiny-patch4-window7-224", model_type="swin", 
                 num_classes=2, dropout_rate=0.3, fusion_type="concat", num_inputs=None):
        """
        Dual-input model that supports multiple fusion methods and variable number of inputs.
        
        Parameters:
        - model_name: str, pre-trained model name.
        - model_type: str, type of backbone model ("swin", "swinv2", "convnext", "resnet", "deit", "vit").
        - num_classes: int, number of output classes.
        - dropout_rate: float, dropout probability.
        - fusion_type: str, fusion method ("concat", "weighted_sum", "diff_mul", "self_attention", "gated", "cross_attention").
        - num_inputs: int or None, expected number of inputs for fusion methods that need a fixed number.
                    For fusion types that can handle variable numbers (e.g. weighted_sum, self_attention),
                    this can be left as None.
        """
        super(DualInputModel, self).__init__()
        self.fusion_type = fusion_type
        self.num_inputs = num_inputs

        # --- Load Pretrained Backbone ---
        if model_type == "swin":
            self.backbone = SwinForImageClassification.from_pretrained(model_name)
        elif model_type == "swinv2":
            self.backbone = Swinv2ForImageClassification.from_pretrained(model_name)
        elif model_type == "convnext":
            self.backbone = ConvNextForImageClassification.from_pretrained(model_name)
        elif model_type == "resnet":
            # First try: if model name contains "microsoft", use the transformer variant
            if "microsoft" in model_name:
                self.backbone = ResNetForImageClassification.from_pretrained(model_name)
            # Second: if model name starts with "resnet", load from torchvision models
            elif model_name.startswith("resnet"):
                self.backbone = models.__dict__[model_name](pretrained=True)
                # Remove the default classification head
                self.backbone.fc = nn.Identity()
            else:
                # Fall back to timm for other resnet variants
                self.backbone = timm.create_model(model_name, pretrained=True)
        elif model_type == "deit":
            self.backbone = DeiTForImageClassification.from_pretrained(model_name)
        elif model_type == "vit":
            self.backbone = ViTForImageClassification.from_pretrained(model_name)
        else:
            raise ValueError("Invalid model type. Choose between 'swin', 'swinv2', 'convnext', 'resnet', 'deit', 'vit'.")

        # --- Determine input feature dimension ---
        if hasattr(self.backbone, "classifier") and hasattr(self.backbone.classifier, "in_features"):
            in_features = self.backbone.classifier.in_features
        elif hasattr(self.backbone, "fc"):  # e.g. ResNet from torchvision
            in_features = self.backbone.fc.in_features if hasattr(self.backbone.fc, "in_features") else in_features
        elif hasattr(self.backbone, "head") and hasattr(self.backbone.head, "in_features"):
            in_features = self.backbone.head.in_features
        else:
            # If unable to determine, require user to provide the expected dimension.
            raise ValueError(f"Unexpected model structure for {model_type}.")

        # Remove the default classifier head so we can fuse features
        if hasattr(self.backbone, "classifier"):
            self.backbone.classifier = nn.Identity()
        elif hasattr(self.backbone, "fc"):
            self.backbone.fc = nn.Identity()
        elif hasattr(self.backbone, "head"):
            self.backbone.head = nn.Identity()

        # --- Define Fusion Layers ---
        if fusion_type == "concat":
            # This fusion concatenates features from each input.
            # It requires num_inputs to be specified.
            if num_inputs is None:
                raise ValueError("For 'concat' fusion, 'num_inputs' must be provided.")
            self.interaction_layer = nn.Sequential(
                nn.Linear(in_features * num_inputs, in_features),
                nn.ReLU(),
                nn.Linear(in_features, num_classes)
            )
        elif fusion_type == "weighted_sum":
            # If num_inputs is known, use a learnable weight per input.
            # Otherwise, we fall back on equal weighting.
            if num_inputs is not None:
                self.alpha = nn.Parameter(torch.ones(num_inputs) / num_inputs)
        elif fusion_type == "diff_mul":
            # For diff_mul, we assume exactly 2 inputs.
            if num_inputs is None or num_inputs != 2:
                raise ValueError("For 'diff_mul' fusion, exactly 2 inputs are required (set num_inputs=2).")
            self.interaction_layer = nn.Sequential(
                nn.Linear(in_features * 2, in_features),
                nn.ReLU(),
                nn.Linear(in_features, num_classes)
            )
        elif fusion_type == "self_attention":
            # Self-attention layer can handle variable sequence lengths.
            self.attention_layer = nn.MultiheadAttention(embed_dim=in_features, num_heads=4)
            self.classifier = nn.Linear(in_features, num_classes)
        elif fusion_type == "gated":
            # For gated fusion, we assume exactly 2 inputs.
            if num_inputs is None or num_inputs != 2:
                raise ValueError("For 'gated' fusion, exactly 2 inputs are required (set num_inputs=2).")
            # Here we use a simple linear layer to generate a scalar gate value for each input.
            self.gate = nn.Linear(in_features, 1)
            self.interaction_layer = nn.Linear(in_features, num_classes)
        elif fusion_type == "cross_attention":
            self.cross_attention = nn.MultiheadAttention(embed_dim=in_features, num_heads=4)
            self.classifier = nn.Linear(in_features, num_classes)
        else:
            raise ValueError("Invalid fusion type. Choose one of: 'concat', 'weighted_sum', 'diff_mul', 'self_attention', 'gated', 'cross_attention'.")

    def forward(self, *inputs):
        """
        Forward pass that accepts a variable number of inputs.
        
        Each input is processed individually through the backbone.
        Fusion is then applied depending on the selected fusion type.
        """
        if len(inputs) == 0:
            raise ValueError("At least one input is required.")

        # Process each input through the backbone
        features = []
        for x in inputs:
            out = self.backbone(x)
            # Some models return an object with a 'logits' attribute.
            feat = out.logits if hasattr(out, 'logits') else out
            features.append(feat)

        if self.fusion_type == "concat":
            if self.num_inputs is None or len(features) != self.num_inputs:
                raise ValueError(f"'concat' fusion expects {self.num_inputs} inputs; got {len(features)}")
            # Concatenate features along the feature dimension
            combined_feat = torch.cat(features, dim=1)
            logits = self.interaction_layer(combined_feat)

        elif self.fusion_type == "weighted_sum":
            # Stack features: shape [num_inputs, batch, feature_dim]
            stacked = torch.stack(features, dim=0)
            if hasattr(self, "alpha"):
                if len(features) != self.alpha.shape[0]:
                    raise ValueError(f"'weighted_sum' fusion expects {self.alpha.shape[0]} inputs; got {len(features)}")
                # Use learnable weights
                weights = self.alpha.view(-1, 1, 1)
                weighted = weights * stacked
                logits = torch.sum(weighted, dim=0)
            else:
                # If no learnable weights, use equal weights (i.e. simple average)
                logits = torch.mean(stacked, dim=0)

        elif self.fusion_type == "diff_mul":
            # Assumes exactly 2 inputs
            if len(features) != 2:
                raise ValueError("'diff_mul' fusion requires exactly 2 inputs.")
            diff_feat = torch.abs(features[0] - features[1])
            mul_feat = features[0] * features[1]
            combined_feat = torch.cat([diff_feat, mul_feat], dim=1)
            logits = self.interaction_layer(combined_feat)

        elif self.fusion_type == "self_attention":
            # Stack features and treat each as a token: shape [num_inputs, batch, feature_dim]
            stacked = torch.stack(features, dim=0)
            # Apply multihead self-attention
            attn_output, _ = self.attention_layer(stacked, stacked, stacked)
            # Pool the attended tokens (here we simply average them)
            pooled = torch.mean(attn_output, dim=0)
            logits = self.classifier(pooled)

        elif self.fusion_type == "gated":
            # Assumes exactly 2 inputs.
            if len(features) != 2:
                raise ValueError("'gated' fusion requires exactly 2 inputs.")
            # Compute gate scores for each input feature separately.
            # Here we apply the same gate module to both features.
            gate1 = torch.sigmoid(self.gate(features[0]))
            gate2 = torch.sigmoid(self.gate(features[1]))
            # Normalize the gate scores so that they sum to 1.
            gates = torch.cat([gate1, gate2], dim=1)
            norm_gates = torch.softmax(gates, dim=1)
            # Compute weighted sum of features
            combined_feat = norm_gates[:, 0:1] * features[0] + norm_gates[:, 1:2] * features[1]
            logits = self.interaction_layer(combined_feat)

        elif self.fusion_type == "cross_attention":
            # Stack features as tokens.
            stacked = torch.stack(features, dim=0)
            cross_feat, _ = self.cross_attention(stacked, stacked, stacked)
            pooled = torch.mean(cross_feat, dim=0)
            logits = self.classifier(pooled)

        else:
            raise ValueError("Invalid fusion type in forward pass.")

        return logits
