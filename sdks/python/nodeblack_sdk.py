"""
NodeBlack Python SDK
Universal File Converter API Client

Installation:
    pip install requests

Usage:
    from nodeblack_sdk import NodeBlackClient
    
    client = NodeBlackClient("your-api-key")
    result = client.convert_file("image.png", "jpg")
    client.download_file(result["task_id"], "converted.jpg")
"""

import requests
import time
from typing import Optional, Dict, Any
from pathlib import Path

class NodeBlackClient:
    def __init__(self, api_key: str, base_url: str = "https://nodeblack.onrender.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})
    
    def convert_file(self, file_path: str, target_format: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Convert a file to target format
        
        Args:
            file_path: Path to input file
            target_format: Target format (e.g., 'jpg', 'png', 'mp3')
            timeout: Max wait time in seconds
            
        Returns:
            Dict with task_id and status
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'target_format': target_format}
            
            response = self.session.post(
                f"{self.base_url}/api/convert",
                files=files,
                params=params
            )
            response.raise_for_status()
            
        result = response.json()
        task_id = result['task_id']
        
        # Wait for completion
        return self._wait_for_completion(task_id, timeout)
    
    def _wait_for_completion(self, task_id: str, timeout: int) -> Dict[str, Any]:
        """Wait for conversion to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_status(task_id)
            
            if status['status'] == 'ready':
                return {'task_id': task_id, 'status': 'completed'}
            elif status['status'] in ['failed', 'expired']:
                raise Exception(f"Conversion failed: {status.get('message', 'Unknown error')}")
            
            time.sleep(1)
        
        raise TimeoutError(f"Conversion timeout after {timeout} seconds")
    
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get conversion status"""
        response = self.session.get(f"{self.base_url}/api/status/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def download_file(self, task_id: str, output_path: str) -> str:
        """Download converted file"""
        response = self.session.get(f"{self.base_url}/api/download/{task_id}")
        response.raise_for_status()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return str(output_path)
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """Get all supported formats"""
        response = self.session.get(f"{self.base_url}/api/formats")
        response.raise_for_status()
        return response.json()
    
    def list_files(self) -> Dict[str, Any]:
        """List all converted files"""
        response = self.session.get(f"{self.base_url}/api/files")
        response.raise_for_status()
        return response.json()

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = NodeBlackClient("your-api-key-here")
    
    try:
        # Convert image
        result = client.convert_file("input.png", "jpg")
        print(f"✅ Conversion completed: {result}")
        
        # Download result
        output_file = client.download_file(result["task_id"], "output.jpg")
        print(f"✅ Downloaded: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")