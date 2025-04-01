/**
 * Apeko Admin Dashboard JavaScript
 */

// Track page views
function trackPageView(page) {
    const sessionId = localStorage.getItem('apeko_session_id') || generateSessionId();
    
    // Store session ID
    if (!localStorage.getItem('apeko_session_id')) {
        localStorage.setItem('apeko_session_id', sessionId);
    }
    
    // Track page view
    fetch('/api/v1/website/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            page: page,
            session_id: sessionId,
            time_spent: 0
        })
    }).catch(error => console.error('Error tracking page view:', error));
    
    // Start timer for time spent
    window.pageLoadTime = new Date();
    
    // Track time spent when leaving page
    window.addEventListener('beforeunload', function() {
        const timeSpent = Math.round((new Date() - window.pageLoadTime) / 1000);
        
        // Use sendBeacon for more reliable tracking on page exit
        navigator.sendBeacon('/api/v1/website/track', JSON.stringify({
            page: page,
            session_id: sessionId,
            time_spent: timeSpent
        }));
    });
}

// Generate a random session ID
function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// File Explorer Functions
function navigateToFolder(path) {
    fetch(`/api/v1/admin/files?path=${encodeURIComponent(path)}`)
        .then(response => response.json())
        .then(data => {
            updateFileExplorer(data);
        })
        .catch(error => console.error('Error navigating to folder:', error));
}

function updateFileExplorer(data) {
    const fileList = document.getElementById('file-list');
    const currentPath = document.getElementById('current-path');
    
    if (!fileList || !currentPath) return;
    
    // Update current path
    currentPath.textContent = data.current_path || '/';
    currentPath.dataset.path = data.current_path || '';
    
    // Clear file list
    fileList.innerHTML = '';
    
    // Add parent directory if not at root
    if (data.current_path && data.current_path !== '') {
        const parentPath = data.current_path.split('/').slice(0, -1).join('/');
        const parentItem = createFileItem({
            name: '..',
            path: parentPath,
            type: 'folder',
            icon: 'fa-folder',
            icon_class: 'folder'
        }, true);
        fileList.appendChild(parentItem);
    }
    
    // Add files and folders
    data.files.forEach(file => {
        const fileItem = createFileItem(file);
        fileList.appendChild(fileItem);
    });
}

function createFileItem(file, isParent = false) {
    const item = document.createElement('div');
    item.className = `file-item ${file.type} ${isParent ? 'parent' : ''}`;
    
    const icon = document.createElement('i');
    icon.className = `fas ${file.icon}`;
    
    const name = document.createElement('span');
    name.className = 'file-name';
    name.textContent = file.name;
    
    item.appendChild(icon);
    item.appendChild(name);
    
    // Add size and modified date for files
    if (file.type === 'file' && !isParent) {
        const details = document.createElement('div');
        details.className = 'file-details';
        
        const size = document.createElement('span');
        size.className = 'file-size';
        size.textContent = file.size;
        
        const modified = document.createElement('span');
        modified.className = 'file-modified';
        modified.textContent = file.modified;
        
        details.appendChild(size);
        details.appendChild(modified);
        item.appendChild(details);
        
        // Add actions for files
        const actions = document.createElement('div');
        actions.className = 'file-actions';
        
        // View button
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-sm btn-secondary';
        viewBtn.innerHTML = '<i class="fas fa-eye"></i>';
        viewBtn.title = 'View';
        viewBtn.onclick = (e) => {
            e.stopPropagation();
            viewFile(file.path);
        };
        
        // Download button
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'btn btn-sm btn-secondary';
        downloadBtn.innerHTML = '<i class="fas fa-download"></i>';
        downloadBtn.title = 'Download';
        downloadBtn.onclick = (e) => {
            e.stopPropagation();
            downloadFile(file.path);
        };
        
        // Add to RAG button (if applicable)
        if (file.can_add_to_rag) {
            const ragBtn = document.createElement('button');
            ragBtn.className = 'btn btn-sm btn-primary';
            ragBtn.innerHTML = '<i class="fas fa-database"></i>';
            ragBtn.title = 'Add to RAG Database';
            ragBtn.onclick = (e) => {
                e.stopPropagation();
                addToRag(file.path);
            };
            actions.appendChild(ragBtn);
        }
        
        actions.appendChild(viewBtn);
        actions.appendChild(downloadBtn);
        item.appendChild(actions);
    }
    
    // Add click event for navigation (folders) or viewing (files)
    item.addEventListener('click', () => {
        if (file.type === 'folder') {
            navigateToFolder(file.path);
        } else {
            viewFile(file.path);
        }
    });
    
    return item;
}

function viewFile(path) {
    fetch(`/api/v1/admin/files/view?path=${encodeURIComponent(path)}`)
        .then(response => response.json())
        .then(data => {
            showFileViewer(data);
        })
        .catch(error => console.error('Error viewing file:', error));
}

function downloadFile(path) {
    window.location.href = `/api/v1/admin/files/download?path=${encodeURIComponent(path)}`;
}

function addToRag(path) {
    // Show modal to select document type
    const modal = document.getElementById('add-to-rag-modal');
    const form = document.getElementById('add-to-rag-form');
    
    if (!modal || !form) return;
    
    // Set file path in form
    const pathInput = form.querySelector('input[name="file_path"]');
    if (pathInput) pathInput.value = path;
    
    // Show modal
    modal.style.display = 'flex';
}

function showFileViewer(data) {
    const viewer = document.getElementById('file-viewer');
    const fileContent = document.getElementById('file-content');
    const fileName = document.getElementById('file-name');
    
    if (!viewer || !fileContent || !fileName) return;
    
    // Set file name
    fileName.textContent = data.name;
    
    // Set file content
    fileContent.textContent = data.content;
    
    // Show viewer
    viewer.style.display = 'block';
}

function closeFileViewer() {
    const viewer = document.getElementById('file-viewer');
    if (viewer) viewer.style.display = 'none';
}

// RAG Database Functions
function loadRagStats() {
    fetch('/api/v1/admin/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            updateRagStats(data.rag_stats);
        })
        .catch(error => console.error('Error loading RAG stats:', error));
}

function updateRagStats(stats) {
    // Update document count
    const docCount = document.getElementById('rag-doc-count');
    if (docCount) docCount.textContent = stats.total_documents;
    
    // Update chunk count
    const chunkCount = document.getElementById('rag-chunk-count');
    if (chunkCount) chunkCount.textContent = stats.total_chunks;
    
    // Update query count
    const queryCount = document.getElementById('rag-query-count');
    if (queryCount) queryCount.textContent = stats.total_queries;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Track page view
    const currentPage = window.location.pathname.replace(/^\//, '').replace(/\/$/, '') || 'home';
    trackPageView(currentPage);
    
    // Initialize file explorer if on file explorer page
    const fileExplorer = document.getElementById('file-explorer');
    if (fileExplorer) {
        navigateToFolder('');
    }
    
    // Initialize RAG stats if on dashboard
    const ragStats = document.getElementById('rag-stats');
    if (ragStats) {
        loadRagStats();
    }
});
