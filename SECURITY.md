# Security Policy

## Security Improvements Implemented

### 1. Dependency Management
- **requirements.txt**: All dependencies are pinned to specific secure versions
- Regular updates recommended for security patches
- Certifi package ensures up-to-date CA certificates

### 2. Download Verification
- **SHA256 Hashing**: All downloads are hashed for integrity verification
- **File Size Limits**: Maximum download size enforced (configurable, default 500MB)
- **HTTPS with SSL Verification**: All network requests verify SSL certificates
- **Timeout Protection**: Connection timeouts prevent hanging on malicious servers

### 3. Secure Subprocess Execution
- **subprocess Module**: Replaced `os.system()` with secure `subprocess.Popen()`
- **Shell=False**: Prevents command injection attacks
- **Explicit Paths**: No shell interpretation of commands

### 4. Path Traversal Protection
- **Zip Extraction Safety**: All zip file paths validated before extraction
- **Normalized Paths**: Prevents `../` directory traversal attacks
- **Absolute Path Detection**: Blocks extraction to arbitrary system locations

### 5. Configuration Management
- **config.json**: Externalized hardcoded URLs and settings
- **Default Fallbacks**: Safe defaults if config file missing or corrupted
- **Easy Updates**: Server URLs and limits configurable without code changes

### 6. Error Handling
- **Specific Exceptions**: Replaced broad `except Exception` with targeted catches
- **Graceful Degradation**: Failures don't expose sensitive information
- **User Feedback**: Clear error messages without stack traces

## TODO: Future Security Enhancements

1. **Code Signing**: Implement digital signature verification for downloaded executables
2. **Hash Verification**: Server should provide expected SHA256 hashes to verify against
3. **Update Rollback**: Ability to revert to previous version if update fails
4. **Secure Storage**: Encrypt sensitive configuration data
5. **Rate Limiting**: Prevent update check spam/DoS
6. **Certificate Pinning**: Pin expected SSL certificate for update server

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **DO NOT** open a public GitHub issue
2. Email security concerns to: [YOUR-EMAIL]
3. Include detailed reproduction steps
4. Allow 90 days for patches before public disclosure

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

Always use the latest version for security updates.
