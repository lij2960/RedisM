# Changelog

All notable changes to RedisM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.5] - 2026-04-15

### 🚀 Added
- **Bitmap Support**: Full support for displaying Bitmap binary data
  - Fixed Bitmap data showing empty due to `decode_responses=True` in Redis connection
  - Use raw bytes to fetch string type data to support binary content
  - Smart detection of binary data with hex and binary bit representation
  - Display byte count and number of bits set to 1

- **CLI Bitmap Commands**: Added Bitmap command support
  - SETBIT, GETBIT, BITCOUNT, BITOP, BITPOS, BITFIELD commands added to auto-complete
  - Improved command parsing using shlex for quoted arguments support

### 🔧 Fixed
- **ZSet Display**: Fixed ZSet type data showing empty
  - Corrected parsing of `zrange(withscores=True)` tuple list format
  - Fixed ZSet total count calculation (removed incorrect `// 2`)
  - Fixed ZSet filter functionality to handle tuple format correctly

- **Binary Data Display**: Improved handling of binary string data
  - Created temporary `decode_responses=False` client for raw data retrieval
  - Added `_format_value_for_display()` method for intelligent value formatting
  - Added `_format_binary_value()` method for hex/binary representation
  - Handle empty bytes and null-byte data gracefully

## [1.1.4] - 2026-04-13

### 🚀 Added
- **CLI Extended Commands**: New custom commands for batch operations
  - `DELPATTERN <pattern>`: Batch delete keys matching a pattern using SCAN (non-blocking)
  - `COUNTPATTERN <pattern>`: Count keys matching a pattern without deletion
  - Dangerous command protection: FLUSHDB, FLUSHALL, DELPATTERN require confirmation dialog
  - Auto-refresh key list after batch delete operations

### 🔧 Fixed
- **SMEMBERS Command**: Fixed CLI freezing when executing SMEMBERS on large sets
  - Added proper handling for Python `set` type return values
  - Optimized result formatting for large datasets
  - Moved formatting to background thread to prevent UI blocking

- **Search Functionality**: Fixed "Find Previous" button not working
  - Corrected cursor position management for backward search
  - Fixed search start position handling with selected text
  - Applied fix to all search dialogs (key_manager.py and search_mixin.py)

### 🛠️ Improved
- **CLI Output**: Optimized command output handling
  - Bulk output updates to reduce UI flickering
  - Better progress feedback for batch operations
  - Thread-safe UI updates

## [1.1.3] - 2025-01-19

### 🧹 Maintenance
- **Project Cleanup**: Removed temporary test files and reorganized documentation
  - Deleted `test_imports.py` and `test_php_serialize.py` test scripts
  - Deleted `quick_rebuild.sh` (kept main `build_python.sh`)
  - Moved `PHP_SERIALIZE_USAGE.md` to `docs/` directory
  - Moved `REBUILD_INSTRUCTIONS.md` to `docs/` directory
  - Organized project structure for better maintainability

### 📚 Documentation
- **Enhanced README**: Comprehensive documentation update
  - Added PHP Serialize feature documentation
  - Updated feature list with all v1.1.x improvements
  - Added detailed usage examples for PHP serialize functionality
  - Improved quick start guide and installation instructions
  - Enhanced troubleshooting section
  - Updated version badges and project structure

### 🔧 Build
- **Improved Build Process**: Streamlined build configuration
  - Consolidated build scripts
  - Updated documentation references
  - Cleaned up temporary build artifacts

## [1.1.2] - 2025-01-19

### 🚀 Added
- **PHP Serialize Support**: Comprehensive PHP serialization parsing and formatting
  - Added "Format PHP" button to parse PHP serialized data and display as readable JSON
  - Added "Minify PHP" button to re-serialize data in compact PHP serialize format
  - Integrated PHP serialize functionality across all value display and edit dialogs:
    - String value editor in key manager
    - Hash field editor and add dialog
    - Set member editor and add dialog
    - List item editor
    - ZSet member editor and add dialog
    - Add new key dialog (string type)
  - PHP formatted data displays with JSON syntax highlighting for readability
  - Seamless conversion between PHP serialize and JSON formats

### 🔧 Fixed
- **Smart Format Detection**: Minify PHP now intelligently handles both JSON and PHP serialize input
  - Automatically detects input format (JSON or PHP serialize)
  - Converts JSON to PHP serialize format when needed
  - Prevents "unexpected opcode" error when minifying formatted JSON data
  - Supports round-trip conversion: PHP → Format → Minify → PHP
  - Improved error messages with user-friendly Chinese descriptions

### 📦 Dependencies
- Added `phpserialize>=1.3` library for PHP serialization support

### 🛠️ Build
- Updated `RedisM.spec` to include `phpserialize` in hiddenimports
- Updated `build_python.sh` to install all dependencies from requirements.txt
- Added missing dialog modules to PyInstaller configuration

## [1.1.1] - 2025-01-19

### 🔧 Fixed
- **Critical Connection Stability**: Resolved application freeze/crash when Redis disconnects
  - Replaced synchronous `check_and_reconnect()` calls with asynchronous `check_and_reconnect_async()`
  - Added connection timeout settings (5s socket timeout, 5s connect timeout) to prevent long blocks
  - Implemented non-blocking reconnection for all critical operations (key loading, searching, deletion)
  - Fixed UI thread blocking that caused application to become unresponsive during connection issues
  - Enhanced error handling with proper thread management for connection recovery

### 🚀 Enhanced
- **Robust Error Recovery**: Improved connection resilience across all operations
  - Key details loading now handles disconnections gracefully without freezing
  - Key search operations continue seamlessly after reconnection
  - Delete operations recover automatically from connection issues
  - CLI commands execute reliably with automatic reconnection
  - All operations provide clear status feedback during reconnection process

## [1.1.0] - 2025-01-19

### 🔧 Fixed
- **Database Switching Consistency**: Resolved critical database switching issues
  - Fixed "Add New Key" operations occasionally switching to default database
  - Fixed key deletion operations causing database reversion to default
  - Fixed key list refresh after operations showing wrong database content
  - Implemented centralized database state management in `get_redis_client()`
  - Ensured all Redis operations maintain current database selection

- **Auto-Height Dialog Enhancement**: Completed conversion of Add dialogs to auto-height
  - Converted `AddSetDialog` and `AddZSetDialog` from BaseDialog to SimpleDialog
  - Implemented true auto-height for value text boxes matching Edit dialogs
  - Added JSON syntax highlighting to all Add dialogs for consistency
  - Enhanced user experience with Format JSON and Minify JSON buttons

### 🔐 Enhanced
- **Connection Security**: Added password visibility toggle with system authentication
  - Added "View Password" button (👁 icon) next to Redis password field
  - Implemented system password verification before revealing stored passwords
  - Enhanced security by requiring macOS system authentication for password access
  - Improved user experience with secure password management

### 🎨 Improved
- **JSON Syntax Highlighting**: Comprehensive JSON formatting enhancement
  - Applied syntax highlighting to all text boxes with Format JSON functionality
  - Implemented color-coded JSON display (strings, keys, numbers, booleans, null values)
  - Enhanced readability with consistent color scheme across all dialogs
  - Real-time syntax highlighting during JSON editing

- **Filter and Statistics Enhancement**: Improved structured data display
  - Modified filter text boxes to fixed width (25 characters) for better layout
  - Added total count display showing "Total: X fields/items/members"
  - Fixed initial count display issues by proper data initialization order
  - Enhanced user experience with immediate and accurate statistics

## [1.0.5] - 2025-01-05

### 🔧 Fixed
- **UI Layout Improvements**: Fixed critical layout issues for better user experience
  - Fixed Add New Key dialog data type section getting compressed in small windows
  - Fixed Key Manager value area JSON format buttons and search controls getting hidden
  - Applied consistent fixed-height approach to prevent UI element compression
  - Improved grid layout weight configuration for proper auto-resizing

- **Hash Edit Dialog**: Fixed critical error in hash field editing
  - Resolved "HashEditDialog object has no attribute 'old_value'" error
  - Corrected hash operations (was incorrectly using set operations)
  - Added proper field name validation and change handling
  - Fixed success messages and error handling for hash operations

- **Tab Navigation**: Completely disabled mouse wheel tab switching
  - Removed unwanted scrollwheel switching between Key Manager and Command Line tabs
  - Preserved normal scrolling functionality for content areas
  - Enhanced user experience by preventing accidental tab changes

- **Key Manager Scrolling**: Removed unnecessary scrollbars from Key Manager window
  - Simplified layout by removing Canvas-based scrolling framework
  - Improved performance and visual clarity
  - Maintained proper auto-resizing behavior for content areas

### 🎨 Enhanced
- **Data Type Selection**: Improved Add New Key dialog layout
  - Changed data type radio buttons from two rows to single row for better space utilization
  - Increased minimum window size to ensure all controls remain visible
  - Enhanced visual spacing and button arrangement

- **Structured Data Display**: Enhanced filter and operation controls
  - Applied fixed-height approach to filter input areas for hash, list, set, zset types
  - Ensured operation buttons (Add Item, Delete Item, Update All, Refresh) always remain accessible
  - Improved table display auto-resizing while preserving control visibility

## [1.0.4] - 2024-12-31

### 🔄 Added
- **Intelligent Auto-Reconnection**: Implemented comprehensive auto-reconnection functionality
  - Automatic connection detection and recovery when Redis connection is lost
  - Seamless operation continuation after successful reconnection
  - Real-time status feedback during reconnection process
  - Enhanced error handling to distinguish connection errors from other issues
- **Auto-Reconnect for All Operations**: Extended auto-reconnect to all Redis operations
  - Key loading and viewing with automatic reconnection
  - Key updating and deletion with reconnection support
  - Database switching with connection recovery
  - Search operations with reconnection capability

### 🗄️ Fixed
- **Database Switching Key List Update**: Resolved issue where key tree structure showed old data after database switching
  - **Root Cause**: Redis connection pool inconsistency when switching databases
  - **Solution**: Implemented dedicated database client creation for each database switch
  - **Enhancement**: Added connection pool management to ensure database state consistency
- **Connection Pool Management**: Improved Redis connection pool handling
  - Added `get_database_client()` method for database-specific operations
  - Enhanced `select_database()` method with connection pool reset
  - Proper connection state management across database switches

### 🎨 Enhanced
- **Dual-Panel Server Information Layout**: Completely redesigned Redis server information display
  - **Left Panel**: Basic Information, Runtime Information, Memory Information
  - **Right Panel**: Statistics, Database Information (table format)
  - **Space Optimization**: Removed excessive padding, maximized screen space utilization
  - **Grid Layout**: Replaced vertical scrolling with efficient dual-column grid layout
- **Database Information Table**: Enhanced database information display
  - Table format showing Database, Keys count, and TTL keys count
  - Current database highlighted with background color
  - Scrollable table for servers with many databases
  - Real-time updates when switching databases

### 🔧 Improved
- **Connection Status Management**: Enhanced connection state tracking and user feedback
  - Clear status messages during reconnection attempts
  - Differentiated error messages for connection vs. operation failures
  - Progress indicators for long-running reconnection operations
- **Error Recovery**: Robust error handling with automatic retry mechanisms
  - Connection error detection and automatic retry
  - Operation continuation after successful reconnection
  - User-friendly error messages with actionable information
- **User Experience**: Seamless operation flow with minimal interruption
  - Transparent reconnection process
  - Automatic operation retry after reconnection
  - Clear status feedback throughout the process

### 🧹 Cleaned
- **Project Structure**: Comprehensive cleanup of development artifacts
  - Removed temporary documentation files (DIALOG_AUTO_RESIZE.md, SEARCH_FUNCTIONALITY.md)
  - Deleted test files and development scripts (test.py)
  - Streamlined docs directory to essential files only
  - Cleaned up build artifacts and temporary files
- **Code Organization**: Improved code maintainability and structure
  - Consolidated connection management logic
  - Enhanced error handling patterns
  - Simplified database switching workflow

### 📚 Documentation
- **Updated README**: Comprehensive update to v1.0.4 with new features
  - Added auto-reconnection feature documentation
  - Enhanced troubleshooting section with reconnection guidance
  - Updated feature descriptions with latest capabilities
  - Improved installation and usage instructions
- **Version History**: Updated changelog with detailed v1.0.4 improvements

### 🏗️ Architecture
- **Connection Management**: Enhanced Redis connection architecture
  - Improved connection pool handling for database operations
  - Added dedicated database client creation methods
  - Enhanced connection state validation and recovery
- **Error Handling**: Systematic error handling and recovery patterns
  - Connection error detection and classification
  - Automatic retry mechanisms with user feedback
  - Graceful degradation and recovery strategies

## [1.0.3] - 2024-12-30

### ✨ Added
- **True Auto-Resize Dialogs**: Implemented SimpleDialog architecture for true auto-resize functionality
  - Text areas now truly adapt to window size changes in real-time
  - No more fixed height constraints - text areas expand/contract with window
  - Proper grid weight configuration ensures optimal space utilization
- **Migrated Edit Dialogs**: All main editing dialogs now use SimpleDialog architecture
  - HashEditDialog: ✅ Migrated with full auto-resize
  - SetEditDialog: ✅ Migrated with full auto-resize  
  - ListEditDialog: ✅ Migrated with full auto-resize
  - ZSetEditDialog: ✅ Migrated with full auto-resize
- **Enhanced Search Integration**: Preserved ⌘F search functionality in all migrated dialogs
- **Improved Default Sizes**: Adjusted dialog default window sizes for better user experience
  - SetEditDialog: 600x400 → 800x500
  - ListEditDialog: 600x400 → 800x500
  - ZSetEditDialog: 600x500 → 800x500

### 🏗️ Architecture
- **SimpleDialog Class**: New dialog base class using pure grid layout without Canvas scrolling
  - Three-tier layout structure (fixed + expandable + fixed sections)
  - Direct grid layout management for better responsiveness
  - Simplified event handling and size calculations
- **Layout Management**: Proper grid weight configuration for true auto-resize
  - Fixed sections: `weight=0` (headers, buttons)
  - Expandable sections: `weight=1` (text areas)
  - Consistent sticky="nsew" for proper expansion

### 🎨 Enhanced
- **User Experience**: Much better utilization of screen real estate
  - Text areas automatically expand to fill available window space
  - Resizing dialog windows immediately adjusts text area size
  - Consistent auto-resize behavior across all migrated dialogs
- **Performance**: Eliminated complex Canvas+scrolling framework interference
- **Maintainability**: Cleaner, more maintainable dialog code structure

### 🧹 Cleaned
- **Project Structure**: Removed development process documentation files
  - Deleted temporary development docs (ADD_ITEM_IMPROVEMENTS.md, etc.)
  - Removed build artifacts (RedisM.dmg, create_icon.py)
  - Cleaned up system files (.DS_Store)
  - Removed PROJECT_SUMMARY.md (content integrated into README)
- **Documentation**: Streamlined docs directory to essential files only

### 📚 Documentation
- **Updated README**: Comprehensive update to v1.0.3 with new features
- **Architecture Documentation**: Added SimpleDialog architecture details
- **User Guide**: Enhanced with auto-resize functionality descriptions

## [1.0.2] - 2024-12-29

### 🆕 Added
- **⌘F Search Functionality**: Implemented comprehensive search functionality for all text display windows
  - String value display window now supports ⌘F search with real-time highlighting
  - All dialog text areas (Hash, List, Set, ZSet editing and creation) support ⌘F search
  - Search dialog with Find Next/Previous navigation and status display
  - Case-insensitive search with automatic wrapping
  - Yellow highlighting of search results with auto-scroll to matches
- **Auto-Resize Text Areas**: Dialog text areas now automatically fill the window and adapt when manually resized
- **Search UI Components**: Added search buttons and visual feedback for better user experience

### 🔧 Enhanced
- **SearchMixin Class**: Created reusable search functionality mixin for text widgets
- **BaseDialog Improvements**: Enhanced with auto-resize text creation and search capabilities
- **Dialog Responsiveness**: All dialog text areas now properly resize with window changes
- **User Experience**: Consistent search experience across all text editing interfaces
- **Auto-Adaptive Text Areas**: Text areas in editing dialogs now automatically adapt to window height
  - Removed fixed height constraints from text components
  - Text areas now fill available space and resize with window
  - Improved space utilization for better editing experience
  - More reasonable minimum window size limits (400x300 minimum)

### 🐛 Fixed
- **Add New Key Functionality**: Fixed Add New Key button not working after moving from right panel to left panel
- **Method Access Path**: Corrected left panel's _add_new_key method to access right_panel.key_manager instead of key_manager
- **Duplicate Method Definition**: Removed duplicate _add_new_key method definition in key_manager.py that was causing the first empty method to override the functional one
- **Text Area Auto-Resize (Root Cause Solution)**: Identified and solved the root cause of text area auto-resize issues
  - **Root Cause**: BaseDialog's Canvas+scrolling framework interferes with tkinter's layout managers
  - **Solution**: Created SimpleDialog class using pure grid layout without Canvas scrolling
  - **Implementation**: HashEditDialog now uses SimpleDialog for true auto-resize functionality
  - **Architecture**: Three-tier layout (fixed sections + expandable section) with proper grid weights
  - **Result**: Text areas now truly adapt to window size changes using tkinter's native layout management

### 🔧 Optimized
- **Project Structure**: Cleaned up project by removing unused temporary files:
  - test_add_key.py
  - test_functionality.py
  - CLEANUP_SUMMARY.md
  - PROJECT_STATUS.md
  - STRUCTURE.md
  - icon_placeholder.txt
- **Code Organization**: Improved code maintainability and removed redundant files

### 📚 Documentation
- **Complete README Rewrite**: Completely rewrote README.md with comprehensive documentation
- **Feature Overview**: Added detailed feature descriptions with emojis and clear sections
- **Installation Guide**: Provided step-by-step installation and setup instructions
- **Usage Guide**: Added comprehensive usage guide with screenshots and examples
- **Troubleshooting**: Added troubleshooting section for common issues
- **Contributing Guide**: Added contribution guidelines and development setup
- **Project Structure**: Updated project structure documentation

### ✨ Enhanced
- **Add New Key Feature**: Ensured complete support for all Redis data types (String, Hash, List, Set, ZSet)
- **Advanced Features**: Confirmed TTL setting, key existence checking, and input validation work properly
- **User Experience**: Optimized UI workflow and interaction patterns

## [1.0.1] - 2024-12-28

### ✨ Added
- **Complete Add New Key Feature**: Implemented comprehensive key creation for all Redis data types
- **New Dialog Classes**: Added AddListDialog, AddSetDialog, AddZSetDialog for specific data types
- **AddNewKeyDialog**: Created unified dialog supporting multi-type key creation with TTL settings
- **UI Repositioning**: Moved Add New Key button from right panel to left panel for better UX

### 🐛 Fixed
- **Add Item Buttons**: Fixed non-functional Add Item buttons for List and Set data types
- **Data Type Operations**: Resolved issues with adding and editing various data types

### 📖 Documentation
- **Feature Documentation**: Added ADD_ITEM_IMPROVEMENTS.md with detailed feature explanations
- **Usage Instructions**: Updated user guides and operation instructions

## [1.0.0] - 2024-12-27

### 🎉 Initial Release
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
- **Modular Design**: Well-organized codebase with clear separation of concerns
- **Configuration Management**: Centralized config in `src/config.py`
- **Build Automation**: Streamlined build process with `build_python.sh`
- **UI Components**: Separate modules for different UI panels and dialogs

### Project Evolution
- **v1.0.0**: Initial monolithic design with single file application
- **v1.0.1**: Modular refactoring with separate UI components and dialogs
- **v1.0.2**: Bug fixes and documentation improvements

### Future Roadmap
- Multi-platform support (Windows, Linux)
- Plugin system for custom data types
- Advanced query builder
- Data export/import functionality
- Performance monitoring and analytics
- Dark mode support
- Internationalization (i18n)