# RedisM - Modern Redis Management Tool

<div align="center">

![RedisM Logo](https://img.shields.io/badge/RedisM-v1.0.1-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.14+-green?style=for-the-badge)

**A modern, feature-rich Redis management application for macOS**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Development](#development)

</div>

## 🚀 Features

### 🔗 Connection Management
- **Multiple Connections**: Manage multiple Redis server connections
- **SSH Tunnel Support**: Connect to Redis servers through SSH tunnels
- **Authentication**: Support for Redis username/password authentication
- **Connection Testing**: Test connections before saving
- **Flexible SSH Auth**: Both password and private key authentication

### 🔑 Key Management
- **Hierarchical View**: Tree-like display of keys with customizable separators
- **All Data Types**: Full support for String, List, Set, Hash, and ZSet
- **Real-time Operations**: Direct add/edit operations without batch updates
- **Advanced Filtering**: Filter functionality for all data types
- **Data Integrity**: Maintains hidden data when filtering is active

### 💻 Command Line Interface
- **Built-in CLI**: Execute Redis commands directly
- **Command Completion**: Auto-completion for Redis commands
- **Syntax Highlighting**: Enhanced command output display
- **Command History**: Navigate through previous commands

### 🎨 Modern UI
- **Native macOS Design**: Follows macOS design guidelines
- **Responsive Layout**: Adapts to different window sizes
- **Intuitive Navigation**: Easy-to-use interface with clear visual hierarchy
- **Real-time Feedback**: Immediate visual feedback for all operations

## 📦 Installation

### Download
1. Download the latest `RedisM.dmg` from the releases
2. Open the DMG file
3. Drag RedisM.app to your Applications folder
4. Launch RedisM from Applications

### Build from Source
```bash
# Clone the repository
git clone <repository-url>
cd RedisM

# Install dependencies
pip install -r requirements.txt

# Build the application
sh build_python.sh
```

## 🔧 Usage

### Creating a Connection
1. Click **"➕ Add"** in the Connections panel
2. Fill in your Redis server details:
   - **Connection Name**: A friendly name for your connection
   - **Redis Host**: Your Redis server address
   - **Port**: Redis port (default: 6379)
   - **Username/Password**: Authentication credentials (if required)
   - **Max Keys**: Maximum keys to load (0 = unlimited)
   - **Databases**: Number of databases (default: 16)

### SSH Tunnel Configuration
1. Check **"Enable SSH Tunnel"** in the connection dialog
2. Configure SSH server details:
   - **SSH Host**: Your SSH server address
   - **Port**: SSH port (default: 22)
   - **Username**: SSH username
3. Choose authentication method:
   - **Password**: Enter SSH password
   - **Private Key**: Select key file or paste key content

### Key Management
- **Browse Keys**: Use the tree view to navigate your keys
- **Filter Data**: Use the "Find" button to filter data in Lists, Sets, Hashes, and ZSets
- **Edit Values**: Double-click any value to edit it directly
- **Add Items**: Use "Add Item" to add new entries
- **Real-time Updates**: Changes are applied immediately to Redis

### Command Line
- Use the built-in command line interface for direct Redis operations
- Type commands and press Enter to execute
- Use Tab for command completion
- View formatted output with syntax highlighting

## 🛠 Development

### Project Structure
```
RedisM/
├── redis_manager.py      # Main application file
├── config.py            # Configuration and constants
├── create_icon.py       # Icon generation utility
├── build_python.sh      # Build script for macOS app
├── requirements.txt     # Python dependencies
├── docs/               # Documentation
│   ├── README.md       # Detailed documentation
│   └── *.md           # Feature documentation
└── dist/              # Built application (after build)
```

### Key Components
- **RedisManager**: Main application class handling UI and Redis operations
- **Connection Dialog**: Modern connection configuration interface
- **Key Tree View**: Hierarchical key display with filtering
- **Command Interface**: Built-in Redis CLI with completion

### Building
The application uses PyInstaller to create a native macOS app:
```bash
sh build_python.sh
```

This creates:
- `dist/RedisM.app` - The application bundle
- `RedisM.dmg` - Installer disk image

## 📋 Requirements

### System Requirements
- **macOS**: 10.14 or later
- **Python**: 3.14+ (for development)
- **Memory**: 50MB+ available RAM
- **Disk**: 100MB+ available space

### Python Dependencies
- `redis` - Redis client library
- `paramiko` - SSH client for tunnel connections
- `tkinter` - GUI framework (included with Python)

## 🔄 Recent Updates

### Version 1.0.1
- ✅ **Test Connection Feature**: Real connection testing with comprehensive validation
- ✅ **Enhanced File Selection**: Support for all file types in SSH private key selection
- ✅ **Bug Fixes**: Resolved duplicate default values and layout consistency issues

### Version 1.0.0
- ✅ **Enhanced Connection Dialog**: Modern UI with unified SSH authentication layout
- ✅ **Real-time Operations**: Direct Redis operations without batch updates
- ✅ **Advanced Filtering**: Filter support for all Redis data types
- ✅ **Connection Testing**: Test connections before saving
- ✅ **Data Integrity**: Maintains filtered data consistency
- ✅ **UI Improvements**: Better spacing, hover effects, and visual hierarchy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation in the `docs/` folder
2. Review the troubleshooting guide
3. Create an issue on the repository

---

<div align="center">
Made with ❤️ for the Redis community
</div>