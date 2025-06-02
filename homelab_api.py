#!/usr/bin/env python3
"""
Example Homelab API Server
This provides endpoints that the Discord bot can interact with.
Deploy this on your homelab server behind Traefik.
"""

from flask import Flask, jsonify, request
import docker
import psutil
import subprocess
import os
from functools import wraps
import time

app = Flask(__name__)

# API Key for authentication
API_KEY = os.getenv('API_KEY', 'your-secret-api-key')

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        if token != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/status')
@require_auth
def get_status():
    """Get overall system status"""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        status = {
            'docker': 'up' if len(containers) > 0 else 'down',
            'api_server': 'up',
            'traefik': 'up',  # Assume up if we're responding
            'total_containers': len(containers),
            'timestamp': int(time.time())
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system')
@require_auth
def get_system_info():
    """Get system resource information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get uptime
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_string = str(int(uptime_seconds // 86400)) + "d " + \
                       str(int((uptime_seconds % 86400) // 3600)) + "h " + \
                       str(int((uptime_seconds % 3600) // 60)) + "m"
        
        system_info = {
            'cpu_usage': round(cpu_percent, 1),
            'memory_usage': round(memory.percent, 1),
            'memory_total_gb': round(memory.total / (1024**3), 1),
            'memory_used_gb': round(memory.used / (1024**3), 1),
            'disk_usage': round(disk.percent, 1),
            'disk_total_gb': round(disk.total / (1024**3), 1),
            'disk_used_gb': round(disk.used / (1024**3), 1),
            'uptime': uptime_string
        }
        
        return jsonify(system_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/containers')
@require_auth
def get_containers():
    """Get list of Docker containers"""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        container_list = []
        for container in containers:
            container_info = {
                'id': container.short_id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'status': container.status,
                'state': container.attrs['State']['Status'],
                'created': container.attrs['Created'],
                'ports': container.attrs['NetworkSettings']['Ports']
            }
            container_list.append(container_info)
        
        return jsonify(container_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/<service_name>/restart', methods=['POST'])
@require_auth
def restart_service(service_name):
    """Restart a Docker container or system service"""
    try:
        client = docker.from_env()
        
        # Try to find container by name
        try:
            container = client.containers.get(service_name)
            container.restart()
            return jsonify({
                'message': f'Container {service_name} restarted successfully',
                'status': 'success'
            })
        except docker.errors.NotFound:
            # Try as a system service
            try:
                result = subprocess.run(['systemctl', 'restart', service_name], 
                                      capture_output=True, text=True, check=True)
                return jsonify({
                    'message': f'Service {service_name} restarted successfully',
                    'status': 'success'
                })
            except subprocess.CalledProcessError as e:
                return jsonify({
                    'error': f'Failed to restart service {service_name}: {e.stderr}',
                    'status': 'error'
                }), 400
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/compose/<stack_name>/restart', methods=['POST'])
@require_auth
def restart_compose_stack(stack_name):
    """Restart a Docker Compose stack"""
    try:
        # Assume compose files are in /opt/docker/<stack_name>/
        compose_dir = f'/opt/docker/{stack_name}'
        
        if not os.path.exists(compose_dir):
            return jsonify({'error': f'Stack {stack_name} not found'}), 404
        
        # Run docker-compose restart
        result = subprocess.run(['docker-compose', 'restart'], 
                              cwd=compose_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                'message': f'Stack {stack_name} restarted successfully',
                'status': 'success'
            })
        else:
            return jsonify({
                'error': f'Failed to restart stack {stack_name}: {result.stderr}',
                'status': 'error'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': int(time.time())})

@app.route('/api/traefik/services')
@require_auth
def get_traefik_services():
    """Get Traefik services (requires Traefik API access)"""
    try:
        # This would require accessing Traefik's API
        # You'll need to configure Traefik to expose its API
        import requests
        
        traefik_api_url = os.getenv('TRAEFIK_API_URL', 'http://traefik:8080')
        response = requests.get(f'{traefik_api_url}/api/http/services')
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to fetch Traefik services'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the API server
    app.run(host='0.0.0.0', port=5000, debug=False)