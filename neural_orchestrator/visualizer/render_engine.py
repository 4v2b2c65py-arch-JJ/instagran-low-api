"""
Visualizer Engine - Render Process
Renders visualizations using N=found value with model mapping and key points.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import json


class VisualizerEngine:
    """
    Visualizer engine for rendering neural network patterns and flows.
    Uses N=found value to build model maps based on key points.
    """
    
    def __init__(self, n_value: float = 1.0, render_resolution: Tuple[int, int] = (800, 600)):
        """
        Initialize the Visualizer Engine.
        
        Args:
            n_value: N=found value for model mapping
            render_resolution: Render resolution (width, height)
        """
        self.n_value = n_value
        self.render_resolution = render_resolution
        
        # Render state
        self.frame_buffer: List[Dict] = []
        self.model_map: Dict[str, any] = {}
        self.key_points: List[Tuple[float, float, float]] = []
        
        # Visualization settings
        self.colormap = 'viridis'
        self.interpolation = 'bilinear'
        
    def set_n_value(self, n_value: float):
        """
        Set N=found value for model mapping.
        
        Args:
            n_value: N value to set
        """
        self.n_value = n_value
    
    def build_model_map(self, density_markers: Dict[str, float], pattern_flow: Dict):
        """
        Build model map based on key points and density markers.
        
        Args:
            density_markers: Dictionary of density markers
            pattern_flow: Pattern flow data
        """
        self.model_map = {
            'n_value': self.n_value,
            'density_markers': density_markers,
            'pattern_flow': pattern_flow,
            'key_points': self.key_points,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate key points from density markers
        self.key_points = self._generate_key_points(density_markers)
    
    def _generate_key_points(self, density_markers: Dict[str, float]) -> List[Tuple[float, float, float]]:
        """
        Generate key points from density markers.
        
        Args:
            density_markers: Dictionary of density markers
            
        Returns:
            List of (x, y, z) key point tuples
        """
        points = []
        
        # Extract density values
        alpha_density = density_markers.get('alpha_density', 0.5)
        beta_density = density_markers.get('beta_density', 0.5)
        frequency_density = density_markers.get('frequency_density', 1.0)
        temporal_density = density_markers.get('temporal_density', 0.5)
        spatial_density = density_markers.get('spatial_density', 0.5)
        
        # Generate 3D key points
        num_points = int(self.n_value * 10)  # Scale by N value
        num_points = min(max(num_points, 5), 50)  # Clamp between 5 and 50
        
        for i in range(num_points):
            angle = (2 * np.pi * i) / num_points
            radius = alpha_density * beta_density
            
            x = radius * np.cos(angle) * frequency_density
            y = radius * np.sin(angle) * temporal_density
            z = spatial_density * np.sin(angle * 2)
            
            points.append((x, y, z))
        
        return points
    
    def render_frame(self, render_data: Dict[str, any]) -> Dict[str, any]:
        """
        Render a single frame of visualization.
        
        Args:
            render_data: Data to render
            
        Returns:
            Dictionary containing render information
        """
        # Update model map
        density_markers = render_data.get('density_markers', {})
        pattern_flow = render_data.get('pattern_flow', {})
        self.build_model_map(density_markers, pattern_flow)
        
        # Create frame data
        frame_data = {
            'frame_number': len(self.frame_buffer),
            'timestamp': datetime.now().isoformat(),
            'n_value': self.n_value,
            'key_points': self.key_points,
            'density_markers': density_markers,
            'pattern_flow': pattern_flow
        }
        
        # Store in buffer
        self.frame_buffer.append(frame_data)
        if len(self.frame_buffer) > 100:
            self.frame_buffer.pop(0)
        
        return frame_data
    
    def render_3d_scatter(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Render 3D scatter plot of key points.
        
        Args:
            output_path: Path to save the plot (optional)
            
        Returns:
            Path to saved plot or None
        """
        if not self.key_points:
            return None
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract coordinates
        x = [point[0] for point in self.key_points]
        y = [point[1] for point in self.key_points]
        z = [point[2] for point in self.key_points]
        
        # Create scatter plot
        scatter = ax.scatter(x, y, z, c=range(len(x)), cmap=self.colormap, s=100)
        
        # Add labels
        ax.set_xlabel('X (Frequency)')
        ax.set_ylabel('Y (Temporal)')
        ax.set_zlabel('Z (Spatial)')
        ax.set_title(f'Neural Network Model Map (N={self.n_value:.2f})')
        
        # Add colorbar
        plt.colorbar(scatter, label='Point Index')
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.show()
            plt.close()
            return None
    
    def render_wave_pattern(self, triangulation_vectors: np.ndarray, output_path: Optional[str] = None) -> Optional[str]:
        """
        Render wave pattern from triangulation vectors.
        
        Args:
            triangulation_vectors: Triangulation vectors (3x3 matrix)
            output_path: Path to save the plot (optional)
            
        Returns:
            Path to saved plot or None
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot each vector component
        for i, ax in enumerate(axes.flat):
            if i < 3:
                vector = triangulation_vectors[i]
                ax.plot(vector, 'o-', linewidth=2, markersize=8)
                ax.set_title(f'Vector {i+1}')
                ax.set_ylim(-1.5, 1.5)
                ax.grid(True)
            else:
                # Plot combined vectors
                combined = np.mean(triangulation_vectors, axis=0)
                ax.plot(combined, 'o-', linewidth=2, markersize=8, color='red')
                ax.set_title('Combined Vector')
                ax.set_ylim(-1.5, 1.5)
                ax.grid(True)
        
        plt.suptitle(f'Triangulation Vectors (N={self.n_value:.2f})')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.show()
            plt.close()
            return None
    
    def render_density_heatmap(self, density_markers: Dict[str, float], output_path: Optional[str] = None) -> Optional[str]:
        """
        Render density heatmap.
        
        Args:
            density_markers: Dictionary of density markers
            output_path: Path to save the plot (optional)
            
        Returns:
            Path to saved plot or None
        """
        # Create 2D density matrix
        grid_size = 50
        density_matrix = np.zeros((grid_size, grid_size))
        
        # Fill matrix based on density markers
        alpha = density_markers.get('alpha_density', 0.5)
        beta = density_markers.get('beta_density', 0.5)
        frequency = density_markers.get('frequency_density', 1.0)
        
        x = np.linspace(0, frequency, grid_size)
        y = np.linspace(0, frequency, grid_size)
        X, Y = np.meshgrid(x, y)
        
        # Create density pattern
        density_matrix = alpha * np.sin(X) + beta * np.cos(Y)
        
        # Plot heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(density_matrix, cmap=self.colormap, interpolation=self.interpolation)
        ax.set_title('Density Heatmap')
        plt.colorbar(im, ax=ax, label='Density')
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.show()
            plt.close()
            return None
    
    def create_animation(self, output_path: str, duration_seconds: float = 5.0):
        """
        Create animation from frame buffer.
        
        Args:
            output_path: Path to save animation
            duration_seconds: Duration of animation in seconds
        """
        if not self.frame_buffer:
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def update_frame(frame_idx):
            ax.clear()
            
            if frame_idx < len(self.frame_buffer):
                frame = self.frame_buffer[frame_idx]
                key_points = frame.get('key_points', [])
                
                if key_points:
                    x = [point[0] for point in key_points]
                    y = [point[1] for point in key_points]
                    z = [point[2] for point in key_points]
                    
                    ax.scatter(x, y, c=z, cmap=self.colormap, s=100)
                    ax.set_title(f'Frame {frame_idx} (N={self.n_value:.2f})')
                    ax.set_xlim(-2, 2)
                    ax.set_ylim(-2, 2)
        
        num_frames = len(self.frame_buffer)
        interval = (duration_seconds / num_frames) * 1000
        
        anim = animation.FuncAnimation(
            fig, update_frame, frames=num_frames,
            interval=interval, blit=False
        )
        
        anim.save(output_path, writer='pillow', fps=30)
        plt.close()
    
    def get_render_statistics(self) -> Dict[str, any]:
        """
        Get statistics about rendered frames.
        
        Returns:
            Dictionary containing render statistics
        """
        return {
            'total_frames': len(self.frame_buffer),
            'n_value': self.n_value,
            'key_points_count': len(self.key_points),
            'model_map_keys': list(self.model_map.keys()),
            'render_resolution': self.render_resolution,
            'colormap': self.colormap
        }
    
    def export_frame_buffer(self, output_path: str):
        """
        Export frame buffer to JSON file.
        
        Args:
            output_path: Path to save JSON file
        """
        export_data = {
            'n_value': self.n_value,
            'render_resolution': self.render_resolution,
            'frames': self.frame_buffer,
            'model_map': self.model_map
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
