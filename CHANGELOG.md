# Changelog

All notable changes to RedisM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-12-25

### Added
- ✅ **Test Connection Feature**: Implemented real connection testing with SSH tunnel support
- ✅ **Connection Validation**: Comprehensive validation for Redis and SSH configurations
- ✅ **Real-time Feedback**: Async connection testing with progress indication

### Improved
- ✅ **File Selection**: Removed file type restrictions for SSH private key selection
- ✅ **Default Values**: Fixed duplicate default values issue in connection editing
- ✅ **User Experience**: Enhanced connection dialog with better error handling

### Fixed
- 🐛 **Duplicate Defaults**: Fixed issue where default values were filled twice when editing connections
- 🐛 **Layout Consistency**: Resolved SSH authentication layout width inconsistencies
- 🐛 **File Compatibility**: Improved private key file selection to support all file types

## [1.0.0] - 2024-12-25

### Added
- **Connection Management**: Multiple Redis connection configurations with save/load functionality
- **SSH Tunnel Support**: Full SSH tunnel support with password and private key authentication
- **Connection Testing**: Test connections before saving with detailed feedback
- **Modern Connection Dialog**: Enhanced UI with unified SSH authentication layout
- **Real-time Operations**: Direct Redis operations without requiring batch updates
- **Advanced Filtering**: Filter functionality for all Redis data types (Hash, List, Set, ZSet)
- **Hierarchical Key View**: Tree-like display of keys with customizable separators
- **Built-in CLI**: Redis command line interface with auto-completion
- **Data Type Support**: Full support for String, List, Set, Hash, and ZSet operations
- **JSON Editor**: Built-in JSON formatting and editing for Hash values
- **Streaming Key Loading**: Efficient loading of up to 100,000 keys
- **Connection Keepalive**: Automatic connection maintenance
- **Native macOS UI**: Modern interface following macOS design guidelines

### Enhanced
- **UI Improvements**: Better spacing, hover effects, and visual hierarchy
- **Data Integrity**: Maintains hidden data when filtering is active
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Performance**: Optimized for large datasets with streaming operations
- **User Experience**: Intuitive navigation and immediate visual feedback

### Fixed
- **Query Button Logic**: Improved query execution and Hash field queries
- **Update All Functionality**: Preserves filtered data during batch updates
- **SSH Authentication**: Reliable switching between password and key authentication
- **Connection Dialog**: Consistent layout and field validation
- **Default Values**: Proper handling of default values in connection forms

### Technical
- **Code Organization**: Clean, modular codebase with comprehensive documentation
- **Build System**: Automated macOS app building with PyInstaller
- **Dependencies**: Minimal dependencies with robust error handling
- **Documentation**: Comprehensive feature documentation and user guides

---

## Development Notes

### Architecture
- **Single File Application**: All functionality consolidated in `redis_manager.py`
- **Configuration Management**: Centralized config in `config.py`
- **Build Automation**: Streamlined build process with `build_python.sh`

### Removed in 1.0.0
- Unused `connection_manager.py` and `key_manager.py` modules
- Test files and development utilities
- Redundant build configurations

### Future Roadmap
- Multi-platform support (Windows, Linux)
- Plugin system for custom data types
- Advanced query builder
- Data export/import functionality
- Performance monitoring and analytics