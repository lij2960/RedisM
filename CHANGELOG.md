# Changelog

All notable changes to RedisM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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