import matplotlib.pyplot as plt
import os
import time
import uuid
from typing import List
from mcp.server.fastmcp import FastMCP

# Use non-interactive backend
plt.switch_backend('Agg')

# Initialize FastMCP server
mcp = FastMCP("chart-mcp-server")

# Configuration
STATIC_DIR = os.path.join(os.getcwd(), "static", "charts")
# Ensure directory exists (redundant check but safe)
os.makedirs(STATIC_DIR, exist_ok=True)

# We will return relative paths or full URLs depending on how we want the client to use it.
# Assuming the server serves /static/charts, we can return the relative path or filename.
# Let's return the filename and let the client construct the URL or Markdown.

def _save_plot() -> str:
    """Helper to save the current plot to a file and return the filename."""
    filename = f"chart_{int(time.time())}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    # Return Markdown image syntax directly to ensure it renders
    return f"![Chart](/static/charts/{filename})"

@mcp.tool()
def generate_bar_chart(title: str, x_label: str, y_label: str, categories: List[str], values: List[float]) -> str:
    """
    Generate a bar chart.
    
    Args:
        title: Chart title
        x_label: Label for X axis
        y_label: Label for Y axis
        categories: List of category names (X axis)
        values: List of numerical values (Y axis)
        
    Returns:
        A Markdown string containing the image URL.
    """
    try:
        plt.figure(figsize=(10, 6))
        # Support Chinese characters on MacOS and other systems
        plt.rcParams['font.sans-serif'] = ['PingFang HK', 'PingFang SC', 'Arial Unicode MS', 'Heiti TC', 'Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'Noto Sans CJK TC', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        plt.bar(categories, values, color='skyblue')
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks(rotation=45)
        
        return _save_plot()
    except Exception as e:
        plt.close()
        return f"Error generating chart: {str(e)}"

@mcp.tool()
def generate_pie_chart(title: str, labels: List[str], values: List[float]) -> str:
    """
    Generate a pie chart.
    
    Args:
        title: Chart title
        labels: List of category labels
        values: List of numerical values
        
    Returns:
        A Markdown string containing the image URL.
    """
    try:
        plt.figure(figsize=(8, 8))
        plt.rcParams['font.sans-serif'] = ['PingFang HK', 'PingFang SC', 'Arial Unicode MS', 'Heiti TC', 'Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'Noto Sans CJK TC', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(title)
        
        return _save_plot()
    except Exception as e:
        plt.close()
        return f"Error generating chart: {str(e)}"

if __name__ == "__main__":
    mcp.run()
