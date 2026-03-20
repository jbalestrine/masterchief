"""
Diagram Generator - Visio-compatible diagrams

Generates diagrams in multiple formats:
- Mermaid (GitHub/Markdown native)
- Draw.io XML (Visio-compatible)
- Graphviz DOT (Standard graph language)
- PlantUML (UML diagrams)
- ASCII (Terminal/plain text)

Light runs on logic.
"""

from enum import Enum
from typing import List, Any


class DiagramType(Enum):
    """Supported diagram types."""
    MERMAID = "mermaid"
    DRAWIO = "drawio"
    GRAPHVIZ = "graphviz"
    PLANTUML = "plantuml"
    ASCII = "ascii"


class DiagramGenerator:
    """Generates diagrams in various formats."""
    
    def generate(
        self,
        diagram_type: DiagramType,
        components: List[Any],
        connections: List[Any],
        title: str = "System Architecture"
    ) -> str:
        """Generate diagram in specified format."""
        if diagram_type == DiagramType.MERMAID:
            return self._generate_mermaid(components, connections, title)
        elif diagram_type == DiagramType.DRAWIO:
            return self._generate_drawio(components, connections, title)
        elif diagram_type == DiagramType.GRAPHVIZ:
            return self._generate_graphviz(components, connections, title)
        elif diagram_type == DiagramType.PLANTUML:
            return self._generate_plantuml(components, connections, title)
        elif diagram_type == DiagramType.ASCII:
            return self._generate_ascii(components, connections, title)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    def _generate_mermaid(
        self,
        components: List[Any],
        connections: List[Any],
        title: str
    ) -> str:
        """Generate Mermaid diagram."""
        lines = [
            "```mermaid",
            "graph TD",
            f"    %% {title}",
            ""
        ]
        
        # Group components by layer
        layers = {}
        for comp in components:
            layer = comp.layer if hasattr(comp, 'layer') else comp.get('layer', 'application')
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(comp)
        
        # Add subgraphs for each layer
        for layer, comps in sorted(layers.items()):
            lines.append(f"    subgraph {layer.title()}")
            for comp in comps:
                comp_id = comp.id if hasattr(comp, 'id') else comp.get('id')
                comp_name = comp.name if hasattr(comp, 'name') else comp.get('name')
                tech = comp.technology if hasattr(comp, 'technology') else comp.get('technology', '')
                lines.append(f"        {comp_id}[{comp_name}<br/>{tech}]")
            lines.append("    end")
            lines.append("")
        
        # Add connections
        for conn in connections:
            source = conn.source if hasattr(conn, 'source') else conn.get('source')
            target = conn.target if hasattr(conn, 'target') else conn.get('target')
            protocol = conn.protocol if hasattr(conn, 'protocol') else conn.get('protocol')
            lines.append(f"    {source} -->|{protocol}| {target}")
        
        lines.append("```")
        
        return "\n".join(lines)
    
    def _generate_drawio(
        self,
        components: List[Any],
        connections: List[Any],
        title: str
    ) -> str:
        """Generate Draw.io XML diagram."""
        # Draw.io uses mxGraph XML format
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" version="22.0.0">',
            f'  <diagram name="{title}" id="diagram1">',
            '    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1">',
            '      <root>',
            '        <mxCell id="0"/>',
            '        <mxCell id="1" parent="0"/>',
        ]
        
        # Add components as rectangles
        y_pos = 100
        x_pos = 100
        cell_id = 2
        comp_cells = {}
        
        for comp in components:
            comp_id = comp.id if hasattr(comp, 'id') else comp.get('id')
            comp_name = comp.name if hasattr(comp, 'name') else comp.get('name')
            tech = comp.technology if hasattr(comp, 'technology') else comp.get('technology', '')
            
            label = f"{comp_name}\\n{tech}"
            lines.append(
                f'        <mxCell id="{cell_id}" value="{label}" '
                f'style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" '
                f'vertex="1" parent="1">'
            )
            lines.append(
                f'          <mxGeometry x="{x_pos}" y="{y_pos}" width="120" height="60" as="geometry"/>'
            )
            lines.append('        </mxCell>')
            
            comp_cells[comp_id] = cell_id
            cell_id += 1
            x_pos += 200
            if x_pos > 600:
                x_pos = 100
                y_pos += 150
        
        # Add connections as edges
        for conn in connections:
            source = conn.source if hasattr(conn, 'source') else conn.get('source')
            target = conn.target if hasattr(conn, 'target') else conn.get('target')
            protocol = conn.protocol if hasattr(conn, 'protocol') else conn.get('protocol')
            
            if source in comp_cells and target in comp_cells:
                lines.append(
                    f'        <mxCell id="{cell_id}" value="{protocol}" '
                    f'style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" '
                    f'edge="1" parent="1" source="{comp_cells[source]}" target="{comp_cells[target]}">'
                )
                lines.append('          <mxGeometry relative="1" as="geometry"/>')
                lines.append('        </mxCell>')
                cell_id += 1
        
        lines.extend([
            '      </root>',
            '    </mxGraphModel>',
            '  </diagram>',
            '</mxfile>'
        ])
        
        return "\n".join(lines)
    
    def _generate_graphviz(
        self,
        components: List[Any],
        connections: List[Any],
        title: str
    ) -> str:
        """Generate Graphviz DOT diagram."""
        lines = [
            'digraph SystemArchitecture {',
            f'    label="{title}";',
            '    rankdir=TB;',
            '    node [shape=box, style=rounded];',
            ''
        ]
        
        # Group by layer for subgraphs
        layers = {}
        for comp in components:
            layer = comp.layer if hasattr(comp, 'layer') else comp.get('layer', 'application')
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(comp)
        
        # Add subgraphs for layers
        for i, (layer, comps) in enumerate(sorted(layers.items())):
            lines.append(f'    subgraph cluster_{i} {{')
            lines.append(f'        label="{layer.title()}";')
            lines.append('        style=filled;')
            lines.append('        color=lightgrey;')
            
            for comp in comps:
                comp_id = comp.id if hasattr(comp, 'id') else comp.get('id')
                comp_name = comp.name if hasattr(comp, 'name') else comp.get('name')
                tech = comp.technology if hasattr(comp, 'technology') else comp.get('technology', '')
                lines.append(f'        {comp_id} [label="{comp_name}\\n{tech}"];')
            
            lines.append('    }')
            lines.append('')
        
        # Add connections
        for conn in connections:
            source = conn.source if hasattr(conn, 'source') else conn.get('source')
            target = conn.target if hasattr(conn, 'target') else conn.get('target')
            protocol = conn.protocol if hasattr(conn, 'protocol') else conn.get('protocol')
            lines.append(f'    {source} -> {target} [label="{protocol}"];')
        
        lines.append('}')
        
        return "\n".join(lines)
    
    def _generate_plantuml(
        self,
        components: List[Any],
        connections: List[Any],
        title: str
    ) -> str:
        """Generate PlantUML diagram."""
        lines = [
            '@startuml',
            f'title {title}',
            '',
            '!define RECTANGLE class',
            ''
        ]
        
        # Add components
        for comp in components:
            comp_id = comp.id if hasattr(comp, 'id') else comp.get('id')
            comp_name = comp.name if hasattr(comp, 'name') else comp.get('name')
            tech = comp.technology if hasattr(comp, 'technology') else comp.get('technology', '')
            layer = comp.layer if hasattr(comp, 'layer') else comp.get('layer', 'application')
            
            lines.append(f'component "{comp_name}\\n{tech}" as {comp_id} <<{layer}>>')
        
        lines.append('')
        
        # Add connections
        for conn in connections:
            source = conn.source if hasattr(conn, 'source') else conn.get('source')
            target = conn.target if hasattr(conn, 'target') else conn.get('target')
            protocol = conn.protocol if hasattr(conn, 'protocol') else conn.get('protocol')
            lines.append(f'{source} --> {target} : {protocol}')
        
        lines.append('')
        lines.append('@enduml')
        
        return "\n".join(lines)
    
    def _generate_ascii(
        self,
        components: List[Any],
        connections: List[Any],
        title: str
    ) -> str:
        """Generate ASCII art diagram."""
        lines = [
            "=" * 60,
            title.center(60),
            "=" * 60,
            ""
        ]
        
        # Group by layer
        layers = {}
        for comp in components:
            layer = comp.layer if hasattr(comp, 'layer') else comp.get('layer', 'application')
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(comp)
        
        # Draw layers top to bottom
        for layer, comps in sorted(layers.items()):
            lines.append(f"[ {layer.upper()} LAYER ]".center(60))
            lines.append("-" * 60)
            
            for comp in comps:
                comp_name = comp.name if hasattr(comp, 'name') else comp.get('name')
                tech = comp.technology if hasattr(comp, 'technology') else comp.get('technology', '')
                lines.append(f"  +------------------+")
                lines.append(f"  | {comp_name:^16} |")
                lines.append(f"  | {tech:^16} |")
                lines.append(f"  +------------------+")
                lines.append("        |")
                lines.append("        v")
            
            lines.append("")
        
        # Add connection list
        lines.append("")
        lines.append("CONNECTIONS:".center(60))
        lines.append("-" * 60)
        
        for conn in connections:
            source = conn.source if hasattr(conn, 'source') else conn.get('source')
            target = conn.target if hasattr(conn, 'target') else conn.get('target')
            protocol = conn.protocol if hasattr(conn, 'protocol') else conn.get('protocol')
            lines.append(f"  {source} --[{protocol}]--> {target}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


__all__ = ['DiagramGenerator', 'DiagramType']
