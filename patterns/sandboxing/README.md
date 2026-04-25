# Sandboxing

## Overview

Isolated execution environments for agent operations, particularly code execution, web browsing, and untrusted tool usage. Sandboxing limits the potential damage from compromised or malfunctioning agents by constraining their access to system resources, network, and data.

## Use Cases

### Code Execution Sandboxing
- Agents that write and execute code (PAL pattern, code interpreters)
- User-submitted code evaluation
- Dynamic function generation and testing

### Browser Sandboxing
- Agents that browse the web
- Web automation and scraping
- Testing web applications

### Tool Execution Sandboxing
- Running untrusted or third-party tools
- Isolating potentially dangerous operations
- Multi-tenant agent environments

## Sandboxing Strategies

### 1. Process Isolation

```python
import subprocess
import tempfile
import os
from pathlib import Path

class ProcessSandbox:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.allowed_commands = {'python3', 'node', 'bash'}
        
    def execute_code(self, code: str, language: str = 'python') -> str:
        """Execute code in isolated process"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f'.{language}',
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Validate code doesn't contain dangerous patterns
            self._validate_code(code)
            
            # Execute with restrictions
            result = subprocess.run(
                [language, temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._restricted_env(),
                preexec_fn=self._restrict_process if os.name != 'nt' else None
            )
            
            # Sanitize output before returning
            return self._sanitize_output(result.stdout, result.stderr)
            
        finally:
            # Cleanup
            os.unlink(temp_file)
    
    def _validate_code(self, code: str) -> None:
        """Block dangerous operations"""
        dangerous_patterns = [
            r'__import__\s*\(',
            r'os\.system\s*\(',
            r'subprocess\.',
            r'eval\s*\(',
            r'exec\s*\(',
            r'open\s*\([^)]*[\'"][^\'"]*[\'"]\s*,\s*[\'"]w',  # File write
            r'shutil\.',
            r'rm\s+-rf',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                raise SecurityError(f"Dangerous code pattern detected: {pattern}")
    
    def _restricted_env(self) -> dict:
        """Create restricted environment"""
        # Start with minimal environment
        env = {
            'PATH': '/usr/bin:/bin',
            'LANG': 'C.UTF-8',
            'PYTHONPATH': '',
            'HOME': tempfile.gettempdir(),
        }
        
        # Explicitly remove dangerous variables
        dangerous_vars = [
            'AWS_ACCESS_KEY', 'AWS_SECRET_KEY',
            'DATABASE_URL', 'API_KEY', 'SECRET',
            'SSH_AUTH_SOCK', 'GNUPGHOME'
        ]
        
        for var in dangerous_vars:
            env.pop(var, None)
        
        return env
    
    def _restrict_process(self):
        """Apply process-level restrictions (Unix)"""
        import resource
        
        # Limit resources
        resource.setrlimit(resource.RLIMIT_CPU, (self.timeout, self.timeout))
        resource.setrlimit(resource.RLIMIT_MEMORY, (1024 * 1024 * 512, 1024 * 1024 * 512))  # 512MB
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))  # Max open files
        
        # Drop privileges (if running as root)
        # os.setgid(1000)
        # os.setuid(1000)
    
    def _sanitize_output(self, stdout: str, stderr: str) -> str:
        """Remove sensitive information from output"""
        # Combine and redact
        output = stdout + stderr
        
        # Redact potential secrets
        output = re.sub(r'[A-Za-z0-9]{32,}', '[REDACTED]', output)
        
        return output[:10000]  # Limit output size
```

### 2. Container-Based Sandboxing

```python
import docker
from docker.types import ContainerSpec, Resources

class DockerSandbox:
    def __init__(self):
        self.client = docker.from_env()
        
    def execute_in_container(self, code: str, image: str = 'python:3.11-slim') -> str:
        """Execute code in isolated Docker container"""
        
        container = None
        try:
            # Create container with restrictions
            container = self.client.containers.run(
                image=image,
                command=f'python -c "{code}"',
                detach=True,
                remove=True,
                # Resource limits
                mem_limit='256m',
                cpu_quota=50000,  # 50% of one CPU
                pids_limit=50,
                # Network isolation
                network='none',  # No network access
                # Filesystem isolation
                read_only=True,
                tmpfs={'/tmp': 'rw,noexec,nosuid,size=64m'},
                # Security options
                security_opt=['no-new-privileges'],
                cap_drop=['ALL'],  # Drop all capabilities
            )
            
            # Wait for completion
            result = container.wait(timeout=30)
            
            # Get logs
            logs = container.logs().decode('utf-8')
            
            return self._sanitize_output(logs)
            
        except docker.errors.APIError as e:
            raise SandboxError(f"Container execution failed: {str(e)}")
        finally:
            if container:
                container.stop(timeout=1)
    
    def execute_with_network(self, code: str, allowed_hosts: list) -> str:
        """Execute with limited network access"""
        
        container = None
        try:
            # Create custom network with restrictions
            network = self.client.networks.create(
                'sandbox-net',
                driver='bridge',
                internal=False,
                labels={'sandbox': 'true'}
            )
            
            container = self.client.containers.run(
                'python:3.11-slim',
                command=f'python -c "{code}"',
                detach=True,
                remove=True,
                network=network.name,
                # Allow only specific hosts (requires DNS filtering)
                # This is a simplification - real implementation needs DNS filtering
                mem_limit='512m',
                read_only=True,
                tmpfs={'/tmp': 'rw,noexec,nosuid,size=64m'},
            )
            
            result = container.wait(timeout=60)
            return container.logs().decode('utf-8')
            
        finally:
            if container:
                container.stop(timeout=1)
            if network:
                network.remove()
```

### 3. Browser Sandboxing

```python
from playwright.sync_api import sync_playwright
import tempfile

class BrowserSandbox:
    def __init__(self):
        self.playwright = sync_playwright().start()
        
    def browse_safely(self, url: str, actions: list = None) -> dict:
        """Browse web pages in isolated browser context"""
        
        browser = None
        try:
            # Launch browser in headless mode with security flags
            browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                ]
            )
            
            # Create isolated context
            context = browser.new_context(
                # No persistent storage
                storage_state=None,
                # Block dangerous features
                java_script_enabled=True,  # Can be disabled for higher security
                cookies=[],
                # Network restrictions
                ignore_https_errors=False,
                # Screen size
                viewport={'width': 1280, 'height': 720},
            )
            
            page = context.new_page()
            
            # Navigate with timeout
            page.goto(url, timeout=30000, wait_until='networkidle')
            
            # Execute allowed actions
            results = []
            if actions:
                for action in actions:
                    result = self._execute_safe_action(page, action)
                    results.append(result)
            
            # Get page content (sanitized)
            content = page.content()
            
            return {
                'url': url,
                'status': page.title(),
                'content': self._sanitize_html(content),
                'actions': results
            }
            
        finally:
            if browser:
                browser.close()
    
    def _execute_safe_action(self, page, action: dict) -> any:
        """Execute browser action with validation"""
        action_type = action.get('type')
        
        # Whitelist of allowed actions
        allowed_actions = ['click', 'fill', 'evaluate', 'screenshot']
        
        if action_type not in allowed_actions:
            raise SecurityError(f"Action {action_type} not allowed")
        
        # Validate selectors (prevent XSS)
        if 'selector' in action:
            self._validate_selector(action['selector'])
        
        # Execute with timeout
        if action_type == 'click':
            page.click(action['selector'], timeout=5000)
        elif action_type == 'fill':
            page.fill(action['selector'], action['value'], timeout=5000)
        elif action_type == 'evaluate':
            # Sanitize JavaScript
            self._validate_javascript(action['script'])
            return page.evaluate(action['script'])
        
        return {'status': 'success', 'action': action_type}
    
    def _validate_selector(self, selector: str):
        """Validate CSS selector"""
        if not re.match(r'^[a-zA-Z0-9\-_\.\#\[\]=\"\'\s:]+$', selector):
            raise SecurityError("Invalid CSS selector")
    
    def _validate_javascript(self, script: str):
        """Basic JavaScript validation"""
        dangerous_patterns = [
            r'document\.cookie',
            r'localStorage',
            r'sessionStorage',
            r'eval\s*\(',
            r'Function\s*\(',
            r'fetch\s*\([^)]*http',
            r'XMLHttpRequest',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, script):
                raise SecurityError(f"Dangerous JS pattern: {pattern}")
    
    def _sanitize_html(self, html: str) -> str:
        """Remove scripts and dangerous elements"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script tags
        for script in soup(['script', 'iframe', 'object', 'embed']):
            script.decompose()
        
        # Remove event handlers
        for tag in soup.find_all(True):
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr.startswith('on'):  # onclick, onload, etc.
                    del tag[attr]
        
        return str(soup)
```

### 4. File System Sandboxing

```python
import os
from pathlib import Path
import tempfile

class FileSystemSandbox:
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or tempfile.mkdtemp(prefix='sandbox_')
        self.allowed_paths = {self.base_dir}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_total_size = 100 * 1024 * 1024  # 100MB
        
    def safe_read(self, path: str) -> str:
        """Read file within sandbox"""
        full_path = self._resolve_path(path)
        self._validate_path(full_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")
        
        if os.path.getsize(full_path) > self.max_file_size:
            raise SecurityError(f"File too large: {path}")
        
        with open(full_path, 'r') as f:
            return f.read()
    
    def safe_write(self, path: str, content: str) -> None:
        """Write file within sandbox"""
        full_path = self._resolve_path(path)
        self._validate_path(full_path)
        
        # Check total size
        current_total = self._get_total_size()
        if current_total + len(content) > self.max_total_size:
            raise SecurityError("Sandbox storage quota exceeded")
        
        # Create parent directories
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path to absolute within sandbox"""
        # Prevent path traversal
        path = os.path.normpath(path)
        if path.startswith('..'):
            raise SecurityError("Path traversal not allowed")
        
        full_path = os.path.join(self.base_dir, path)
        return os.path.abspath(full_path)
    
    def _validate_path(self, path: str) -> None:
        """Ensure path is within sandbox"""
        real_path = os.path.realpath(path)
        
        for allowed in self.allowed_paths:
            if real_path.startswith(os.path.realpath(allowed)):
                return
        
        raise SecurityError(f"Access denied: {path} is outside sandbox")
    
    def _get_total_size(self) -> int:
        """Calculate total size of files in sandbox"""
        total = 0
        for root, dirs, files in os.walk(self.base_dir):
            for f in files:
                total += os.path.getsize(os.path.join(root, f))
        return total
    
    def cleanup(self):
        """Remove sandbox and all contents"""
        import shutil
        shutil.rmtree(self.base_dir, ignore_errors=True)
```

## Best Practices

1. **Defense in Depth**: Combine multiple sandboxing layers
2. **Minimal Privileges**: Grant only necessary permissions
3. **Timeout Everything**: All operations should have timeouts
4. **Resource Limits**: CPU, memory, disk, network quotas
5. **Audit Execution**: Log all sandboxed operations
6. **Regular Updates**: Keep sandbox environments patched
7. **Escape Detection**: Monitor for sandbox escape attempts

## When to Use

- Code execution agents (PAL, code interpreters)
- Web browsing agents
- Multi-tenant systems
- User-submitted content processing
- Testing untrusted code or tools

## When NOT to Use

- Trusted internal tools with known behavior
- Performance-critical operations (sandboxing adds overhead)
- Operations requiring full system access

## Related Patterns

- [Prompt Injection Defense](../prompt-injection-defense/) - Prevent malicious code injection
- [Tool Permissioning](../tool-permissioning/) - Control which tools can be used
- [Secret Handling](../secret-handling/) - Protect credentials from sandboxed code
- [Audit Logging](../audit-logging/) - Track sandboxed operations

## References

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Playwright Security](https://playwright.dev/docs/security)
- [gVisor Container Sandbox](https://gvisor.dev/)
- [Firecracker MicroVMs](https://firecracker-microvm.github.io/)
- [OWASP Code Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html)